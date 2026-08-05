"""Pure comparison of captured compiler evidence."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from weave_loupe.compiler_audit.model import CompilerAuditPolicy, CompilerEvidence
from weave_loupe.diffing import compare_bundles

_RUNTIME_VOLATILE = {
    "elapsed_seconds",
    "executable_sha256",
    "limits",
    "sandbox",
    "sidecar",
    "timeout_seconds",
}


def compare_compiler_evidence(
    baseline: CompilerEvidence,
    candidate: CompilerEvidence,
    policy: CompilerAuditPolicy,
) -> dict[str, Any]:
    """Return deterministic bundle, metric, runtime, and summary comparisons."""
    before = baseline.result
    after = candidate.result
    return {
        "bundle_diff": compare_bundles(
            baseline.bundle,
            candidate.bundle,
            before_context=before,
            after_context=after,
        ),
        "metric_deltas": metric_deltas(before, after, policy),
        "runtime_equal": stable_runtime(before["runtime"])
        == stable_runtime(after["runtime"]),
        "diagnostics_equal": before["analysis"]["diagnostics"]
        == after["analysis"]["diagnostics"],
        "evidence_equal": before["analysis"]["evidence"]
        == after["analysis"]["evidence"],
    }


def metric_deltas(
    baseline: Mapping[str, Any],
    candidate: Mapping[str, Any],
    policy: CompilerAuditPolicy,
) -> list[dict[str, Any]]:
    """Compare every policy-controlled numeric evidence path."""
    changes: list[dict[str, Any]] = []
    for path, rule in sorted(policy.metric_deltas.items()):
        before = _numeric_path(baseline, path)
        after = _numeric_path(candidate, path)
        if before is None or after is None:
            delta = None
            passed = False
        else:
            delta = after - before
            passed = (rule.minimum is None or delta >= rule.minimum) and (
                rule.maximum is None or delta <= rule.maximum
            )
        changes.append(
            {
                "path": path,
                "available": before is not None and after is not None,
                "before": before,
                "after": after,
                "delta": delta,
                "minimum": rule.minimum,
                "maximum": rule.maximum,
                "passed": passed,
            }
        )
    return changes


def stable_runtime(value: Any) -> Any:
    """Remove volatile runtime fields before deterministic comparison."""
    if isinstance(value, Mapping):
        return {
            key: stable_runtime(item)
            for key, item in sorted(value.items())
            if key not in _RUNTIME_VOLATILE
        }
    if isinstance(value, list):
        return [stable_runtime(item) for item in value]
    return value


def stable_contract(value: Any) -> Any:
    """Remove sidecar location identity from a contract comparison."""
    if not isinstance(value, Mapping):
        return value
    return {
        key: stable_contract(item)
        for key, item in sorted(value.items())
        if key not in {"sidecar", "sidecar_sha256"}
    }


def _numeric_path(document: Mapping[str, Any], path: str) -> int | None:
    value: Any = document
    for component in path.split("."):
        if not isinstance(value, Mapping) or component not in value:
            return None
        value = value[component]
    return value if isinstance(value, int) and not isinstance(value, bool) else None
