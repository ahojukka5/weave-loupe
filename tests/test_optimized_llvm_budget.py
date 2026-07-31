"""Tests for deterministic optimized LLVM contracts."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from weave_loupe.analysis import analyze_llvm
from weave_loupe.optimized_llvm_budget import (
    OptimizedLlvmBudgetError,
    evaluate_optimized_llvm_budget,
    load_optimized_llvm_budget,
)


def _write_budget(source: Path, budget: dict[str, object]) -> Path:
    sidecar = source.with_suffix(".audit.json")
    sidecar.write_text(
        json.dumps(
            {
                "format": "weave-loupe-runtime-cases-v1",
                "optimized_llvm_budget": {
                    "format": "weave-loupe-optimized-llvm-budget-v1",
                    **budget,
                },
            }
        ),
        encoding="utf-8",
    )
    return sidecar


def _constant_llvm() -> str:
    return """define i32 @main() {
entry:
  ret i32 55
}
"""


def _runtime_llvm() -> str:
    return """declare ptr @getenv(ptr)
declare i32 @atoi(ptr)
define i32 @main() {
entry:
  %input = call ptr @getenv(ptr null)
  %parsed = call i32 @atoi(ptr %input)
  br label %loop
loop:
  %i = phi i32 [ 0, %entry ], [ %next, %loop ]
  %value = phi i32 [ 0, %entry ], [ %sum, %loop ]
  %sum = add i32 %value, 1
  %next = add i32 %i, 1
  %done = icmp sge i32 %next, %parsed
  br i1 %done, label %exit, label %loop
exit:
  ret i32 %sum
}
"""


def test_optimized_llvm_budget_accepts_exact_constant_module(tmp_path: Path) -> None:
    source = tmp_path / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")
    sidecar = _write_budget(
        source,
        {
            "min_functions": 1,
            "max_functions": 1,
            "min_instructions": 1,
            "max_instructions": 1,
            "max_call": 0,
            "max_alloca": 0,
            "max_load": 0,
            "max_store": 0,
            "required_defined_functions": ["main"],
        },
    )
    llvm_ir = _constant_llvm()

    result = evaluate_optimized_llvm_budget(
        sources=[source],
        optimized_llvm=llvm_ir,
        metrics=analyze_llvm(llvm_ir),
    )

    assert result["configured"] is True
    assert result["passed"] is True
    assert result["failures"] == []
    assert result["sidecar"] == str(sidecar)
    assert len(result["sidecar_sha256"]) == 64
    assert result["observed"]["functions"] == 1
    assert result["observed"]["instructions"] == 1
    assert result["observed"]["defined_functions"] == ["main"]
    assert result["observed"]["call_targets"] == []


def test_optimized_llvm_budget_accepts_required_calls_and_ssa(tmp_path: Path) -> None:
    source = tmp_path / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")
    _write_budget(
        source,
        {
            "max_functions": 1,
            "max_instructions": 20,
            "max_alloca": 0,
            "max_load": 0,
            "max_store": 0,
            "min_call": 2,
            "max_call": 2,
            "min_phi": 2,
            "min_br": 2,
            "required_defined_functions": ["main"],
            "required_call_targets": ["atoi", "getenv"],
        },
    )
    llvm_ir = _runtime_llvm()

    result = evaluate_optimized_llvm_budget(
        sources=[source],
        optimized_llvm=llvm_ir,
        metrics=analyze_llvm(llvm_ir),
    )

    assert result["passed"] is True
    assert result["observed"]["call_targets"] == ["atoi", "getenv"]
    assert result["observed"]["defined_functions"] == ["main"]
    assert result["observed"]["alloca"] == 0
    assert result["observed"]["load"] == 0
    assert result["observed"]["store"] == 0


def test_optimized_llvm_budget_reports_all_contract_failures(tmp_path: Path) -> None:
    source = tmp_path / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")
    _write_budget(
        source,
        {
            "max_instructions": 0,
            "min_phi": 1,
            "required_defined_functions": ["helper", "main"],
            "required_call_targets": ["getenv"],
        },
    )
    llvm_ir = _constant_llvm()

    result = evaluate_optimized_llvm_budget(
        sources=[source],
        optimized_llvm=llvm_ir,
        metrics=analyze_llvm(llvm_ir),
    )

    assert result["passed"] is False
    assert result["failures"] == [
        "optimized LLVM instructions 1 exceeds maximum 0",
        "optimized LLVM phi 0 is below minimum 1",
        "optimized LLVM missing required defined functions: helper",
        "optimized LLVM missing required call targets: getenv",
    ]


def test_optimized_llvm_budget_fails_closed_without_ir(tmp_path: Path) -> None:
    source = tmp_path / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")
    _write_budget(source, {"max_instructions": 1})

    result = evaluate_optimized_llvm_budget(
        sources=[source],
        optimized_llvm="",
        metrics={},
    )

    assert result["passed"] is False
    assert result["failures"] == ["optimized LLVM IR is unavailable"]


def test_optimized_llvm_budget_is_optional(tmp_path: Path) -> None:
    source = tmp_path / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")

    result = evaluate_optimized_llvm_budget(
        sources=[source],
        optimized_llvm=_constant_llvm(),
        metrics=analyze_llvm(_constant_llvm()),
    )

    assert result == {
        "format": "weave-loupe-optimized-llvm-budget-result-v1",
        "configured": False,
        "passed": True,
        "failures": [],
    }


def test_optimized_llvm_budget_rejects_invalid_schema(tmp_path: Path) -> None:
    source = tmp_path / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")
    sidecar = _write_budget(source, {"maximum_instructions": 1})

    with pytest.raises(OptimizedLlvmBudgetError, match="unknown fields"):
        load_optimized_llvm_budget(sidecar)

    sidecar = _write_budget(source, {"max_instructions": -1})
    with pytest.raises(OptimizedLlvmBudgetError, match="non-negative integer"):
        load_optimized_llvm_budget(sidecar)

    sidecar = _write_budget(
        source,
        {"min_instructions": 2, "max_instructions": 1},
    )
    with pytest.raises(OptimizedLlvmBudgetError, match="minimum must not exceed"):
        load_optimized_llvm_budget(sidecar)

    sidecar = _write_budget(
        source,
        {"required_call_targets": ["getenv", "getenv"]},
    )
    with pytest.raises(OptimizedLlvmBudgetError, match="must not contain duplicates"):
        load_optimized_llvm_budget(sidecar)
