"""Tests for bundle comparisons."""

from __future__ import annotations

from pathlib import Path

from weave_loupe.bundle import capture_bundle, load_bundle
from weave_loupe.diffing import compare_bundles


def test_compare_bundles_reports_zero_delta(
    tmp_path: Path, source_file: Path, fake_weavec: Path
) -> None:
    left = tmp_path / "left.loupe"
    right = tmp_path / "right.loupe"
    capture_bundle(sources=[source_file], output=left, weavec=fake_weavec)
    capture_bundle(sources=[source_file], output=right, weavec=fake_weavec)
    diff = compare_bundles(load_bundle(left), load_bundle(right))
    assert diff["format"] == "weave-loupe-diff-v1"
    assert diff["llvm_metrics"]["instructions"]["delta"] == 0
    assert diff["trace_actions"]["typed-integer-wrap"]["delta"] == 0
