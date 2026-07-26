"""Tests for deterministic artifact analysis."""

from __future__ import annotations

from pathlib import Path

from weave_loupe.analysis import analyze_bundle, analyze_llvm, analyze_trace
from weave_loupe.bundle import capture_bundle, load_bundle


def test_analyze_llvm_counts_structure() -> None:
    llvm = """define i32 @f() {
entry:
  %0 = alloca i32
  store i32 1, ptr %0
  %x = load i32, ptr %0
  %y = add i32 %x, 0
  br label %1
1:
  ret i32 %y
}
"""
    metrics = analyze_llvm(llvm)
    assert metrics["functions"] == 1
    assert metrics["basic_blocks"] == 2
    assert metrics["instructions"] == 6
    assert metrics["alloca"] == 1
    assert metrics["identity_adds"] == 1
    assert metrics["anonymous_ssa_lines"] == 4
    assert metrics["numeric_blocks"] == 1


def test_analyze_llvm_counts_provenance() -> None:
    metrics = analyze_llvm(
        "; weave.source kind=statement index=0 bytes=0..1 "
        'wir-bytes=0..2 path="x.weave"\n'
    )
    assert metrics["provenance_comments"] == 1


def test_analyze_trace_groups_actions() -> None:
    summary = analyze_trace(
        {
            "events": [
                {"action": "x", "pass": "lower", "category": "lowering"},
                {"action": "x", "pass": "lower", "category": "lowering"},
            ]
        }
    )
    assert summary["events"] == 2
    assert summary["actions"] == {"x": 2}


def test_analyze_bundle_uses_captured_artifacts(
    tmp_path: Path, source_file: Path, fake_weavec: Path
) -> None:
    output = tmp_path / "demo.loupe"
    capture_bundle(sources=[source_file], output=output, weavec=fake_weavec)
    analysis = analyze_bundle(load_bundle(output))
    assert analysis["format"] == "weave-loupe-analysis-v1"
    assert analysis["compiler_exit_code"] == 0
    assert analysis["trace"]["events"] == 1
    assert analysis["llvm"]["identity_adds"] == 1
