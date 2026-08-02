"""Tests for deterministic WIR structural analysis."""

import pathlib

import weave_loupe.wir_analysis as wir_analysis

_LLVM = """declare i32 @puts(ptr)
define i32 @helper(i32 %x) {
entry:
  %negative = icmp slt i32 %x, 0
  br i1 %negative, label %return_x, label %return_zero
return_x:
  ret i32 %x
return_zero:
  ret i32 0
}
define i32 @main() {
entry:
  br label %loop
loop:
  %i = phi i32 [ 0, %entry ], [ %next, %loop ]
  %keep_going = icmp slt i32 %i, 4
  %next = add i32 %i, 1
  br i1 %keep_going, label %loop, label %exit
exit:
  ret i32 0
}
"""


def test_analyze_wir_produces_stable_golden_structure() -> None:
    path = pathlib.Path(__file__).parent / "fixtures" / "wir" / "structured.wir"
    wir = path.read_text(encoding="utf-8")

    analysis = wir_analysis.analyze_wir(wir, _LLVM)

    assert analysis == wir_analysis.analyze_wir(wir, _LLVM)
    assert analysis["format"] == wir_analysis.WIR_ANALYSIS_FORMAT
    assert analysis["available"] is True
    assert analysis["valid"] is True
    assert analysis["failure_reason"] is None
    assert analysis["core_version"] == 2
    assert analysis["metrics"] == {
        "declarations": 3,
        "functions": 2,
        "externs": 1,
        "unknown_declarations": 0,
        "blocks": 8,
        "reachable_blocks": 7,
        "unreachable_blocks": 1,
        "control_flow_edges": 6,
        "backedges": 1,
        "instructions": 29,
        "operands": 45,
        "calls": 1,
        "branches": 2,
        "loops": 1,
        "returns": 3,
        "locals": 3,
        "anonymous_identifiers": 0,
        "unresolved_symbols": 0,
        "duplicate_declarations": 0,
        "malformed_provenance": 0,
        "provenance_files": 1,
        "provenance_spans": 5,
        "mapped_functions": 2,
        "mapped_instructions": 2,
    }
    assert analysis["call_graph"] == {"helper": [], "main": ["helper"]}
    assert analysis["functions"]["helper"]["metrics"]["unreachable_blocks"] == 1
    assert analysis["functions"]["helper"]["metrics"]["unreachable_instructions"] == 2
    assert analysis["functions"]["main"]["metrics"]["backedges"] == 1
    assert analysis["provenance"]["malformed"] == []
    assert analysis["cross_stage"]["missing_definitions"] == []
    assert analysis["cross_stage"]["unexpected_definitions"] == []
    assert analysis["cross_stage"]["missing_externs"] == []
    assert analysis["cross_stage"]["functions"]["helper"] == {
        "wir_blocks": 4,
        "llvm_blocks": 3,
        "block_delta": -1,
    }
    assert analysis["cross_stage"]["functions"]["main"] == {
        "wir_blocks": 4,
        "llvm_blocks": 3,
        "block_delta": -1,
    }


def test_analyze_wir_reports_syntax_and_envelope_failures() -> None:
    syntax = wir_analysis.analyze_wir("(core-module")
    version = wir_analysis.analyze_wir("(core-module (core-version 1) (decls))")

    assert syntax["available"] is True
    assert syntax["valid"] is False
    assert "unclosed WIR list" in syntax["failure_reason"]
    assert syntax["metrics"]["functions"] == 0
    assert version["valid"] is False
    assert version["failure_reason"] == (
        "WIR core-version must contain the single integer token 2"
    )


def test_analyze_wir_reports_symbols_names_and_provenance() -> None:
    wir = """; weavec-source-file-v1 broken
; weavec-source-span-v1 7 10 5
(core-module
  (core-version 2)
  (decls
    (fn 1
      (params)
      (returns i32)
      (do
        (call_i32 missing)
        (return (local_get absent))))))
"""

    analysis = wir_analysis.analyze_wir(
        wir,
        "define i32 @other() { ret i32 0 }\n",
    )

    assert analysis["valid"] is True
    assert analysis["anonymous_identifiers"] == ["1"]
    assert analysis["unresolved_symbols"] == ["call:missing", "local:absent"]
    assert analysis["metrics"]["malformed_provenance"] == 2
    assert analysis["cross_stage"]["missing_definitions"] == ["1"]
    assert analysis["cross_stage"]["unexpected_definitions"] == ["other"]
