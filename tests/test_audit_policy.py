"""Tests for the versioned audit validity envelope."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from weave_loupe.audit_policy import (
    AUDIT_VALIDITY_FORMAT,
    DEFAULT_AUDIT_MAX_AGE_DAYS,
    build_audit_validity,
)
from weave_loupe.audit_result import AuditVerdict, render_audit_report


def test_validity_envelope_sets_exact_thirty_day_deadline() -> None:
    validity = build_audit_validity("2026-07-27T21:30:00+00:00")

    assert validity == {
        "format": AUDIT_VALIDITY_FORMAT,
        "max_age_days": DEFAULT_AUDIT_MAX_AGE_DAYS,
        "revalidate_after_utc": "2026-08-26T21:30:00+00:00",
        "invalidate_on_input_hash_change": True,
        "invalidate_on_development_version_change": True,
        "require_command_identity_when_available": True,
    }


def test_validity_envelope_normalizes_naive_timestamp_to_utc() -> None:
    validity = build_audit_validity("2026-07-27T21:30:00", max_age_days=1)

    assert validity["revalidate_after_utc"] == "2026-07-28T21:30:00+00:00"


def test_validity_envelope_rejects_nonpositive_lifetime() -> None:
    with pytest.raises(ValueError, match="must be positive"):
        build_audit_validity("2026-07-27T21:30:00+00:00", max_age_days=0)


def test_report_renders_human_visible_validity_scope() -> None:
    timestamp = datetime(2026, 7, 27, 21, 30, tzinfo=UTC).isoformat()
    metadata = {
        "timestamp_utc": timestamp,
        "validity": build_audit_validity(timestamp),
        "model": "model",
        "source_repository": {"sha": "source", "state": "clean"},
        "loupe_repository": {"sha": "loupe"},
        "weavec": {
            "sha256": "binary",
            "version": "weavec v0.3.0+git.abc",
            "development": True,
            "version_source": "command",
            "repository": {"sha": "compiler"},
        },
        "machine": {},
        "bundle": {"artifacts": {}},
        "github": {},
        "sources": [],
    }
    verdict = AuditVerdict(
        status="OK",
        code=None,
        reason=None,
        body="No defect.",
    )

    report = render_audit_report(
        verdict=verdict,
        metadata=metadata,
        model_response="OK\nNo defect.",
    )

    assert "Re-audit no later than (UTC):** `2026-08-26T21:30:00+00:00`" in report
    assert "Maximum audit age:** `30` days" in report
    assert (
        "Audited input invalidation:** `any source or runtime matrix hash change`"
        in report
    )
    assert (
        "Development compiler invalidation:** `any compiler version change`" in report
    )
    assert "Identity attestation upgrade:** `required" in report
