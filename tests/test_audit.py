"""Tests for enriched LLM audit orchestration."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from weave_loupe.commands.audit import run_audit
from weave_loupe.llm import LlmConfig


def test_audit_passes_trace_and_metrics(
    tmp_path: Path, source_file: Path, fake_weavec: Path, capsys
) -> None:
    config = LlmConfig(
        endpoint="https://example.test/v1",
        api_key="secret",
        model="model",
        max_tokens=64,
    )
    with (
        patch("weave_loupe.commands.audit.load_config", return_value=config),
        patch(
            "weave_loupe.commands.audit.chat_completion", return_value="report"
        ) as chat,
    ):
        code = run_audit(
            weave_files=[source_file],
            model="model",
            weavec=fake_weavec,
            llvm_out=tmp_path / "out.ll",
            wir_out=tmp_path / "out.wir",
            max_tokens=64,
            verbose=False,
        )
    assert code == 0
    prompt = chat.call_args.args[1]
    assert "Trace summary JSON" in prompt
    assert "typed-integer-wrap" in prompt
    assert "identity_adds" in prompt
    assert capsys.readouterr().out == "report\n"


def test_audit_verbose_prints_prompt(
    source_file: Path, fake_weavec: Path, capsys
) -> None:
    config = LlmConfig(
        endpoint="https://example.test/v1", api_key="secret", model="model"
    )
    with (
        patch("weave_loupe.commands.audit.load_config", return_value=config),
        patch("weave_loupe.commands.audit.chat_completion", return_value="ok"),
    ):
        code = run_audit(
            weave_files=[source_file],
            model="model",
            weavec=fake_weavec,
            llvm_out=None,
            wir_out=None,
            max_tokens=64,
            verbose=True,
        )
    assert code == 0
    assert "loupe audit prompt begin" in capsys.readouterr().err
