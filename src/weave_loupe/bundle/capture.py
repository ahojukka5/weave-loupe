"""Live compiler capture for portable evidence bundles."""

from __future__ import annotations

import json
import shutil
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from weave_loupe.compiler.capabilities import (
    CompilerCapabilityError,
    validate_capability_document,
)
from weave_loupe.path_identity import (
    PORTABLE_PATH_FORMAT,
    PathIdentityError,
    plan_public_paths,
)
from weave_loupe.weavec import (
    BuildRequest,
    EvidenceLevel,
    WeavecError,
    normalize_sources,
    run_build,
)

from .identity import compiler_content_identity
from .lineage import (
    artifact_identities,
    compilation_record,
    normalize_evidence_level,
    source_identities,
)
from .model import BundleError
from .publication import file_entry, publish_directory
from .verification import BUNDLE_FORMAT, MANIFEST_NAME, verify_bundle


@dataclass(frozen=True)
class CaptureResult:
    """Result of capturing one compiler invocation."""

    bundle: Path
    compiler_exit_code: int


def capture_bundle(
    *,
    sources: Sequence[Path],
    output: Path,
    weavec: Path | None = None,
    include_executable: bool = False,
    compiler_timeout_seconds: float | None = None,
    compiler_output_bytes: int | None = None,
    audit_root: Path | None = None,
    source_names: Sequence[str] | None = None,
    evidence_level: EvidenceLevel | str = "standard",
) -> CaptureResult:
    """Compile ordered sources and atomically publish a portable evidence bundle."""
    level = normalize_evidence_level(evidence_level)
    keep_executable = include_executable or level == "full"
    try:
        plan = plan_public_paths(
            sources,
            audit_root=audit_root,
            logical_names=source_names,
        )
        normalized = normalize_sources(
            [source.execution_path for source in plan.sources]
        )
    except (PathIdentityError, WeavecError) as exc:
        raise BundleError(str(exc)) from exc

    destination = output.expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    work = Path(
        tempfile.mkdtemp(prefix=f".{destination.name}.", dir=destination.parent)
    )
    try:
        source_dir = work / "sources"
        artifact_dir = work / "artifacts"
        log_dir = work / "logs"
        source_dir.mkdir()
        artifact_dir.mkdir()
        log_dir.mkdir()

        source_entries: list[dict[str, Any]] = []
        for index, (source, public) in enumerate(
            zip(normalized, plan.sources, strict=True)
        ):
            target = source_dir / f"{index:03d}-{source.name}"
            shutil.copyfile(source, target)
            source_entries.append(
                file_entry(
                    work,
                    target,
                    extra={
                        "index": index,
                        "input": public.identity,
                        "identity": public.metadata(),
                    },
                )
            )

        request = BuildRequest(
            sources=normalized,
            executable=artifact_dir / "program",
            wir=artifact_dir / "program.wir",
            llvm=artifact_dir / "program.ll",
            optimized_llvm=artifact_dir / "program.optimized.ll",
            assembly=artifact_dir / "program.s",
            disassembly=artifact_dir / "program.disasm",
            optimization_record=artifact_dir / "program.opt.yaml",
            diagnostics=artifact_dir / "diagnostics.json",
            trace=artifact_dir / "trace.json",
            build_manifest=artifact_dir / "build-manifest.json",
        )
        result = run_build(
            request,
            weavec=weavec,
            timeout_seconds=compiler_timeout_seconds,
            output_bytes=compiler_output_bytes,
            evidence_level=level,
        )
        capabilities_path = artifact_dir / "compiler-capabilities.json"
        capabilities_path.write_bytes(result.capabilities.raw_bytes)
        try:
            validate_capability_document(
                json.loads(capabilities_path.read_text(encoding="utf-8"))
            )
        except (json.JSONDecodeError, CompilerCapabilityError) as exc:
            message = f"retained compiler capabilities are invalid: {exc}"
            raise BundleError(message) from exc

        stdout_path = log_dir / "stdout.txt"
        stderr_path = log_dir / "stderr.txt"
        stdout_path.write_text(result.stdout, encoding="utf-8")
        stderr_path.write_text(result.stderr, encoding="utf-8")

        artifact_paths: dict[str, Path] = {
            "compiler_capabilities": capabilities_path,
            "wir": request.wir,
            "llvm": request.llvm,
            "optimized_llvm": request.optimized_llvm,
            "assembly": request.assembly,
            "disassembly": request.disassembly,
            "optimization_record": request.optimization_record,
            "diagnostics": request.diagnostics,
            "trace": request.trace,
            "build_manifest": request.build_manifest,
        }
        if keep_executable:
            artifact_paths["executable"] = request.executable
        elif request.executable.exists():
            request.executable.unlink()

        artifacts: dict[str, dict[str, Any]] = {}
        for name, artifact_path in artifact_paths.items():
            if artifact_path.is_file():
                artifacts[name] = file_entry(work, artifact_path)

        build_manifest = None
        manifest_entry = artifacts.get("build_manifest")
        if manifest_entry is not None:
            try:
                build_manifest = json.loads(
                    (work / str(manifest_entry["path"])).read_text(encoding="utf-8")
                )
            except (OSError, json.JSONDecodeError, TypeError):
                build_manifest = None
        if not isinstance(build_manifest, dict):
            build_manifest = None
        capability_digest = artifacts.get("compiler_capabilities", {}).get("sha256")
        target_triple = None
        if isinstance(build_manifest, dict):
            raw_target = build_manifest.get("target")
            target_triple = raw_target if isinstance(raw_target, str) else None
        compilation = compilation_record(
            manifest_artifacts=artifact_identities({"artifacts": artifacts}),
            sources=source_identities({"sources": source_entries}),
            exit_code=result.returncode,
            evidence_level=(
                "full" if keep_executable and level != "lightweight" else level
            ),
            include_executable=keep_executable,
            identity=compiler_content_identity(
                Path(result.command[0]),
                capability_registry_sha256=(
                    capability_digest if isinstance(capability_digest, str) else None
                ),
                target=target_triple,
            ),
            build_manifest=build_manifest,
            declared=True,
        )
        portable_command = _portable_command(source_entries, evidence_level=level)
        manifest: dict[str, Any] = {
            "format": BUNDLE_FORMAT,
            "source_identity": {
                "format": PORTABLE_PATH_FORMAT,
                "root_kind": plan.root_kind,
            },
            "compiler": {
                "binary": Path(result.command[0]).name,
                "command": portable_command,
                "exit_code": result.returncode,
                "execution": result.execution.as_dict(),
            },
            "compilation": compilation,
            "sources": source_entries,
            "artifacts": artifacts,
            "logs": {
                "stdout": file_entry(work, stdout_path),
                "stderr": file_entry(work, stderr_path),
            },
        }
        (work / MANIFEST_NAME).write_text(
            json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        verification = verify_bundle(work)
        if not verification.valid:
            raise BundleError(verification.error_message())

        publish_directory(work, destination)
        return CaptureResult(
            bundle=destination,
            compiler_exit_code=result.returncode,
        )
    except BundleError:
        shutil.rmtree(work, ignore_errors=True)
        raise
    except (OSError, WeavecError, ValueError) as exc:
        shutil.rmtree(work, ignore_errors=True)
        raise BundleError(str(exc)) from exc


def _portable_command(
    source_entries: Sequence[Mapping[str, Any]],
    *,
    evidence_level: EvidenceLevel,
) -> list[str]:
    command = ["weavec", "build"]
    command.extend(str(entry["path"]) for entry in source_entries)
    command.extend(["-o", "artifacts/program"])
    if evidence_level in {"standard", "full"}:
        command.extend(
            [
                "--emit-wir",
                "artifacts/program.wir",
                "--emit-llvm",
                "artifacts/program.ll",
                "--emit-optimized-llvm",
                "artifacts/program.optimized.ll",
                "--emit-assembly",
                "artifacts/program.s",
                "--emit-disassembly",
                "artifacts/program.disasm",
                "--optimization-record",
                "artifacts/program.opt.yaml",
                "-O3",
                "--native",
                "--llvm-provenance",
            ]
        )
    command.extend(
        [
            "--diagnostics-json",
            "artifacts/diagnostics.json",
            "--trace-json",
            "artifacts/trace.json",
            "--manifest-json",
            "artifacts/build-manifest.json",
        ]
    )
    return command
