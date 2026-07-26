"""Tests for the loupe audit command orchestration."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from weave_loupe.commands.audit import run_audit
from weave_loupe.llm import LlmConfig
from weave_loupe.weavec import CompilationArtifacts, WeavecError


def test_run_audit_success_writes_artifacts_and_report(tmp_path: Path, capsys) -> None:
    source = tmp_path / "demo.weave"
    source.write_text("(program)", encoding="utf-8")
    wir_out = tmp_path / "out.wir"
    llvm_out = tmp_path / "out.ll"
    artifacts = CompilationArtifacts(
        weave_source="(program)",
        wir="(core-module)",
        llvm_ir="define i32 @main()",
    )
    config = LlmConfig(
        endpoint="https://example.test/v1",
        api_key="secret",
        model="z-ai/glm-5.2",
        max_tokens=64,
    )

    with (
        patch(
            "weave_loupe.commands.audit.compile_weave",
            return_value=artifacts,
        ) as compile_mock,
        patch(
            "weave_loupe.commands.audit.load_config",
            return_value=config,
        ) as load_mock,
        patch(
            "weave_loupe.commands.audit.chat_completion",
            return_value="# Weave Loupe Audit Report\nOK",
        ) as chat_mock,
    ):
        code = run_audit(
            weave_file=source,
            model="z-ai/glm-5.2",
            weavec=None,
            llvm_out=llvm_out,
            wir_out=wir_out,
            max_tokens=64,
            verbose=False,
        )

    assert code == 0
    assert wir_out.read_text(encoding="utf-8") == "(core-module)"
    assert llvm_out.read_text(encoding="utf-8") == "define i32 @main()"
    assert "# Weave Loupe Audit Report" in capsys.readouterr().out
    compile_mock.assert_called_once()
    load_mock.assert_called_once_with(model="z-ai/glm-5.2", max_tokens=64)
    prompt = chat_mock.call_args.args[1]
    assert "(program)" in prompt
    assert "(core-module)" in prompt
    assert "define i32 @main()" in prompt


def test_run_audit_verbose_prints_prompt(tmp_path: Path, capsys) -> None:
    source = tmp_path / "demo.weave"
    source.write_text("(program)", encoding="utf-8")
    artifacts = CompilationArtifacts(
        weave_source="(program)",
        wir="(core-module)",
        llvm_ir="define i32 @main()",
    )
    config = LlmConfig(
        endpoint="https://example.test/v1",
        api_key="secret",
        model="z-ai/glm-5.2",
    )

    with (
        patch(
            "weave_loupe.commands.audit.compile_weave",
            return_value=artifacts,
        ),
        patch("weave_loupe.commands.audit.load_config", return_value=config),
        patch(
            "weave_loupe.commands.audit.chat_completion",
            return_value="report",
        ),
    ):
        code = run_audit(
            weave_file=source,
            model="z-ai/glm-5.2",
            weavec=None,
            llvm_out=None,
            wir_out=None,
            max_tokens=16,
            verbose=True,
        )

    assert code == 0
    captured = capsys.readouterr()
    assert captured.out == "report\n"
    assert "=== loupe audit prompt begin ===" in captured.err
    assert "=== Weave source (.weave) ===" in captured.err
    assert "=== Intermediate representation (.wir) ===" in captured.err
    assert "=== Emitted LLVM IR (.ll) ===" in captured.err
    assert "=== loupe audit prompt end ===" in captured.err


def test_run_audit_returns_one_on_weavec_error(tmp_path: Path, capsys) -> None:
    source = tmp_path / "demo.weave"
    source.write_text("(program)", encoding="utf-8")

    with patch(
        "weave_loupe.commands.audit.compile_weave",
        side_effect=WeavecError("boom"),
    ):
        code = run_audit(
            weave_file=source,
            model="z-ai/glm-5.2",
            weavec=None,
            llvm_out=None,
            wir_out=None,
            max_tokens=16,
            verbose=False,
        )

    assert code == 1
    assert "loupe audit: boom" in capsys.readouterr().err
