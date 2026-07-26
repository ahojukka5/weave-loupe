"""Comparison of compiler-evidence bundles."""

from __future__ import annotations

from typing import Any, Mapping, cast

from weave_loupe.analysis import analyze_bundle
from weave_loupe.bundle import Bundle


def compare_bundles(before: Bundle, after: Bundle) -> dict[str, Any]:
    """Compare deterministic analyses from two bundles."""
    left = analyze_bundle(before)
    right = analyze_bundle(after)
    left_llvm = cast(Mapping[str, int], left["llvm"])
    right_llvm = cast(Mapping[str, int], right["llvm"])
    metric_names = sorted(set(left_llvm) | set(right_llvm))
    metrics = {
        name: {
            "before": int(left_llvm.get(name, 0)),
            "after": int(right_llvm.get(name, 0)),
            "delta": int(right_llvm.get(name, 0)) - int(left_llvm.get(name, 0)),
        }
        for name in metric_names
    }

    left_trace = cast(Mapping[str, Any], left["trace"])
    right_trace = cast(Mapping[str, Any], right["trace"])
    return {
        "format": "weave-loupe-diff-v1",
        "llvm_metrics": metrics,
        "trace_actions": _counter_diff(
            cast(Mapping[str, int], left_trace.get("actions", {})),
            cast(Mapping[str, int], right_trace.get("actions", {})),
        ),
        "trace_passes": _counter_diff(
            cast(Mapping[str, int], left_trace.get("passes", {})),
            cast(Mapping[str, int], right_trace.get("passes", {})),
        ),
    }


def _counter_diff(
    before: Mapping[str, int], after: Mapping[str, int]
) -> dict[str, dict[str, int]]:
    names = sorted(set(before) | set(after))
    return {
        name: {
            "before": int(before.get(name, 0)),
            "after": int(after.get(name, 0)),
            "delta": int(after.get(name, 0)) - int(before.get(name, 0)),
        }
        for name in names
    }
