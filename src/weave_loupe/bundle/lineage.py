"""Explicit compilation-stage lineage for compiler-evidence bundles."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Literal

from weave_loupe.bundle.model import Bundle, BundleError

EvidenceLevel = Literal["lightweight", "standard", "full"]
StageStatus = Literal[
    "present",
    "partial",
    "failed",
    "missing",
    "unavailable",
]

STAGE_IDS: tuple[str, ...] = (
    "source",
    "wir",
    "llvm",
    "optimized_llvm",
    "native",
    "runtime",
)
STAGE_PRODUCED_FROM: dict[str, tuple[str, ...]] = {
    "source": (),
    "wir": ("source",),
    "llvm": ("wir",),
    "optimized_llvm": ("llvm",),
    "native": ("optimized_llvm",),
    "runtime": ("native",),
}
STAGE_ARTIFACTS: dict[str, tuple[str, ...]] = {
    "source": (),
    "wir": ("wir",),
    "llvm": ("llvm",),
    "optimized_llvm": ("optimized_llvm",),
    "native": ("assembly", "disassembly", "executable"),
    "runtime": (),
}
NATIVE_PRESENT_ARTIFACTS: tuple[str, ...] = ("assembly", "disassembly")
SUPPORTING_ARTIFACTS: tuple[str, ...] = (
    "compiler_capabilities",
    "diagnostics",
    "trace",
    "optimization_record",
    "build_manifest",
)
EVIDENCE_LEVELS: tuple[EvidenceLevel, ...] = ("lightweight", "standard", "full")
_PHASE_FAILED_STAGE: dict[str, str] = {
    "frontend": "wir",
    "backend": "llvm",
    "optimize": "optimized_llvm",
    "optimization-record": "optimized_llvm",
    "assembly": "native",
    "codegen": "native",
    "link": "native",
    "disassemble": "native",
    "publish": "native",
}
_EXPECTED_STAGES: dict[EvidenceLevel, tuple[str, ...]] = {
    "lightweight": ("source",),
    "standard": ("source", "wir", "llvm", "optimized_llvm", "native"),
    "full": ("source", "wir", "llvm", "optimized_llvm", "native"),
}


def normalize_evidence_level(value: str) -> EvidenceLevel:
    """Return a validated capture/retention level."""
    levels: dict[str, EvidenceLevel] = {
        "lightweight": "lightweight",
        "standard": "standard",
        "full": "full",
    }
    try:
        return levels[value]
    except KeyError:
        raise BundleError(
            f"unknown evidence level {value!r}; expected one of {EVIDENCE_LEVELS}"
        ) from None


def artifact_identities(manifest: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    """Return sha256/size identity for every declared artifact."""
    raw = manifest.get("artifacts")
    if not isinstance(raw, Mapping):
        return {}
    result: dict[str, dict[str, Any]] = {}
    for name, item in raw.items():
        if not isinstance(name, str) or not isinstance(item, Mapping):
            continue
        digest, size = item.get("sha256"), item.get("size")
        if isinstance(digest, str) and isinstance(size, int):
            result[name] = {"sha256": digest, "size": size}
    return result


def source_identities(manifest: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    """Return ordered source content identities."""
    raw = manifest.get("sources")
    if not isinstance(raw, list):
        return ()
    result: list[dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, Mapping):
            continue
        digest, size = item.get("sha256"), item.get("size")
        if isinstance(digest, str) and isinstance(size, int):
            result.append(
                {
                    "index": item.get("index"),
                    "input": item.get("input"),
                    "sha256": digest,
                    "size": size,
                }
            )
    return tuple(result)


def compilation_record(
    *,
    manifest_artifacts: Mapping[str, Mapping[str, Any]],
    sources: Sequence[Mapping[str, Any]],
    exit_code: int,
    evidence_level: EvidenceLevel,
    include_executable: bool,
    identity: Mapping[str, Any],
    build_manifest: Mapping[str, Any] | None = None,
    declared: bool = True,
) -> dict[str, Any]:
    """Build the portable compilation identity and declared stage lineage."""
    present = {name for name, item in manifest_artifacts.items() if item}
    failed_stage = _failed_stage(exit_code, build_manifest)
    stages = [
        _stage_entry(
            stage_id,
            present_artifacts=present,
            sources=sources,
            failed_stage=failed_stage,
            exit_code=exit_code,
            identities=manifest_artifacts,
        )
        for stage_id in STAGE_IDS
    ]
    target = identity.get("target")
    if target is None and isinstance(build_manifest, Mapping):
        raw_target = build_manifest.get("target")
        target = raw_target if isinstance(raw_target, str) else None
    identity_out = dict(identity)
    if isinstance(target, str) and target:
        identity_out["target"] = target
    return {
        "identity": identity_out,
        "retention": {
            "level": evidence_level,
            "include_executable": include_executable,
        },
        "lineage": {
            "declared": declared,
            "stages": stages,
        },
    }


def lineage_for_bundle(bundle: Bundle) -> dict[str, Any]:
    """Return declared lineage, or an inferred historical reconstruction."""
    raw = bundle.manifest.get("compilation")
    if isinstance(raw, Mapping):
        lineage = raw.get("lineage")
        if isinstance(lineage, Mapping) and isinstance(lineage.get("stages"), list):
            stages = [
                dict(item) for item in lineage["stages"] if isinstance(item, Mapping)
            ]
            return {
                "declared": lineage.get("declared") is not False,
                "inferred": False,
                "stages": stages,
            }
    build_manifest = bundle.artifact_json("build_manifest")
    return infer_lineage(
        bundle.manifest,
        build_manifest=build_manifest if isinstance(build_manifest, Mapping) else None,
    )


def infer_lineage(
    manifest: Mapping[str, Any],
    *,
    build_manifest: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Reconstruct stage relationships from known artifact names.

    Historical bundles did not declare lineage. The reconstruction is marked
    inferred so later comparison does not treat filenames as declared identity.
    """
    artifacts = artifact_identities(manifest)
    sources = source_identities(manifest)
    record = compilation_record(
        manifest_artifacts=artifacts,
        sources=sources,
        exit_code=_exit_code(manifest) if _exit_code(manifest) != -1 else 0,
        evidence_level="standard",
        include_executable="executable" in artifacts,
        identity={},
        build_manifest=build_manifest,
        declared=False,
    )
    return {
        "declared": False,
        "inferred": True,
        "stages": record["lineage"]["stages"],
    }


def completeness_for_bundle(bundle: Bundle) -> dict[str, Any]:
    """Describe missing, failed, and unavailable stages fail-closed."""
    compilation = bundle.manifest.get("compilation")
    level: EvidenceLevel = "standard"
    include_executable = bundle.artifact_path("executable") is not None
    if isinstance(compilation, Mapping):
        retention = compilation.get("retention")
        if isinstance(retention, Mapping):
            raw_level = retention.get("level")
            if (
                raw_level == "lightweight"
                or raw_level == "standard"
                or raw_level == "full"
            ):
                level = raw_level
            include_executable = retention.get("include_executable") is True
    lineage = lineage_for_bundle(bundle)
    return completeness_from_lineage(
        lineage,
        evidence_level=level,
        include_executable=include_executable,
        exit_code=_exit_code(bundle.manifest),
    )


def completeness_from_lineage(
    lineage: Mapping[str, Any],
    *,
    evidence_level: EvidenceLevel,
    include_executable: bool,
    exit_code: int,
) -> dict[str, Any]:
    """Return fail-closed completeness for one lineage document."""
    stages = {
        str(item.get("id")): item
        for item in lineage.get("stages", [])
        if isinstance(item, Mapping)
    }
    expected = list(_EXPECTED_STAGES[evidence_level])
    if include_executable and "native" not in expected:
        expected.append("native")
    gaps: list[dict[str, str]] = []
    for stage_id in expected:
        item = stages.get(stage_id)
        status = str(item.get("status")) if isinstance(item, Mapping) else "missing"
        names = _stage_artifacts(item) if isinstance(item, Mapping) else set()
        if (
            include_executable
            and stage_id == "native"
            and "executable" not in names
            and exit_code == 0
        ):
            gaps.append(
                {
                    "stage": stage_id,
                    "status": "missing",
                    "reason": "full retention requested the native executable",
                }
            )
            continue
        if status == "present":
            continue
        if status == "partial" and stage_id == "native" and not include_executable:
            continue
        if exit_code != 0 and status in {"unavailable", "failed"}:
            continue
        gaps.append(
            {
                "stage": stage_id,
                "status": status,
                "reason": _gap_reason(stage_id, status, exit_code),
            }
        )
    runtime = stages.get("runtime")
    runtime_status = (
        str(runtime.get("status")) if isinstance(runtime, Mapping) else "unavailable"
    )
    return {
        "complete": not gaps,
        "evidence_level": evidence_level,
        "gaps": gaps,
        "runtime": runtime_status,
        "inferred_lineage": lineage.get("inferred") is True,
    }


def _stage_entry(
    stage_id: str,
    *,
    present_artifacts: set[str],
    sources: Sequence[Mapping[str, Any]],
    failed_stage: str | None,
    exit_code: int,
    identities: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    produced_from = list(STAGE_PRODUCED_FROM[stage_id])
    names = [name for name in STAGE_ARTIFACTS[stage_id] if name in present_artifacts]
    hashes = {
        name: identities[name]["sha256"]
        for name in names
        if isinstance(identities.get(name), Mapping)
        and isinstance(identities[name].get("sha256"), str)
    }
    status = _status_for_stage(
        stage_id,
        present_artifacts=present_artifacts,
        sources=sources,
        failed_stage=failed_stage,
        exit_code=exit_code,
    )
    entry: dict[str, Any] = {
        "id": stage_id,
        "status": status,
        "produced_from": produced_from,
        "artifacts": names,
        "artifact_sha256": hashes,
    }
    if stage_id == "source":
        entry["source_sha256"] = [
            item["sha256"] for item in sources if "sha256" in item
        ]
    return entry


def _status_for_stage(
    stage_id: str,
    *,
    present_artifacts: set[str],
    sources: Sequence[Mapping[str, Any]],
    failed_stage: str | None,
    exit_code: int,
) -> StageStatus:
    if stage_id == "source":
        return "present" if sources else "missing"
    if stage_id == "runtime":
        return "unavailable"
    if stage_id == "native":
        have = [name for name in NATIVE_PRESENT_ARTIFACTS if name in present_artifacts]
        extra = "executable" in present_artifacts
        if len(have) == len(NATIVE_PRESENT_ARTIFACTS):
            return "present"
        if have or extra:
            if failed_stage == "native":
                return "failed"
            return "partial"
        if failed_stage == "native":
            return "failed"
        if failed_stage is not None and _stage_index(failed_stage) < _stage_index(
            "native"
        ):
            return "unavailable"
        if exit_code != 0:
            return "unavailable"
        return "missing"
    required = STAGE_ARTIFACTS[stage_id]
    if any(name in present_artifacts for name in required):
        return "present"
    if failed_stage == stage_id:
        return "failed"
    if failed_stage is not None and _stage_index(failed_stage) < _stage_index(stage_id):
        return "unavailable"
    if exit_code != 0:
        return "unavailable"
    return "missing"


def _failed_stage(
    exit_code: int, build_manifest: Mapping[str, Any] | None
) -> str | None:
    if exit_code == 0:
        return None
    if not isinstance(build_manifest, Mapping):
        return None
    phase = build_manifest.get("phase")
    if isinstance(phase, str) and phase in _PHASE_FAILED_STAGE:
        return _PHASE_FAILED_STAGE[phase]
    return None


def _stage_index(stage_id: str) -> int:
    return STAGE_IDS.index(stage_id)


def _stage_artifacts(item: Mapping[str, Any]) -> set[str]:
    raw = item.get("artifacts")
    if not isinstance(raw, list):
        return set()
    return {name for name in raw if isinstance(name, str)}


def _gap_reason(stage_id: str, status: str, exit_code: int) -> str:
    if status == "failed":
        return f"{stage_id} failed during compilation"
    if status == "unavailable":
        if exit_code != 0:
            return f"{stage_id} was not produced because an earlier stage failed"
        return f"{stage_id} was not retained"
    if status == "partial":
        return f"{stage_id} is only partially retained"
    return f"{stage_id} artifact is missing"


def _exit_code(manifest: Mapping[str, Any]) -> int:
    compiler = manifest.get("compiler")
    if isinstance(compiler, Mapping):
        exit_code = compiler.get("exit_code")
        if isinstance(exit_code, int) and not isinstance(exit_code, bool):
            return exit_code
    return -1


def _load_build_manifest_from_mapping(
    manifest: Mapping[str, Any],
) -> Mapping[str, Any] | None:
    return None


def validate_compilation(
    manifest: Mapping[str, Any],
) -> tuple[dict[str, str], ...]:
    """Return lineage consistency problems for a declared compilation record."""
    raw = manifest.get("compilation")
    if raw is None:
        return ()
    problems: list[dict[str, str]] = []
    if not isinstance(raw, Mapping):
        return (
            {
                "code": "compilation-not-object",
                "location": "compilation",
                "message": "compilation metadata must be an object",
            },
        )
    artifacts = artifact_identities(manifest)
    identity = raw.get("identity")
    if identity is not None and not isinstance(identity, Mapping):
        problems.append(
            {
                "code": "compilation-identity-invalid",
                "location": "compilation.identity",
                "message": "compilation identity must be an object",
            }
        )
    elif isinstance(identity, Mapping):
        digest = identity.get("capability_registry_sha256")
        capability = artifacts.get("compiler_capabilities")
        if (
            isinstance(digest, str)
            and capability is not None
            and capability.get("sha256") != digest
        ):
            problems.append(
                {
                    "code": "capability-identity-mismatch",
                    "location": "compilation.identity.capability_registry_sha256",
                    "message": (
                        "capability registry hash does not match the retained "
                        "compiler_capabilities artifact"
                    ),
                }
            )
        compiler_digest = identity.get("compiler_sha256")
        if compiler_digest is not None and not (
            isinstance(compiler_digest, str) and len(compiler_digest) == 64
        ):
            problems.append(
                {
                    "code": "compiler-sha256-invalid",
                    "location": "compilation.identity.compiler_sha256",
                    "message": "compiler sha256 must be a 64-character hex digest",
                }
            )
    lineage = raw.get("lineage")
    if not isinstance(lineage, Mapping):
        problems.append(
            {
                "code": "lineage-not-object",
                "location": "compilation.lineage",
                "message": "compilation lineage must be an object",
            }
        )
        return tuple(problems)
    stages = lineage.get("stages")
    if not isinstance(stages, list):
        problems.append(
            {
                "code": "lineage-stages-invalid",
                "location": "compilation.lineage.stages",
                "message": "lineage stages must be a list",
            }
        )
        return tuple(problems)
    seen: set[str] = set()
    for index, item in enumerate(stages):
        location = f"compilation.lineage.stages[{index}]"
        if not isinstance(item, Mapping):
            problems.append(
                {
                    "code": "stage-not-object",
                    "location": location,
                    "message": "lineage stage must be an object",
                }
            )
            continue
        stage_id = item.get("id")
        if stage_id not in STAGE_IDS:
            problems.append(
                {
                    "code": "stage-id-invalid",
                    "location": f"{location}.id",
                    "message": f"stage id must be one of {STAGE_IDS}",
                }
            )
            continue
        if stage_id in seen:
            problems.append(
                {
                    "code": "stage-duplicate",
                    "location": f"{location}.id",
                    "message": f"stage {stage_id!r} is repeated",
                }
            )
        seen.add(str(stage_id))
        produced = item.get("produced_from")
        expected_from = STAGE_PRODUCED_FROM[str(stage_id)]
        if produced != list(expected_from):
            problems.append(
                {
                    "code": "stage-produced-from-invalid",
                    "location": f"{location}.produced_from",
                    "message": (
                        f"stage {stage_id} must be produced from {list(expected_from)}"
                    ),
                }
            )
        names = item.get("artifacts")
        if not isinstance(names, list) or not all(
            isinstance(name, str) for name in names
        ):
            problems.append(
                {
                    "code": "stage-artifacts-invalid",
                    "location": f"{location}.artifacts",
                    "message": "stage artifacts must be a list of names",
                }
            )
            continue
        for name in names:
            if name not in artifacts and name not in STAGE_ARTIFACTS[str(stage_id)]:
                problems.append(
                    {
                        "code": "stage-artifact-unknown",
                        "location": f"{location}.artifacts",
                        "message": f"stage references unknown artifact {name!r}",
                    }
                )
            elif name not in artifacts:
                problems.append(
                    {
                        "code": "stage-artifact-missing",
                        "location": f"{location}.artifacts",
                        "message": (
                            f"stage {stage_id} declares artifact {name!r} "
                            "that is not in the bundle"
                        ),
                    }
                )
            hashes = item.get("artifact_sha256")
            if isinstance(hashes, Mapping) and name in artifacts:
                declared = hashes.get(name)
                actual = artifacts[name]["sha256"]
                if declared != actual:
                    problems.append(
                        {
                            "code": "stage-artifact-hash-mismatch",
                            "location": f"{location}.artifact_sha256.{name}",
                            "message": (
                                "lineage hash does not match the retained artifact"
                            ),
                        }
                    )
    return tuple(problems)
