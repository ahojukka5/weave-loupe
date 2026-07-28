"""Tests for deterministic audit overrides."""

from __future__ import annotations

from weave_loupe.audit_result import AuditVerdict
from weave_loupe.deterministic_gate import apply_deterministic_gate


def _ok_verdict() -> AuditVerdict:
    return AuditVerdict(
        status="OK",
        code=None,
        reason=None,
        body="## Summary\nThe model found no problem.",
    )


def test_dead_native_code_overrides_model_ok() -> None:
    analysis = {
        "native": {
            "reachability_complete": True,
            "unreachable_program_functions": ["fib", "weave_rt_contract_fail"],
            "unreachable_program_instructions": 37,
        }
    }

    verdict = apply_deterministic_gate(_ok_verdict(), analysis)

    assert not verdict.passed
    assert verdict.code == "dead-native-code"
    assert verdict.reason == (
        "unreachable program-owned native functions remain: fib, weave_rt_contract_fail"
    )
    assert "The model returned `OK`" in verdict.body
    assert "37" in verdict.body


def test_runtime_mismatch_overrides_model_ok() -> None:
    analysis = {
        "runtime": {
            "configured": True,
            "passed": False,
            "cases": [
                {
                    "name": "twelve",
                    "passed": False,
                    "failures": ["exit code 143 did not match 144"],
                }
            ],
        }
    }

    verdict = apply_deterministic_gate(_ok_verdict(), analysis)

    assert not verdict.passed
    assert verdict.code == "runtime-mismatch"
    assert verdict.reason == "native runtime cases failed: twelve"
    assert "exit code 143 did not match 144" in verdict.body
    assert "correct lowering or code generation" in verdict.body


def test_native_budget_overrun_overrides_model_ok() -> None:
    analysis = {
        "runtime": {"configured": True, "passed": True, "cases": []},
        "native_budget": {
            "configured": True,
            "passed": False,
            "failures": [
                "function 'main' instructions 5 exceeds maximum 2",
                "function 'main' direct calls 1 exceeds maximum 0",
            ],
        },
    }

    verdict = apply_deterministic_gate(_ok_verdict(), analysis)

    assert not verdict.passed
    assert verdict.code == "native-budget-exceeded"
    assert verdict.reason == (
        "native optimization budget exceeded: "
        "function 'main' instructions 5 exceeds maximum 2"
    )
    assert "direct calls 1 exceeds maximum 0" in verdict.body
    assert "explicit final-code quality contract" in verdict.body


def test_deterministic_gate_preserves_model_failure() -> None:
    model_verdict = AuditVerdict(
        status="FAILED",
        code="incorrect-lowering",
        reason="wrong return value",
        body="Evidence.",
    )

    assert apply_deterministic_gate(model_verdict, {}) is model_verdict


def test_deterministic_gate_accepts_reachable_program_code() -> None:
    model_verdict = _ok_verdict()
    analysis = {
        "runtime": {"configured": True, "passed": True, "cases": []},
        "native_budget": {"configured": True, "passed": True, "failures": []},
        "native": {
            "reachability_complete": True,
            "unreachable_program_functions": [],
            "unreachable_program_instructions": 0,
        },
    }

    assert apply_deterministic_gate(model_verdict, analysis) is model_verdict
