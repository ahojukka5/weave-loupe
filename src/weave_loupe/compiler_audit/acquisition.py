"""Live acquisition of compiler audit evidence."""

from __future__ import annotations

import shutil
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from weave_loupe.analysis import analyze_bundle
from weave_loupe.auditor_identity import sha256_file
from weave_loupe.bundle import Bundle, BundleError, capture_bundle, load_bundle
from weave_loupe.compiler_version import identify_weavec
from weave_loupe.native_budget import evaluate_native_budget
from weave_loupe.optimized_llvm_budget import evaluate_optimized_llvm_budget
from weave_loupe.runtime_cases import execute_runtime_cases

from .model import CompilerAuditError, CompilerEvidence


def resolve_compiler_input(path: Path) -> Path:
    """Resolve an executable or a repository checkout containing one."""
    resolved = path.expanduser().resolve()
    if resolved.is_file():
        return resolved
    if resolved.is_dir():
        candidates = (resolved / "build" / "weavec", resolved / "weavec")
        for candidate in candidates:
            if candidate.is_file():
                return candidate
        raise CompilerAuditError(
            f"compiler checkout has no built weavec binary: {resolved}; "
            "run its build before auditing"
        )
    raise CompilerAuditError(f"compiler input does not exist: {resolved}")


def capture_evidence_pair(
    *,
    sources: list[Path],
    baseline_weavec: Path,
    candidate_weavec: Path,
    work_dir: Path,
    compiler_timeout_seconds: float | None,
    compiler_output_bytes: int | None,
    runtime_timeout_seconds: float | None,
    runtime_output_bytes: int | None,
) -> tuple[CompilerEvidence, CompilerEvidence]:
    """Capture and derive observations for identical baseline and candidate inputs."""
    baseline_bundle, candidate_bundle = _capture_pair(
        sources=sources,
        baseline_weavec=baseline_weavec,
        candidate_weavec=candidate_weavec,
        work_dir=work_dir,
        compiler_timeout_seconds=compiler_timeout_seconds,
        compiler_output_bytes=compiler_output_bytes,
    )
    return (
        evidence_from_bundle(
            bundle=baseline_bundle,
            compiler=baseline_weavec,
            sources=sources,
            runtime_timeout_seconds=runtime_timeout_seconds,
            runtime_output_bytes=runtime_output_bytes,
        ),
        evidence_from_bundle(
            bundle=candidate_bundle,
            compiler=candidate_weavec,
            sources=sources,
            runtime_timeout_seconds=runtime_timeout_seconds,
            runtime_output_bytes=runtime_output_bytes,
        ),
    )


def evidence_from_bundle(
    *,
    bundle: Bundle,
    compiler: Path,
    sources: list[Path],
    runtime_timeout_seconds: float | None,
    runtime_output_bytes: int | None,
) -> CompilerEvidence:
    """Derive audit observations from one verified compiler evidence bundle."""
    analysis = analyze_bundle(bundle)
    if analysis["compiler_exit_code"] == 0:
        optimized_budget = evaluate_optimized_llvm_budget(
            sources=sources,
            optimized_llvm=bundle.artifact_text("optimized_llvm") or "",
            metrics=analysis.get("optimized_llvm"),
        )
        native_budget = evaluate_native_budget(
            sources=sources,
            native_analysis=analysis.get("native"),
        )
        runtime = execute_runtime_cases(
            bundle=bundle,
            sources=sources,
            runtime_timeout_seconds=runtime_timeout_seconds,
            runtime_output_bytes=runtime_output_bytes,
        )
    else:
        skipped = {
            "configured": None,
            "passed": False,
            "skipped": True,
            "reason": "compiler did not produce a successful executable",
        }
        optimized_budget = dict(skipped)
        native_budget = dict(skipped)
        runtime = dict(skipped)
    result = {
        "compiler": _compiler_identity(compiler),
        "compiler_exit_code": analysis["compiler_exit_code"],
        "analysis": analysis,
        "optimized_llvm_budget": optimized_budget,
        "native_budget": native_budget,
        "runtime": runtime,
        "artifacts": _artifact_identities(bundle),
    }
    return CompilerEvidence(bundle=bundle, result=result)


def _capture_pair(
    *,
    sources: list[Path],
    baseline_weavec: Path,
    candidate_weavec: Path,
    work_dir: Path,
    compiler_timeout_seconds: float | None,
    compiler_output_bytes: int | None,
) -> tuple[Bundle, Bundle]:
    root = work_dir.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    outputs = (root / "baseline.loupe", root / "candidate.loupe")
    for output in outputs:
        _remove_existing(output)
    try:
        baseline = capture_bundle(
            sources=sources,
            output=outputs[0],
            weavec=baseline_weavec,
            include_executable=True,
            compiler_timeout_seconds=compiler_timeout_seconds,
            compiler_output_bytes=compiler_output_bytes,
        )
        candidate = capture_bundle(
            sources=sources,
            output=outputs[1],
            weavec=candidate_weavec,
            include_executable=True,
            compiler_timeout_seconds=compiler_timeout_seconds,
            compiler_output_bytes=compiler_output_bytes,
        )
        return load_bundle(baseline.bundle), load_bundle(candidate.bundle)
    except BundleError as exc:
        raise CompilerAuditError(str(exc)) from exc


def _compiler_identity(binary: Path) -> dict[str, Any]:
    version = identify_weavec(binary)
    return {
        "path": str(binary),
        "sha256": sha256_file(binary),
        "version": version.display,
        "base_version": version.base,
        "git_sha": version.git_sha,
        "development": version.development,
        "version_source": version.source,
    }


def _artifact_identities(bundle: Bundle) -> dict[str, dict[str, Any]]:
    raw = bundle.manifest.get("artifacts")
    if not isinstance(raw, Mapping):
        return {}
    result: dict[str, dict[str, Any]] = {}
    for name, item in sorted(raw.items()):
        if not isinstance(name, str) or not isinstance(item, Mapping):
            continue
        digest, size = item.get("sha256"), item.get("size")
        if isinstance(digest, str) and isinstance(size, int):
            result[name] = {"sha256": digest, "size": size}
    return result


def _remove_existing(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()
