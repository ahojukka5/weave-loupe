"""Verifier coverage for the shared unsafe HTTP environment policy."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from weave_loupe.auditor_identity import identify_auditor, sha256_file
from weave_loupe.commands.verify_report import run_verify_report
from weave_loupe.report_integrity import seal_audit_report

_ENDPOINT = "http://example.test/v1"
_MODEL = "model"
_MAX_TOKENS = 4096


def _write_report(source: Path, compiler: Path) -> Path:
    report = source.with_suffix(".md")
    timestamp = datetime.now(UTC).replace(microsecond=0).isoformat()
    content = (
        "# Weave Loupe Audit Report\n\n"
        "## Reproducibility\n\n"
        f"- **Audit timestamp (UTC):** `{timestamp}`\n"
        f"- **Auditor content SHA-256:** `{identify_auditor().sha256}`\n"
        f"- **weavec binary SHA-256:** `{sha256_file(compiler)}`\n"
        "- **weavec version:** `weavec v0.3.0+git.test123`\n"
        "- **weavec version source:** `command`\n"
        f"- **LLM endpoint:** `{_ENDPOINT}`\n"
        f"- **LLM model:** `{_MODEL}`\n"
        f"- **LLM max tokens:** `{_MAX_TOKENS}`\n\n"
        "## Audited inputs\n\n"
        f"- Source `{source}` — SHA-256 `{sha256_file(source)}`\n\n"
        "## Captured evidence\n"
    )
    report.write_text(seal_audit_report(content), encoding="utf-8")
    return report


def test_verify_report_accepts_environment_remote_http_override(
    source_file: Path,
    fake_weavec: Path,
    monkeypatch,
    capsys,
) -> None:
    report = _write_report(source_file, fake_weavec)
    monkeypatch.setenv("WEAVE_LLM_ALLOW_UNSAFE_HTTP", "1")

    code = run_verify_report(
        report=report,
        source=None,
        weavec=fake_weavec,
        model=_MODEL,
        endpoint="http://user:secret@EXAMPLE.test:80/v1/?token=hidden",
        max_tokens=_MAX_TOKENS,
        max_age_days=30,
        json_out=None,
    )

    captured = capsys.readouterr()
    assert code == 0
    assert captured.out == f"VALID: {report}\n"
    assert captured.err == ""


def test_verify_report_rejects_invalid_http_policy_environment(
    source_file: Path,
    fake_weavec: Path,
    monkeypatch,
    capsys,
) -> None:
    report = _write_report(source_file, fake_weavec)
    monkeypatch.setenv("WEAVE_LLM_ALLOW_UNSAFE_HTTP", "sometimes")

    code = run_verify_report(
        report=report,
        source=None,
        weavec=fake_weavec,
        model=_MODEL,
        endpoint=_ENDPOINT,
        max_tokens=_MAX_TOKENS,
        max_age_days=30,
        json_out=None,
    )

    captured = capsys.readouterr()
    assert code == 1
    assert captured.out == ""
    assert "WEAVE_LLM_ALLOW_UNSAFE_HTTP must be one of" in captured.err
