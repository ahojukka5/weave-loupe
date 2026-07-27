"""Tests for the strict audit verdict protocol."""

from __future__ import annotations

import pytest

from weave_loupe.audit_result import AuditProtocolError, parse_audit_response


def test_parse_ok() -> None:
    verdict = parse_audit_response("OK\n## Summary\nGood.\n")
    assert verdict.passed
    assert verdict.code is None
    assert verdict.body == "## Summary\nGood."


def test_parse_failed() -> None:
    verdict = parse_audit_response(
        "FAILED: incorrect-lowering: return value changes\nEvidence"
    )
    assert not verdict.passed
    assert verdict.code == "incorrect-lowering"
    assert verdict.reason == "return value changes"


@pytest.mark.parametrize(
    "response",
    [
        "",
        "PASS",
        "FAILED",
        "FAILED: Bad_Code: reason",
        "```\nOK\n```",
    ],
)
def test_reject_invalid_protocol(response: str) -> None:
    with pytest.raises(AuditProtocolError):
        parse_audit_response(response)
