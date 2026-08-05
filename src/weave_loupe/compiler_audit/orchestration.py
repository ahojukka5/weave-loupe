"""Composition of compiler audit acquisition, comparison, policy, and reporting."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from .acquisition import capture_evidence_pair, resolve_compiler_input
from .comparison import compare_compiler_evidence
from .model import CompilerAuditError, ReviewCallback
from .policy import evaluate_compiler_audit_policy, load_compiler_audit_policy
from .reporting import build_compiler_audit_report


def audit_compilers(
    *,
    sources: Sequence[Path],
    baseline_weavec: Path,
    candidate_weavec: Path,
    work_dir: Path,
    policy_path: Path | None = None,
    compiler_timeout_seconds: float | None = None,
    compiler_output_bytes: int | None = None,
    runtime_timeout_seconds: float | None = None,
    runtime_output_bytes: int | None = None,
    reviewer: ReviewCallback | None = None,
) -> dict[str, Any]:
    """Compile identical inputs twice and return a sealed regression verdict."""
    ordered_sources = [Path(source) for source in sources]
    if not ordered_sources:
        raise CompilerAuditError("at least one source is required")
    baseline_binary = resolve_compiler_input(baseline_weavec)
    candidate_binary = resolve_compiler_input(candidate_weavec)
    policy = load_compiler_audit_policy(policy_path)
    baseline, candidate = capture_evidence_pair(
        sources=ordered_sources,
        baseline_weavec=baseline_binary,
        candidate_weavec=candidate_binary,
        work_dir=work_dir,
        compiler_timeout_seconds=compiler_timeout_seconds,
        compiler_output_bytes=compiler_output_bytes,
        runtime_timeout_seconds=runtime_timeout_seconds,
        runtime_output_bytes=runtime_output_bytes,
    )
    comparison = compare_compiler_evidence(baseline, candidate, policy)
    failures = evaluate_compiler_audit_policy(
        baseline=baseline.result,
        candidate=candidate.result,
        policy=policy,
        comparison=comparison,
    )
    return build_compiler_audit_report(
        sources=ordered_sources,
        baseline=baseline,
        candidate=candidate,
        policy=policy,
        comparison=comparison,
        failures=failures,
        reviewer=reviewer,
    )
