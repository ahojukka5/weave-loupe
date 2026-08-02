"""Tests for deterministic WIR structural comparisons."""

from __future__ import annotations

from copy import deepcopy

from weave_loupe.wir_diffing import compare_wir_analysis


def test_identical_wir_analyses_have_empty_stable_changes() -> None:
    analysis = _analysis()

    section, changes = compare_wir_analysis(analysis, deepcopy(analysis))

    assert section["changed"] is False
    assert section["change_count"] == 0
    assert changes == []
    assert (section, changes) == compare_wir_analysis(analysis, deepcopy(analysis))


def test_wir_only_changes_are_explicit_and_classified() -> None:
    before = _analysis()
    after = deepcopy(before)
    after["metrics"]["instructions"] = 4
    after["metrics"]["unreachable_blocks"] = 1
    after["opcodes"]["return"] = 2
    after["functions"]["main"]["metrics"]["instructions"] = 4
    after["functions"]["main"]["blocks"].append(
        {
            "id": "b1",
            "role": "unreachable",
            "reachable": False,
            "instructions": 1,
            "opcodes": ["return"],
        }
    )
    after["functions"]["helper"] = {
        "params": [],
        "returns": ["i32"],
        "metrics": {"blocks": 1, "instructions": 1},
        "opcodes": {"return": 1},
        "types": {"i32": 1},
        "calls": [],
        "locals": [],
        "duplicate_locals": [],
        "anonymous_identifiers": [],
        "unresolved_symbols": [],
        "blocks": [
            {
                "id": "b0",
                "role": "entry",
                "reachable": True,
                "instructions": 1,
                "opcodes": ["return"],
            }
        ],
        "edges": [],
        "provenance": {"spans": [], "mapped_instructions": 0},
    }
    after["call_graph"]["helper"] = []
    after["provenance"]["malformed"] = ["line 2: malformed source-span record"]
    after["cross_stage"]["missing_definitions"] = ["helper"]
    after["cross_stage"]["metrics"]["missing_definitions"] = 1

    section, changes = compare_wir_analysis(before, after)

    assert section["changed"] is True
    assert section["metrics"]["instructions"]["delta"] == 1
    assert section["functions"]["added"] == ["helper"]
    assert section["functions"]["modified"] == ["main"]
    assert section["cross_stage"]["missing_definitions"]["added"] == ["helper"]
    assert any(
        item["path"] == "functions.helper"
        and item["classification"] == "semantic"
        and item["severity"] == "error"
        for item in changes
    )
    assert any(
        item["path"] == "metrics.unreachable_blocks"
        and item["classification"] == "quality"
        and item["severity"] == "warning"
        for item in changes
    )
    assert any(
        item["path"].startswith("provenance.")
        and item["classification"] == "provenance"
        for item in changes
    )
    assert any(
        item["path"] == "cross_stage.missing_definitions.helper"
        and item["classification"] == "semantic"
        and item["severity"] == "error"
        for item in changes
    )
    assert changes == sorted(
        changes,
        key=lambda item: (
            item["section"],
            item["path"],
            item["kind"],
            item["classification"],
            item["severity"],
        ),
    )


def test_invalid_wir_transition_is_evidence_error() -> None:
    before = _analysis()
    after = deepcopy(before)
    after["valid"] = False
    after["failure_reason"] = "unclosed WIR list at byte offset 0"

    _, changes = compare_wir_analysis(before, after)

    assert any(
        item["path"] == "valid"
        and item["classification"] == "evidence"
        and item["severity"] == "error"
        for item in changes
    )
    assert any(item["path"] == "failure_reason" for item in changes)


def _analysis() -> dict[str, object]:
    return {
        "format": "weave-loupe-wir-analysis-v1",
        "available": True,
        "valid": True,
        "failure_reason": None,
        "core_version": 2,
        "metrics": {
            "functions": 1,
            "blocks": 1,
            "instructions": 3,
            "unreachable_blocks": 0,
            "unresolved_symbols": 0,
        },
        "opcodes": {"return": 1},
        "types": {"i32": 1},
        "declarations": [
            {"kind": "fn", "name": "main", "params": [], "returns": ["i32"]}
        ],
        "duplicate_declarations": [],
        "anonymous_identifiers": [],
        "unresolved_symbols": [],
        "functions": {
            "main": {
                "params": [],
                "returns": ["i32"],
                "metrics": {"blocks": 1, "instructions": 3},
                "opcodes": {"return": 1},
                "types": {"i32": 1},
                "calls": [],
                "locals": [],
                "duplicate_locals": [],
                "anonymous_identifiers": [],
                "unresolved_symbols": [],
                "blocks": [
                    {
                        "id": "b0",
                        "role": "entry",
                        "reachable": True,
                        "instructions": 3,
                        "opcodes": ["return"],
                    }
                ],
                "edges": [],
                "provenance": {"spans": [], "mapped_instructions": 0},
            }
        },
        "call_graph": {"main": []},
        "provenance": {
            "files": [{"index": 0, "path": "demo.weave"}],
            "spans": [],
            "malformed": [],
        },
        "cross_stage": {
            "wir_functions": ["main"],
            "wir_externs": [],
            "llvm_definitions": ["main"],
            "llvm_declarations": [],
            "missing_definitions": [],
            "unexpected_definitions": [],
            "missing_externs": [],
            "duplicate_llvm_definitions": [],
            "duplicate_llvm_declarations": [],
            "metrics": {
                "missing_definitions": 0,
                "unexpected_definitions": 0,
                "missing_externs": 0,
                "duplicate_llvm_definitions": 0,
                "duplicate_llvm_declarations": 0,
            },
            "functions": {
                "main": {
                    "wir_blocks": 1,
                    "llvm_blocks": 1,
                    "block_delta": 0,
                }
            },
        },
    }
