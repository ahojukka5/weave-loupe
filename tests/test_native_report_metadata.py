"""Audit-report coverage for architecture-aware native metadata."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from weave_loupe.commands.audit import run_audit
from weave_loupe.llm import LlmConfig, LlmResponse


def test_nonverbose_report_records_native_parser_identity(
    tmp_path: Path,
    source_file: Path,
    fake_weavec: Path,
) -> None:
    report_path = tmp_path / "native-metadata.md"
    config = LlmConfig(
        endpoint="https://example.test/v1",
        api_key="secret",
        model="model",
        max_tokens=64,
    )
    response = LlmResponse(
        content="OK\n## Summary\nNative metadata is present.",
        requested_model="model",
        endpoint="https://example.test/v1",
        max_tokens=64,
        temperature=0.0,
        prompt_sha256="c" * 64,
        request_sha256="d" * 64,
        provider_model="model",
        response_id="response",
        system_fingerprint=None,
        finish_reason="stop",
        created=None,
        prompt_tokens=None,
        completion_tokens=None,
        total_tokens=None,
    )

    with (
        patch("weave_loupe.commands.audit.load_config", return_value=config),
        patch(
            "weave_loupe.commands.audit.chat_completion",
            return_value=response,
        ),
    ):
        code = run_audit(
            weave_files=[source_file],
            model="model",
            weavec=fake_weavec,
            llvm_out=None,
            wir_out=None,
            report_out=report_path,
            max_tokens=64,
            verbose=False,
        )

    report = report_path.read_text(encoding="utf-8")
    assert code == 0
    assert "Native analysis supported:** `True`" in report
    assert "Native target architecture:** `x86_64`" in report
    assert "Native object format:** `unknown`" in report
    assert "Native disassembler:** `unknown`" in report
    assert "Native disassembler version:** `unavailable`" in report
    assert "Native parser format:** `weave-loupe-native-disassembly-v1`" in report
    assert "Native analysis failure:** `unavailable`" in report
