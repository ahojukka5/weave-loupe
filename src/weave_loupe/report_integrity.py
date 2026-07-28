"""Deterministic integrity seals for generated Markdown audit reports."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

REPORT_CONTENT_PREFIX = "- **Report content SHA-256:** `"
_INPUTS_HEADING = "## Audited inputs"
_REPRODUCIBILITY_HEADING = "## Reproducibility"


@dataclass(frozen=True)
class ReportIntegrity:
    """Recorded and recomputed content identity for one report."""

    recorded_sha256: str | None
    calculated_sha256: str
    seal_count: int

    @property
    def valid(self) -> bool:
        return (
            self.seal_count == 1
            and self.recorded_sha256 is not None
            and self.recorded_sha256 == self.calculated_sha256
        )


def seal_audit_report(report: str) -> str:
    """Insert or replace the stable content seal in a generated report."""
    canonical, _, _ = _without_envelope_seals(report)
    digest = _sha256_text(canonical)
    lines = canonical.splitlines()
    try:
        heading = lines.index(_REPRODUCIBILITY_HEADING)
    except ValueError as exc:
        raise ValueError("report does not contain a Reproducibility section") from exc

    insertion = heading + 1
    if insertion < len(lines) and lines[insertion] == "":
        insertion += 1
    lines.insert(insertion, f"{REPORT_CONTENT_PREFIX}{digest}`")
    sealed = "\n".join(lines)
    if canonical.endswith("\n"):
        sealed += "\n"
    return sealed


def inspect_report_integrity(report: str) -> ReportIntegrity:
    """Read the stable seal and recompute the canonical report content hash."""
    canonical, recorded, count = _without_envelope_seals(report)
    return ReportIntegrity(
        recorded_sha256=recorded,
        calculated_sha256=_sha256_text(canonical),
        seal_count=count,
    )


def _without_envelope_seals(report: str) -> tuple[str, str | None, int]:
    lines = report.splitlines(keepends=True)
    kept: list[str] = []
    recorded: str | None = None
    count = 0
    in_envelope = True

    for line in lines:
        plain = line.rstrip("\r\n")
        if plain == _INPUTS_HEADING:
            in_envelope = False
        if in_envelope and plain.startswith(REPORT_CONTENT_PREFIX) and plain.endswith("`"):
            count += 1
            value = plain[len(REPORT_CONTENT_PREFIX) : -1]
            if len(value) == 64 and all(character in "0123456789abcdef" for character in value):
                if recorded is None:
                    recorded = value
            continue
        kept.append(line)

    return "".join(kept), recorded, count


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
