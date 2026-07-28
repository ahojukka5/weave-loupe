"""Versioned validity policy shared by audit reports and maintenance jobs."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

AUDIT_VALIDITY_FORMAT = "weave-loupe-audit-validity-v1"
DEFAULT_AUDIT_MAX_AGE_DAYS = 30


def build_audit_validity(
    timestamp_utc: str,
    *,
    max_age_days: int = DEFAULT_AUDIT_MAX_AGE_DAYS,
) -> dict[str, Any]:
    """Return the machine-readable invalidation envelope for one audit."""
    if max_age_days <= 0:
        raise ValueError("max_age_days must be positive")
    timestamp = _parse_timestamp(timestamp_utc)
    revalidate_after = timestamp + timedelta(days=max_age_days)
    return {
        "format": AUDIT_VALIDITY_FORMAT,
        "max_age_days": max_age_days,
        "revalidate_after_utc": revalidate_after.replace(microsecond=0).isoformat(),
        "invalidate_on_development_version_change": True,
        "require_command_identity_when_available": True,
    }


def _parse_timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)
