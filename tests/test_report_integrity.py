"""Tests for deterministic generated report content seals."""

from __future__ import annotations

from weave_loupe.report_integrity import (
    REPORT_CONTENT_PREFIX,
    inspect_report_integrity,
    seal_audit_report,
)


def _report() -> str:
    return (
        "# Weave Loupe Audit Report\n\n"
        "## Reproducibility\n\n"
        "- **Audit timestamp (UTC):** `2026-07-28T00:00:00+00:00`\n\n"
        "## Audited inputs\n\n"
        "- Source `demo.weave` — SHA-256 `" + "a" * 64 + "`\n\n"
        "## LLM review\n\n"
        "No defect.\n"
    )


def test_seal_is_valid_and_idempotent() -> None:
    sealed = seal_audit_report(_report())

    integrity = inspect_report_integrity(sealed)

    assert integrity.valid
    assert integrity.seal_count == 1
    assert integrity.recorded_sha256 == integrity.calculated_sha256
    assert seal_audit_report(sealed) == sealed
    assert sealed.endswith("\n")


def test_content_change_invalidates_seal() -> None:
    sealed = seal_audit_report(_report())
    changed = sealed.replace("No defect.", "Edited verdict narrative.")

    integrity = inspect_report_integrity(changed)

    assert not integrity.valid
    assert integrity.recorded_sha256 != integrity.calculated_sha256


def test_duplicate_envelope_seals_are_rejected() -> None:
    sealed = seal_audit_report(_report())
    duplicate = sealed.replace(
        "## Reproducibility\n\n",
        f"## Reproducibility\n\n{REPORT_CONTENT_PREFIX}{'0' * 64}`\n",
    )

    integrity = inspect_report_integrity(duplicate)

    assert not integrity.valid
    assert integrity.seal_count == 2


def test_model_prose_cannot_spoof_the_envelope_seal() -> None:
    report = _report().replace(
        "No defect.\n",
        f"No defect.\n\n{REPORT_CONTENT_PREFIX}{'0' * 64}`\n",
    )
    sealed = seal_audit_report(report)

    integrity = inspect_report_integrity(sealed)

    assert integrity.valid
    assert integrity.seal_count == 1
    assert f"{REPORT_CONTENT_PREFIX}{'0' * 64}`" in sealed
    changed = sealed.replace("No defect.", "Changed review.")
    assert not inspect_report_integrity(changed).valid


def test_sealing_preserves_absence_of_final_newline() -> None:
    report = _report().removesuffix("\n")

    sealed = seal_audit_report(report)

    assert not sealed.endswith("\n")
    assert inspect_report_integrity(sealed).valid
