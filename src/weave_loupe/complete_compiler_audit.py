"""Complete baseline-versus-candidate compiler audits."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from weave_loupe.bundle import load_bundle
from weave_loupe.bundle_diffing import compare_bundles
from weave_loupe.compiler_audit import (
    COMPILER_AUDIT_FORMAT,
    COMPILER_AUDIT_POLICY_FORMAT,
    COMPILER_AUDIT_SEAL_FORMAT,
    CompilerAuditError,
    CompilerAuditPolicy,
    MetricDeltaRule,
    ReviewCallback,
    load_compiler_audit_policy,
    resolve_compiler_input,
    seal_compiler_audit,
)
from weave_loupe.compiler_audit import audit_compilers as _audit_without_extensions
from weave_loupe.optimization_remark_policy import (
    base_policy_path,
    evaluate_optimization_remark_policy,
    load_optimization_remark_policy,
)
from weave_loupe.path_identity import (
    canonicalize_compiler_audit,
    plan_public_paths,
)

_WIR_DEFAULT_PATHS = (
    "analysis.wir.metrics.unreachable_blocks",
    "analysis.wir.metrics.unresolved_symbols",
    "analysis.wir.metrics.anonymous_identifiers",
    "analysis.wir.metrics.malformed_provenance",
    "analysis.wir.cross_stage.metrics.missing_definitions",
    "analysis.wir.cross_stage.metrics.unexpected_definitions",
    "analysis.wir.cross_stage.metrics.missing_externs",
    "analysis.wir.cross_stage.metrics.duplicate_llvm_definitions",
    "analysis.wir.cross_stage.metrics.duplicate_llvm_declarations",
)


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
    audit_root: Path | None = None,
    source_names: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Run the established audit and add complete deterministic evidence."""
    plan = plan_public_paths(
        sources,
        audit_root=audit_root,
        logical_names=source_names,
    )
    remark_policy = load_optimization_remark_policy(policy_path)
    core_policy = base_policy_path(
        policy_path,
        work_dir.expanduser().resolve() / "core-policy.json",
    )
    report = _audit_without_extensions(
        sources=sources,
        baseline_weavec=baseline_weavec,
        candidate_weavec=candidate_weavec,
        work_dir=work_dir,
        policy_path=core_policy,
        compiler_timeout_seconds=compiler_timeout_seconds,
        compiler_output_bytes=compiler_output_bytes,
        runtime_timeout_seconds=runtime_timeout_seconds,
        runtime_output_bytes=runtime_output_bytes,
        reviewer=None,
    )
    report.pop("seal", None)
    baseline = _mapping(report.get("baseline"))
    candidate = _mapping(report.get("candidate"))
    comparison = dict(_mapping(report.get("comparison")))
    root = work_dir.expanduser().resolve()
    comparison["bundle_diff"] = compare_bundles(
        load_bundle(root / "baseline.loupe"),
        load_bundle(root / "candidate.loupe"),
        before_context=baseline,
        after_context=candidate,
    )
    report["comparison"] = comparison

    policy = dict(_mapping(report.get("policy")))
    policy["optimization_remarks"] = remark_policy
    report["policy"] = policy

    failures = [dict(item) for item in _mapping_list(report.get("failures"))]
    _append_validity_failures(baseline, candidate, failures)
    _append_default_metric_rules(report, baseline, candidate, failures)
    failures.extend(
        evaluate_optimization_remark_policy(
            remark_policy,
            baseline,
            candidate,
            _mapping(comparison.get("bundle_diff")),
        )
    )
    report["failures"] = failures
    infrastructure = any(item.get("category") == "infrastructure" for item in failures)
    report["passed"] = not failures
    report["status"] = (
        "infrastructure-failure"
        if infrastructure
        else "regression"
        if failures
        else "pass"
    )
    report["review"] = None
    report = canonicalize_compiler_audit(report, plan=plan)
    if reviewer is not None:
        review = reviewer(report)
        if not isinstance(review, Mapping):
            raise CompilerAuditError("compiler audit reviewer must return a mapping")
        report["review"] = dict(review)
    return seal_compiler_audit(report)


def _append_validity_failures(
    baseline: Mapping[str, Any],
    candidate: Mapping[str, Any],
    failures: list[dict[str, Any]],
) -> None:
    before = _wir(baseline)
    after = _wir(candidate)
    if before.get("valid") is not True:
        failures.append(
            {
                "category": "infrastructure",
                "code": "baseline-wir-invalid",
                "detail": str(
                    before.get("failure_reason")
                    or "baseline WIR structural analysis is invalid"
                ),
            }
        )
    if before.get("valid") is True and after.get("valid") is not True:
        failures.append(
            {
                "category": "semantic",
                "code": "candidate-wir-invalid",
                "detail": str(
                    after.get("failure_reason")
                    or "candidate WIR structural analysis is invalid"
                ),
            }
        )


def _append_default_metric_rules(
    report: dict[str, Any],
    baseline: Mapping[str, Any],
    candidate: Mapping[str, Any],
    failures: list[dict[str, Any]],
) -> None:
    comparison = dict(_mapping(report.get("comparison")))
    deltas = [dict(item) for item in _mapping_list(comparison.get("metric_deltas"))]
    existing = {str(item.get("path")) for item in deltas}
    policy = dict(_mapping(report.get("policy")))
    policy_rules = dict(_mapping(policy.get("metric_deltas")))
    for path in _WIR_DEFAULT_PATHS:
        if path in existing:
            continue
        policy_rules[path] = {"minimum": None, "maximum": 0}
        before = _integer_path(baseline, path)
        after = _integer_path(candidate, path)
        delta = after - before if before is not None and after is not None else None
        passed = delta is not None and delta <= 0
        evidence = {
            "path": path,
            "available": before is not None and after is not None,
            "before": before,
            "after": after,
            "delta": delta,
            "minimum": None,
            "maximum": 0,
            "passed": passed,
        }
        deltas.append(evidence)
        if not passed:
            detail = (
                f"{path} is unavailable for deterministic comparison"
                if delta is None
                else f"{path} delta {delta} is outside [None, 0]"
            )
            failures.append(
                {
                    "category": "quality",
                    "code": "metric-delta-outside-policy",
                    "detail": detail,
                    "evidence": evidence,
                }
            )
    deltas.sort(key=lambda item: str(item.get("path")))
    comparison["metric_deltas"] = deltas
    report["comparison"] = comparison
    policy["metric_deltas"] = dict(sorted(policy_rules.items()))
    report["policy"] = policy


def _wir(result: Mapping[str, Any]) -> Mapping[str, Any]:
    analysis = _mapping(result.get("analysis"))
    return _mapping(analysis.get("wir"))


def _integer_path(document: Mapping[str, Any], path: str) -> int | None:
    value: Any = document
    for component in path.split("."):
        if not isinstance(value, Mapping) or component not in value:
            return None
        value = value[component]
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _mapping_list(value: object) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


__all__ = [
    "COMPILER_AUDIT_FORMAT",
    "COMPILER_AUDIT_POLICY_FORMAT",
    "COMPILER_AUDIT_SEAL_FORMAT",
    "CompilerAuditError",
    "CompilerAuditPolicy",
    "MetricDeltaRule",
    "ReviewCallback",
    "audit_compilers",
    "load_compiler_audit_policy",
    "resolve_compiler_input",
    "seal_compiler_audit",
]
