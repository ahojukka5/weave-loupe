"""Tests for self-contained reports."""

from __future__ import annotations

from pathlib import Path

from weave_loupe.bundle import capture_bundle, load_bundle
from weave_loupe.reporting import render_bundle_report, render_diff_report


def test_bundle_report_is_self_contained_and_escaped(
    tmp_path: Path, source_file: Path, fake_weavec: Path
) -> None:
    source_file.write_text("<script>alert(1)</script>\n")
    output = tmp_path / "demo.loupe"
    capture_bundle(sources=[source_file], output=output, weavec=fake_weavec)
    report = render_bundle_report(load_bundle(output))
    assert report.startswith("<!doctype html>")
    assert "&lt;script&gt;" in report
    assert "<script>" not in report
    assert "https://" not in report


def test_bundle_report_is_deterministic(
    tmp_path: Path, source_file: Path, fake_weavec: Path
) -> None:
    output = tmp_path / "demo.loupe"
    capture_bundle(sources=[source_file], output=output, weavec=fake_weavec)
    bundle = load_bundle(output)
    assert render_bundle_report(bundle) == render_bundle_report(bundle)


def test_v1_diff_report_contains_metric_table() -> None:
    report = render_diff_report(
        {
            "format": "weave-loupe-diff-v1",
            "llvm_metrics": {"instructions": {"before": 5, "after": 4, "delta": -1}},
        }
    )
    assert "Weave Loupe comparison" in report
    assert "Legacy" in report
    assert "instructions" in report
    assert "-1" in report


def test_v2_diff_report_contains_navigation_and_all_major_sections() -> None:
    report = render_diff_report(
        {
            "format": "weave-loupe-diff-v2",
            "summary": {
                "total_changes": 2,
                "by_classification": {"semantic": 1, "quality": 1},
                "by_severity": {"error": 1, "warning": 1},
            },
            "changes": [
                {
                    "severity": "error",
                    "classification": "semantic",
                    "section": "analysis.diagnostics",
                    "path": "abc",
                    "kind": "added",
                    "before": None,
                    "after": {"message": "<unsafe>"},
                }
            ],
            "analysis": {
                "llvm": {
                    "metrics": {
                        "instructions": {
                            "before": 5,
                            "after": 6,
                            "delta": 1,
                            "changed": True,
                        }
                    }
                },
                "optimized_llvm": {"metrics": {}},
                "native": {
                    "functions": {
                        "added": ["helper"],
                        "removed": [],
                        "modified": {},
                    }
                },
                "diagnostics": {"added": [{"message": "<unsafe>"}]},
            },
            "sources": {"items": {}},
            "artifacts": {
                "items": {
                    "llvm": {
                        "status": "hash-changed",
                        "before": {"sha256": "a"},
                        "after": {"sha256": "b"},
                    }
                }
            },
            "logs": {"items": {}},
            "supplemental": {
                "runtime": {"available": True, "changed": True},
                "native_budget": {"available": True, "changed": False},
            },
            "manifest": {"changed": True},
            "optimization_remarks": {"changed": True},
        }
    )

    assert "complete evidence comparison" in report
    assert 'href="#changes"' in report
    assert "Raw LLVM metrics" in report
    assert "Optimized LLVM metrics" in report
    assert "Native code and reachability" in report
    assert "Runtime and deterministic contracts" in report
    assert "Manifest and optimization remarks" in report
    assert "helper" in report
    assert "hash-changed" in report
    assert "&lt;unsafe&gt;" in report
    assert "<unsafe>" not in report
