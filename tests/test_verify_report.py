"""Tests for the public deterministic report verifier."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from weave_loupe.auditor_identity import identify_auditor, sha256_file
from weave_loupe.commands.verify_report import run_verify_report
from weave_loupe.report_integrity import seal_audit_report

_MODEL = "z-ai/glm-5.2"
_ENDPOINT = "https://example.test/v1"
_MAX_TOKENS = 4096
_PROMPT_SHA256 = "c" * 64
_REQUEST_SHA256 = "d" * 64


def _write_report(
    source: Path,
    compiler: Path,
    *,
    model: str = _MODEL,
    endpoint: str = _ENDPOINT,
    max_tokens: int = _MAX_TOKENS,
) -> Path:
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
        f"- **LLM endpoint:** `{endpoint}`\n"
        f"- **LLM model:** `{model}`\n"
        f"- **LLM max tokens:** `{max_tokens}`\n"
        "- **LLM temperature:** `0.0`\n"
        f"- **LLM prompt SHA-256:** `{_PROMPT_SHA256}`\n"
        f"- **LLM request SHA-256:** `{_REQUEST_SHA256}`\n"
        "- **Provider-reported model:** `z-ai/glm-5.2-20260728`\n"
        "- **Provider response ID:** `chatcmpl-test`\n"
        "- **Provider system fingerprint:** `fp_test`\n"
        "- **Provider finish reason:** `stop`\n"
        "- **Provider created (Unix):** `1785236400`\n"
        "- **Provider prompt tokens:** `1000`\n"
        "- **Provider completion tokens:** `200`\n"
        "- **Provider total tokens:** `1200`\n\n"
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
        endpoint=_ENDPOINT,
        max_tokens=_MAX_TOKENS,
        max_age_days=30,
        json_out=json_out,
    )

    captured = capsys.readouterr()
    document = json.loads(json_out.read_text(encoding="utf-8"))
    identity = document["report_identity"]
    assert code == 0
    assert captured.out == f"VALID: {report}\n"
    assert captured.err == ""
    assert document["format"] == "weave-loupe-report-verification-v1"
    assert document["valid"] is True
    assert document["reasons"] == []
    assert document["current_compiler"]["binary_sha256"] == sha256_file(fake_weavec)
    assert document["current_auditor"]["sha256"] == identify_auditor().sha256
    assert document["current_model"] == _MODEL
    assert document["current_endpoint"] == _ENDPOINT
    assert document["current_max_tokens"] == _MAX_TOKENS
    assert identity["model"] == _MODEL
    assert identity["endpoint"] == _ENDPOINT
    assert identity["max_tokens"] == _MAX_TOKENS
    assert identity["temperature"] == 0.0
    assert identity["prompt_sha256"] == _PROMPT_SHA256
    assert identity["request_sha256"] == _REQUEST_SHA256
    assert identity["provider_model"] == "z-ai/glm-5.2-20260728"
    assert identity["response_id"] == "chatcmpl-test"
    assert identity["system_fingerprint"] == "fp_test"
    assert identity["finish_reason"] == "stop"
    assert identity["created"] == 1785236400
    assert identity["prompt_tokens"] == 1000
    assert identity["completion_tokens"] == 200
    assert identity["total_tokens"] == 1200
    assert len(identity["report_content_sha256"]) == 64


def test_verify_report_lists_all_stale_reasons(
    source_file: Path,
    fake_weavec: Path,
    capsys,
) -> None:
    report = _write_report(
        source_file,
        fake_weavec,
        model="old-model",
        endpoint="https://old.example.test/v1",
        max_tokens=2048,
    )
    source_file.write_text("changed\n", encoding="utf-8")

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
    assert code == 2
    assert captured.out.startswith(f"STALE: {report}\n")
    assert "- source content changed since audit\n" in captured.out
    assert f"- LLM model changed from old-model to {_MODEL}\n" in captured.out
    assert (
        "- LLM endpoint changed from https://old.example.test/v1 "
        "to https://example.test/v1\n"
    ) in captured.out
    assert "- LLM max tokens changed from 2048 to 4096\n" in captured.out
    assert captured.err == ""


def test_verify_report_normalizes_loopback_endpoint(
    source_file: Path,
    fake_weavec: Path,
    capsys,
) -> None:
    identity = "http://localhost:8000/v1"
    report = _write_report(source_file, fake_weavec, endpoint=identity)

    code = run_verify_report(
        report=report,
        source=None,
        weavec=fake_weavec,
        model=_MODEL,
        endpoint=("http://user:secret@LOCALHOST:8000/v1/?token=hidden#fragment"),
        max_tokens=_MAX_TOKENS,
        max_age_days=30,
        json_out=None,
    )

    captured = capsys.readouterr()
    assert code == 0
    assert captured.out == f"VALID: {report}\n"
    assert captured.err == ""


def test_verify_report_rejects_remote_http_without_exposing_secrets(
    source_file: Path,
    fake_weavec: Path,
    capsys,
) -> None:
    report = _write_report(
        source_file,
        fake_weavec,
        endpoint="http://example.test/v1",
    )

    code = run_verify_report(
        report=report,
        source=None,
        weavec=fake_weavec,
        model=_MODEL,
        endpoint=(
            "http://private-user:private-password@example.test/v1"
            "?token=private-token#private-fragment"
        ),
        max_tokens=_MAX_TOKENS,
        max_age_days=30,
        json_out=None,
    )

    captured = capsys.readouterr()
    assert code == 1
    assert captured.out == ""
    assert "restricted to loopback" in captured.err
    assert "private" not in captured.err


def test_verify_report_accepts_explicit_remote_http_override(
    source_file: Path,
    fake_weavec: Path,
    capsys,
) -> None:
    identity = "http://example.test/v1"
    report = _write_report(source_file, fake_weavec, endpoint=identity)

    code = run_verify_report(
        report=report,
        source=None,
        weavec=fake_weavec,
        model=_MODEL,
        endpoint="http://user:secret@EXAMPLE.test:80/v1/?token=hidden",
        max_tokens=_MAX_TOKENS,
        max_age_days=30,
        json_out=None,
        allow_unsafe_http=True,
    )

    captured = capsys.readouterr()
    assert code == 0
    assert captured.out == f"VALID: {report}\n"
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
        endpoint=_ENDPOINT,
        max_tokens=_MAX_TOKENS,
        max_age_days=30,
        json_out=None,
    )

    captured = capsys.readouterr()
    assert code == 2
    assert captured.out.startswith(f"STALE: {report}\n")
    assert "- report content changed since audit\n" in captured.out
    assert captured.err == ""


def test_verify_report_can_skip_reviewer_request_comparisons(
    source_file: Path,
    fake_weavec: Path,
    capsys,
) -> None:
    report = _write_report(
        source_file,
        fake_weavec,
        model="archived-model",
        endpoint="https://archived.example.test/v1",
        max_tokens=1024,
    )

    code = run_verify_report(
        report=report,
        source=None,
        weavec=fake_weavec,
        model=None,
        endpoint=None,
        max_tokens=None,
        max_age_days=30,
        json_out=None,
    )

    captured = capsys.readouterr()
    assert code == 0
    assert captured.out == f"VALID: {report}\n"


def test_verify_report_rejects_invalid_maximum_tokens(
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
        endpoint=_ENDPOINT,
        max_tokens=0,
        max_age_days=30,
        json_out=None,
    )

    captured = capsys.readouterr()
    assert code == 1
    assert captured.out == ""
    assert "max_tokens must be positive" in captured.err


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
        endpoint=_ENDPOINT,
        max_tokens=_MAX_TOKENS,
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
        endpoint=_ENDPOINT,
        max_tokens=_MAX_TOKENS,
        max_age_days=30,
        json_out=None,
    )

    captured = capsys.readouterr()
    assert code == 1
    assert captured.out == ""
    assert f"audit report not found: {report}" in captured.err
