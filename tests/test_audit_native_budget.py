"""Integration tests for native optimization budgets in ``loupe audit``."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from weave_loupe.commands.audit import run_audit
from weave_loupe.llm import LlmConfig, LlmResponse


def _config() -> LlmConfig:
    return LlmConfig(
        endpoint="https://example.test/v1",
        api_key="secret",
        model="model",
        max_tokens=64,
    )


def _response() -> LlmResponse:
    return LlmResponse(
        content="OK\n## Summary\nThe model found no blocking defect.",
        requested_model="model",
        endpoint="https://example.test/v1",
        max_tokens=64,
        temperature=0.0,
        prompt_sha256="c" * 64,
        request_sha256="d" * 64,
        provider_model="model",
        response_id="chatcmpl-test",
        system_fingerprint=None,
        finish_reason="stop",
        created=1785236400,
        prompt_tokens=100,
        completion_tokens=20,
        total_tokens=120,
    )


def _write_contract(source: Path, *, max_instructions: int) -> None:
    source.with_suffix(".audit.json").write_text(
        json.dumps(
            {
                "format": "weave-loupe-runtime-cases-v1",
                "native_budget": {
                    "format": "weave-loupe-native-budget-v1",
                    "max_program_owned_functions": 1,
                    "functions": {
                        "main": {
                            "max_instructions": max_instructions,
                            "max_padding_instructions": 0,
                            "max_direct_calls": 0,
                            "max_indirect_calls": 0,
                        }
                    },
                },
                "cases": [
                    {
                        "name": "native-result",
                        "expect": {"exit_code": 1},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def test_native_budget_overrun_blocks_passing_model_report(
    tmp_path: Path,
    source_file: Path,
    fake_weavec: Path,
    capsys,
) -> None:
    _write_contract(source_file, max_instructions=1)
    report = tmp_path / "demo.md"
    report.write_text("stale\n", encoding="utf-8")

    with (
        patch("weave_loupe.commands.audit.load_config", return_value=_config()),
        patch(
            "weave_loupe.commands.audit.chat_completion",
            return_value=_response(),
        ),
    ):
        code = run_audit(
            weave_files=[source_file],
            model="model",
            weavec=fake_weavec,
            llvm_out=None,
            wir_out=None,
            report_out=report,
            max_tokens=64,
            verbose=True,
        )

    captured = capsys.readouterr()
    assert code == 2
    assert not report.exists()
    assert "**Status:** FAILED" in captured.out
    assert "native-budget-exceeded" in captured.out
    assert "instructions 2 exceeds maximum 1" in captured.out
    assert "FAILED [native-budget-exceeded]" in captured.err


def test_passing_native_budget_is_embedded_in_verbose_report(
    tmp_path: Path,
    source_file: Path,
    fake_weavec: Path,
    capsys,
) -> None:
    _write_contract(source_file, max_instructions=2)
    report = tmp_path / "demo.md"

    with (
        patch("weave_loupe.commands.audit.load_config", return_value=_config()),
        patch(
            "weave_loupe.commands.audit.chat_completion",
            return_value=_response(),
        ),
    ):
        code = run_audit(
            weave_files=[source_file],
            model="model",
            weavec=fake_weavec,
            llvm_out=None,
            wir_out=None,
            report_out=report,
            max_tokens=64,
            verbose=True,
        )

    captured = capsys.readouterr()
    content = report.read_text(encoding="utf-8")
    assert code == 0
    assert "### Native optimization budget" in content
    assert '"configured": true' in content
    assert '"max_instructions": 2' in content
    assert '"instructions": 2' in content
    assert '"passed": true' in content
    assert captured.err == ""
