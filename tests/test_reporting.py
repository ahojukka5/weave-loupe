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


def test_diff_report_contains_metric_table() -> None:
    report = render_diff_report(
        {"llvm_metrics": {"instructions": {"before": 5, "after": 4, "delta": -1}}}
    )
    assert "Weave Loupe comparison" in report
    assert "instructions" in report
    assert "-1" in report
