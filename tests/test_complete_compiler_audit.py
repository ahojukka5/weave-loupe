"""Tests for WIR-aware compiler audit policy."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import patch

from weave_loupe.bundle import Bundle
from weave_loupe.complete_compiler_audit import audit_compilers


def test_invalid_baseline_wir_is_infrastructure(tmp_path: Path) -> None:
    report = _run(
        tmp_path,
        baseline=_result(valid=False, reason="bad baseline"),
        candidate=_result(valid=True),
    )

    assert report["status"] == "infrastructure-failure"
    assert "baseline-wir-invalid" in _codes(report)


def test_invalid_candidate_wir_is_semantic_regression(tmp_path: Path) -> None:
    report = _run(
        tmp_path,
        baseline=_result(valid=True),
        candidate=_result(valid=False, reason="bad candidate"),
    )

    assert report["status"] == "regression"
    assert "candidate-wir-invalid" in _codes(report)


def test_default_wir_metric_increase_fails_and_is_published(tmp_path: Path) -> None:
    baseline = _result(valid=True)
    candidate = _result(valid=True)
    candidate["analysis"]["wir"]["metrics"]["unreachable_blocks"] = 1
    reviewed: list[dict[str, Any]] = []

    def reviewer(evidence):
        reviewed.append(dict(evidence))
        return {"status": "OK", "body": "reviewed complete evidence"}

    report = _run(
        tmp_path,
        baseline=baseline,
        candidate=candidate,
        reviewer=reviewer,
    )

    path = "analysis.wir.metrics.unreachable_blocks"
    assert report["passed"] is False
    assert "metric-delta-outside-policy" in _codes(report)
    assert report["policy"]["metric_deltas"][path] == {
        "minimum": None,
        "maximum": 0,
    }
    delta = next(
        item for item in report["comparison"]["metric_deltas"] if item["path"] == path
    )
    assert delta["delta"] == 1
    assert delta["passed"] is False
    assert reviewed
    wir_diff = reviewed[0]["comparison"]["bundle_diff"]["analysis"]["wir"]
    assert wir_diff["changed"] is True
    assert report["review"]["status"] == "OK"


def _run(
    tmp_path: Path,
    *,
    baseline: dict[str, Any],
    candidate: dict[str, Any],
    reviewer=None,
) -> dict[str, Any]:
    original = {
        "format": "weave-loupe-compiler-audit-v1",
        "status": "pass",
        "passed": True,
        "sources": [],
        "policy": {
            "format": "weave-loupe-compiler-audit-policy-v1",
            "metric_deltas": {},
            "forbid_changes": [],
        },
        "baseline": baseline,
        "candidate": candidate,
        "comparison": {"bundle_diff": {}, "metric_deltas": []},
        "failures": [],
        "review": None,
        "seal": {"format": "old", "sha256": "old"},
    }
    bundle = Bundle(root=tmp_path, manifest={"format": "weave-loupe-bundle-v1"})
    wir_changed = baseline["analysis"]["wir"] != candidate["analysis"]["wir"]
    complete_diff = {
        "format": "weave-loupe-diff-v2",
        "analysis": {"wir": {"changed": wir_changed}},
        "changes": [],
        "summary": {"changed": wir_changed},
    }
    with (
        patch(
            "weave_loupe.complete_compiler_audit._audit_without_wir",
            return_value=original,
        ),
        patch(
            "weave_loupe.complete_compiler_audit.load_bundle",
            return_value=bundle,
        ),
        patch(
            "weave_loupe.complete_compiler_audit.compare_bundles",
            return_value=complete_diff,
        ),
    ):
        return audit_compilers(
            sources=[tmp_path / "demo.weave"],
            baseline_weavec=tmp_path / "baseline-weavec",
            candidate_weavec=tmp_path / "candidate-weavec",
            work_dir=tmp_path,
            reviewer=reviewer,
        )


def _result(*, valid: bool, reason: str | None = None) -> dict[str, Any]:
    zero_metrics = {
        "unreachable_blocks": 0,
        "unresolved_symbols": 0,
        "anonymous_identifiers": 0,
        "malformed_provenance": 0,
    }
    zero_cross_stage = {
        "missing_definitions": 0,
        "unexpected_definitions": 0,
        "missing_externs": 0,
        "duplicate_llvm_definitions": 0,
        "duplicate_llvm_declarations": 0,
    }
    return {
        "compiler": {},
        "compiler_exit_code": 0,
        "analysis": {
            "wir": {
                "valid": valid,
                "failure_reason": reason,
                "metrics": zero_metrics,
                "cross_stage": {"metrics": zero_cross_stage},
            },
            "diagnostics": {},
            "evidence": {},
        },
        "runtime": {},
        "native_budget": {},
        "optimized_llvm_budget": {},
        "artifacts": {},
    }


def _codes(report: dict[str, Any]) -> set[str]:
    return {
        str(item["code"])
        for item in report["failures"]
        if isinstance(item, dict) and "code" in item
    }
