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
        "WIR core version 1 is unsupported, expected 2 or 3"
    )
    assert version["core_version"] is None


def test_analyze_wir_rejects_a_malformed_version_token() -> None:
    missing = wir_analysis.analyze_wir("(core-module (core-version) (decls))")
    string = wir_analysis.analyze_wir('(core-module (core-version "2") (decls))')

    expected = "WIR core-version must contain a single integer token, one of 2 or 3"
    assert missing["valid"] is False
    assert missing["failure_reason"] == expected
    assert string["valid"] is False
    assert string["failure_reason"] == expected


def test_analyze_wir_accepts_every_supported_core_version() -> None:
    template = """(core-module
  (core-version {version})
  (decls
    (fn main
      (params)
      (returns i32)
      (do (return (const_i32 0))))))
"""

    for version in wir_analysis.SUPPORTED_CORE_VERSIONS:
        analysis = wir_analysis.analyze_wir(template.format(version=version))

        assert analysis["valid"] is True, version
        assert analysis["failure_reason"] is None, version
        # The declared version is reported, not the one Loupe happens to prefer.
        assert analysis["core_version"] == version


def test_analyze_wir_counts_unfamiliar_forms_without_interpreting_them() -> None:
    # Struct field access as proposed for the next core version. The analysis is
    # form-generic, so a form it has never seen is counted as an opcode without
    # a change here -- and a field access must not become a call-graph edge.
    wir = """(core-module
  (core-version 3)
  (decls
    (struct Point
      (field x f64)
      (field y f64))
    (fn read
      (params (p ptr))
      (returns f64)
      (do (return (field_get_f64 Point x (param_get p)))))))
"""

    analysis = wir_analysis.analyze_wir(wir)

    assert analysis["valid"] is True
    assert analysis["core_version"] == 3
    assert analysis["opcodes"]["field_get_f64"] == 1
    assert analysis["call_graph"]["read"] == []
    assert analysis["metrics"]["calls"] == 0
    assert analysis["metrics"]["unresolved_symbols"] == 0

    # The declaration is recorded by kind and name, and counted as unknown
    # because Loupe does not model structs yet. That is a reporting fact rather
    # than a failure: no gate reads this metric. Teaching Loupe the declaration
    # belongs with the version that finalizes its form.
    assert analysis["declarations"][0]["kind"] == "struct"
    assert analysis["declarations"][0]["name"] == "Point"
    assert analysis["metrics"]["unknown_declarations"] == 1


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
