"""Tests for deterministic audit overrides."""

from __future__ import annotations

from weave_loupe.audit_result import AuditVerdict
from weave_loupe.deterministic_gate import apply_deterministic_gate


def test_dead_native_code_overrides_model_ok() -> None:
    model_verdict = AuditVerdict(
        status="OK",
        code=None,
        reason=None,
        body="## Summary\nThe model found no problem.",
    )
    analysis = {
        "native": {
            "reachability_complete": True,
            "unreachable_program_functions": ["fib", "weave_rt_contract_fail"],
            "unreachable_program_instructions": 37,
        }
    }

    verdict = apply_deterministic_gate(model_verdict, analysis)

    assert not verdict.passed
    assert verdict.code == "dead-native-code"
    assert verdict.reason == (
        "unreachable program-owned native functions remain: fib, weave_rt_contract_fail"
    )
    assert "The model returned `OK`" in verdict.body
    assert "37" in verdict.body


def test_deterministic_gate_preserves_model_failure() -> None:
    model_verdict = AuditVerdict(
        status="FAILED",
        code="incorrect-lowering",
        reason="wrong return value",
        body="Evidence.",
    )

    assert apply_deterministic_gate(model_verdict, {}) is model_verdict


def test_deterministic_gate_accepts_reachable_program_code() -> None:
    model_verdict = AuditVerdict(
        status="OK",
        code=None,
        reason=None,
        body="Verified.",
    )
    analysis = {
        "native": {
            "reachability_complete": True,
            "unreachable_program_functions": [],
            "unreachable_program_instructions": 0,
        }
    }

    assert apply_deterministic_gate(model_verdict, analysis) is model_verdict
