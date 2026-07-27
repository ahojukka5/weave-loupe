"""Tests for gated LLM audit orchestration."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from weave_loupe.commands.audit import run_audit
from weave_loupe.llm import LlmConfig


def _config() -> LlmConfig:
    return LlmConfig(
        endpoint="https://example.test/v1",
        api_key="secret",
        model="model",
        max_tokens=64,
    )


def test_audit_writes_report_only_for_ok_verdict(
    tmp_path: Path, source_file: Path, fake_weavec: Path, capsys
) -> None:
    report_path = tmp_path / "demo.md"
    wir_path = tmp_path / "out.wir"
    with (
        patch("weave_loupe.commands.audit.load_config", return_value=_config()),
        patch(
            "weave_loupe.commands.audit.chat_completion",
            return_value="OK\n## Summary\nNo blocking defect found.",
        ) as chat,
    ):
        code = run_audit(
            weave_files=[source_file],
            model="model",
            weavec=fake_weavec,
            llvm_out=tmp_path / "out.ll",
            wir_out=wir_path,
            report_out=report_path,
            max_tokens=64,
            verbose=False,
        )
    assert code == 0
    prompt = chat.call_args.args[1]
    assert "Complete analysis JSON" in prompt
    assert "Optimized LLVM IR" in prompt
    assert "Linked executable disassembly" in prompt
    assert "=== WIR ===" not in prompt
    assert "typed-integer-wrap" in prompt
    assert "identity_adds" in prompt
    assert wir_path.read_text(encoding="utf-8")
    report = report_path.read_text(encoding="utf-8")
    assert "**Status:** OK" in report
    assert "Audit timestamp (UTC)" in report
    assert "weavec binary SHA-256" in report
    assert "Machine and running conditions" in report
    assert capsys.readouterr().out == report


def test_audit_failure_returns_nonzero_and_removes_stale_report(
    tmp_path: Path, source_file: Path, fake_weavec: Path, capsys
) -> None:
    report_path = tmp_path / "demo.md"
    report_path.write_text("stale", encoding="utf-8")
    with (
        patch("weave_loupe.commands.audit.load_config", return_value=_config()),
        patch(
            "weave_loupe.commands.audit.chat_completion",
            return_value=(
                "FAILED: memory-leakage: allocation is not released\n"
                "## Blocking findings\nConcrete evidence."
            ),
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
    captured = capsys.readouterr()
    assert code == 2
    assert not report_path.exists()
    assert "**Status:** FAILED" in captured.out
    assert "FAILED [memory-leakage]" in captured.err


def test_audit_rejects_malformed_verdict(
    tmp_path: Path, source_file: Path, fake_weavec: Path, capsys
) -> None:
    report_path = tmp_path / "demo.md"
    with (
        patch("weave_loupe.commands.audit.load_config", return_value=_config()),
        patch(
            "weave_loupe.commands.audit.chat_completion",
            return_value="Looks fine to me.",
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
    assert code == 1
    assert not report_path.exists()
    assert "first line must be exactly" in capsys.readouterr().err


def test_audit_verbose_embeds_focused_evidence(
    source_file: Path, fake_weavec: Path, capsys
) -> None:
    with (
        patch("weave_loupe.commands.audit.load_config", return_value=_config()),
        patch(
            "weave_loupe.commands.audit.chat_completion",
            return_value="OK\n## Summary\nNo defect.",
        ),
    ):
        code = run_audit(
            weave_files=[source_file],
            model="model",
            weavec=fake_weavec,
            llvm_out=None,
            wir_out=None,
            report_out=None,
            max_tokens=64,
            verbose=True,
        )
    captured = capsys.readouterr()
    assert code == 0
    assert "## Complete compiler evidence" in captured.out
    assert "### Weave source" in captured.out
    assert "### WIR" not in captured.out
    assert "### Raw LLVM IR" in captured.out
    assert "### Optimized LLVM IR" in captured.out
    assert "### Target assembly" in captured.out
    assert "### Linked executable disassembly" in captured.out
    assert "### Deterministic analysis" in captured.out
    assert captured.err == ""
