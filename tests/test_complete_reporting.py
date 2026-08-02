"""Tests for focused self-contained HTML reports."""

from __future__ import annotations

from pathlib import Path

from weave_loupe.bundle import capture_bundle, load_bundle
from weave_loupe.complete_reporting import render_bundle_report, render_diff_report


def test_bundle_report_contains_wir_and_remark_sections(
    tmp_path: Path,
    source_file: Path,
    fake_weavec: Path,
) -> None:
    output = tmp_path / "demo.loupe"
    capture_bundle(sources=[source_file], output=output, weavec=fake_weavec)

    report = render_bundle_report(load_bundle(output))

    assert report.startswith("<!doctype html>")
    assert "WIR structural analysis" in report
    assert "WIR functions and control flow" in report
    assert "WIR provenance" in report
    assert "WIR-to-LLVM correspondence" in report
    assert "LLVM optimization remarks" in report
    assert "Remark categories" in report
    assert "Optimization passes" in report
    assert "Highest-value missed optimizations" in report
    assert "Complete normalized optimization remarks" in report
    assert "https://" not in report


def test_v2_diff_report_contains_navigable_focused_sections() -> None:
    diff = {
        "format": "weave-loupe-diff-v2",
        "summary": {
            "total_changes": 2,
            "by_classification": {"quality": 2},
            "by_severity": {"warning": 2},
        },
        "changes": [
            {
                "section": "analysis.wir",
                "path": "metrics.unreachable_blocks",
                "kind": "delta",
                "classification": "quality",
                "severity": "warning",
                "before": 0,
                "after": 1,
            },
            {
                "section": "optimization_remarks",
                "path": "missed",
                "kind": "added",
                "classification": "quality",
                "severity": "warning",
                "before": None,
                "after": {"name": "NoDefinition"},
            },
        ],
        "analysis": {
            "wir": {
                "metrics": {
                    "unreachable_blocks": {
                        "before": 0,
                        "after": 1,
                        "delta": 1,
                        "changed": True,
                    }
                },
                "functions": {
                    "added": ["helper"],
                    "removed": [],
                    "modified": ["main"],
                },
                "provenance": {"changed": False},
                "cross_stage": {"missing_definitions": {"added": ["helper"]}},
            },
            "llvm": {"metrics": {}},
            "optimized_llvm": {"metrics": {}},
            "native": {},
            "diagnostics": {},
        },
        "sources": {},
        "artifacts": {},
        "logs": {},
        "supplemental": {},
        "manifest": {},
        "optimization_remarks": {
            "counters": {
                "by_category": {
                    "missed": {
                        "before": 0,
                        "after": 1,
                        "delta": 1,
                        "changed": True,
                    }
                }
            },
            "added": [
                {
                    "category": "missed",
                    "function": "main",
                    "pass": "inline",
                    "name": "NoDefinition",
                    "hotness": 100,
                    "message": "helper has no definition",
                }
            ],
            "removed": [],
        },
    }

    report = render_diff_report(diff)

    assert '<a href="#wir">WIR</a>' in report
    assert '<section id="wir">' in report
    assert "WIR structure and lowering correspondence" in report
    assert "unreachable_blocks" in report
    assert "helper" in report
    assert '<a href="#optimization-remarks">Optimization remarks</a>' in report
    assert '<section id="optimization-remarks">' in report
    assert "LLVM optimization remark changes" in report
    assert "NoDefinition" in report
    assert "helper has no definition" in report
    assert report.index('href="#wir"') < report.index('href="#llvm"')
    assert report.index('href="#optimization-remarks"') < report.index(
        'href="#manifest"'
    )


def test_v1_diff_report_remains_legacy() -> None:
    diff = {
        "format": "weave-loupe-diff-v1",
        "llvm_metrics": {"instructions": {"before": 1, "after": 1, "delta": 0}},
        "trace_actions": {},
        "trace_passes": {},
    }

    report = render_diff_report(diff)

    assert "Legacy <code>weave-loupe-diff-v1</code>" in report
    assert '<section id="wir">' not in report
    assert '<section id="optimization-remarks">' not in report
