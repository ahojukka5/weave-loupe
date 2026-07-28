"""Tests for the public deterministic report verifier."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from weave_loupe.auditor_identity import identify_auditor, sha256_file
from weave_loupe.commands.verify_report import run_verify_report
from weave_loupe.report_integrity import seal_audit_report

_MODEL = "z-ai/glm-5.2"


def _write_report(source: Path, compiler: Path, *, model: str = _MODEL) -> Path:
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
        f"- **LLM model:** `{model}`\n\n"
        "## Audited inputs\n\n"
        f"- Source `{source}` — SHA-256 `{sha256_file(source)}`\n\n"
        "## Captured evidence\n"
    )
    report.write_text(seal_audit_report(content), encoding="utf-8")
    return report


def test_verify_report_accepts_exact_current_identity(
    tmp_path: Path,
    source_file: Path,
    fake_weavec: Path,
    capsys,
) -> None:
    report = _write_report(source_file, fake_weavec)
    json_out = tmp_path / "verification.json"

    code = run_verify_report(
        report=report,
        source=None,
        weavec=fake_weavec,
        model=_MODEL,
        max_age_days=30,
        json_out=json_out,
    )

    captured = capsys.readouterr()
    document = json.loads(json_out.read_text(encoding="utf-8"))
    assert code == 0
    assert captured.out == f"VALID: {report}\n"
    assert captured.err == ""
    assert document["format"] == "weave-loupe-report-verification-v1"
    assert document["valid"] is True
    assert document["reasons"] == []
    assert document["current_compiler"]["binary_sha256"] == sha256_file(fake_weavec)
    assert document["current_auditor"]["sha256"] == identify_auditor().sha256
    assert document["current_model"] == _MODEL
    assert document["report_identity"]["model"] == _MODEL
    assert len(document["report_identity"]["report_content_sha256"]) == 64


def test_verify_report_lists_all_stale_reasons(
    source_file: Path,
    fake_weavec: Path,
    capsys,
) -> None:
    report = _write_report(source_file, fake_weavec, model="old-model")
    source_file.write_text("changed\n", encoding="utf-8")

    code = run_verify_report(
        report=report,
        source=None,
        weavec=fake_weavec,
        model=_MODEL,
        max_age_days=30,
        json_out=None,
    )

    captured = capsys.readouterr()
    assert code == 2
    assert captured.out.startswith(f"STALE: {report}\n")
    assert "- source content changed since audit\n" in captured.out
    assert f"- LLM model changed from old-model to {_MODEL}\n" in captured.out
    assert captured.err == ""


def test_verify_report_rejects_changed_markdown_content(
    source_file: Path,
    fake_weavec: Path,
    capsys,
) -> None:
    report = _write_report(source_file, fake_weavec)
    report.write_text(
        report.read_text(encoding="utf-8") + "\nManual unsealed edit.\n",
        encoding="utf-8",
    )

    code = run_verify_report(
        report=report,
        source=None,
        weavec=fake_weavec,
        model=_MODEL,
        max_age_days=30,
        json_out=None,
    )

    captured = capsys.readouterr()
    assert code == 2
    assert captured.out.startswith(f"STALE: {report}\n")
    assert "- report content changed since audit\n" in captured.out
    assert captured.err == ""


def test_verify_report_can_skip_model_comparison(
    source_file: Path,
    fake_weavec: Path,
    capsys,
) -> None:
    report = _write_report(source_file, fake_weavec, model="archived-model")

    code = run_verify_report(
        report=report,
        source=None,
        weavec=fake_weavec,
        model=None,
        max_age_days=30,
        json_out=None,
    )

    captured = capsys.readouterr()
    assert code == 0
    assert captured.out == f"VALID: {report}\n"


def test_verify_report_rejects_invalid_maximum_age(
    source_file: Path,
    fake_weavec: Path,
    capsys,
) -> None:
    report = _write_report(source_file, fake_weavec)

    code = run_verify_report(
        report=report,
        source=None,
        weavec=fake_weavec,
        model=_MODEL,
        max_age_days=0,
        json_out=None,
    )

    captured = capsys.readouterr()
    assert code == 1
    assert captured.out == ""
    assert "max_age_days must be positive" in captured.err


def test_verify_report_rejects_missing_report(
    tmp_path: Path,
    fake_weavec: Path,
    capsys,
) -> None:
    report = tmp_path / "missing.md"

    code = run_verify_report(
        report=report,
        source=None,
        weavec=fake_weavec,
        model=_MODEL,
        max_age_days=30,
        json_out=None,
    )

    captured = capsys.readouterr()
    assert code == 1
    assert captured.out == ""
    assert f"audit report not found: {report}" in captured.err
