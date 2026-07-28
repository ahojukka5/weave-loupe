"""Tests for deterministic native optimization budgets."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from weave_loupe.native_budget import (
    NativeBudgetError,
    evaluate_native_budget,
    load_native_budget,
)


def _write_budget(source: Path, budget: dict[str, object]) -> Path:
    sidecar = source.with_suffix(".audit.json")
    sidecar.write_text(
        json.dumps(
            {
                "format": "weave-loupe-runtime-cases-v1",
                "native_budget": {
                    "format": "weave-loupe-native-budget-v1",
                    **budget,
                },
            }
        ),
        encoding="utf-8",
    )
    return sidecar


def _native() -> dict[str, object]:
    return {
        "available": True,
        "reachability_complete": True,
        "program_owned_functions": ["main"],
        "reachable_program_functions": ["main"],
        "unreachable_program_functions": [],
        "unreachable_program_instructions": 0,
        "functions": {
            "main": {
                "instructions": 2,
                "padding_instructions": 0,
                "direct_calls": [],
                "indirect_calls": 0,
            }
        },
    }


def test_native_budget_accepts_exact_final_code(tmp_path: Path) -> None:
    source = tmp_path / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")
    sidecar = _write_budget(
        source,
        {
            "max_program_owned_functions": 1,
            "max_reachable_program_functions": 1,
            "max_unreachable_program_functions": 0,
            "max_unreachable_program_instructions": 0,
            "functions": {
                "main": {
                    "max_instructions": 2,
                    "max_padding_instructions": 0,
                    "max_direct_calls": 0,
                    "max_indirect_calls": 0,
                }
            },
        },
    )

    result = evaluate_native_budget(sources=[source], native_analysis=_native())

    assert result["configured"] is True
    assert result["passed"] is True
    assert result["failures"] == []
    assert result["sidecar"] == str(sidecar)
    assert len(result["sidecar_sha256"]) == 64
    assert result["observed"]["program_owned_functions"] == 1
    assert result["observed"]["functions"]["main"] == {
        "present": True,
        "instructions": 2,
        "padding_instructions": 0,
        "direct_calls": 0,
        "indirect_calls": 0,
    }


def test_native_budget_reports_every_exceeded_limit(tmp_path: Path) -> None:
    source = tmp_path / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")
    _write_budget(
        source,
        {
            "max_program_owned_functions": 0,
            "max_unreachable_program_functions": 0,
            "functions": {
                "main": {
                    "max_instructions": 1,
                    "max_padding_instructions": 0,
                    "max_direct_calls": 0,
                    "max_indirect_calls": 0,
                },
                "helper": {"max_instructions": 4},
            },
        },
    )
    native = _native()
    native["unreachable_program_functions"] = ["dead"]

    result = evaluate_native_budget(sources=[source], native_analysis=native)

    assert result["passed"] is False
    assert result["failures"] == [
        "program owned functions 1 exceeds maximum 0",
        "unreachable program functions 1 exceeds maximum 0",
        "required native function 'helper' is missing",
        "function 'main' instructions 2 exceeds maximum 1",
    ]


def test_native_budget_fails_closed_without_complete_native_evidence(
    tmp_path: Path,
) -> None:
    source = tmp_path / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")
    _write_budget(source, {"max_program_owned_functions": 1})

    result = evaluate_native_budget(
        sources=[source],
        native_analysis={"available": False, "reachability_complete": False},
    )

    assert result["passed"] is False
    assert result["failures"][:2] == [
        "linked executable disassembly is unavailable",
        "native program-function reachability is incomplete",
    ]


def test_native_budget_is_optional(tmp_path: Path) -> None:
    source = tmp_path / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")

    result = evaluate_native_budget(sources=[source], native_analysis=_native())

    assert result == {
        "format": "weave-loupe-native-budget-result-v1",
        "configured": False,
        "passed": True,
        "failures": [],
    }


def test_native_budget_rejects_unknown_and_negative_limits(tmp_path: Path) -> None:
    source = tmp_path / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")
    sidecar = _write_budget(source, {"maximum_instructions": 2})

    with pytest.raises(NativeBudgetError, match="unknown fields"):
        load_native_budget(sidecar)

    sidecar = _write_budget(source, {"max_program_owned_functions": -1})
    with pytest.raises(NativeBudgetError, match="non-negative integer"):
        load_native_budget(sidecar)
