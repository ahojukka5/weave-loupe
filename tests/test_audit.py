"""Tests for gated LLM audit orchestration."""

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


def _response(content: str) -> LlmResponse:
    return LlmResponse(
        content=content,
        requested_model="model",
        endpoint="https://example.test/v1",
        provider_model="model-20260728",
        response_id="chatcmpl-test",
        system_fingerprint="fp_test",
    )


def _write_runtime_cases(source: Path, *, exit_code: int, actual: int = 1) -> None:
    source.with_suffix(".audit.json").write_text(
        json.dumps(
            {
                "format": "weave-loupe-runtime-cases-v1",
                "cases": [
                    {
                        "name": "native-result",
                        "env": {"LOUPE_EXIT": str(actual)},
                        "expect": {
                            "exit_code": exit_code,
                            "stdout": "",
                            "stderr": "",
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
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
            return_value=_response("OK\n## Summary\nNo blocking defect found."),
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
    assert "WIR review projection" in prompt
    assert "(fn main (params) (returns i32)" in prompt
    assert "weavec-source-span-v1" not in prompt
    assert "Optimized LLVM IR" in prompt
    assert "Linked executable disassembly" in prompt
    assert "typed-integer-wrap" in prompt
    assert "identity_adds" in prompt
    assert '"configured": false' in prompt
    assert '"endpoint": "https://example.test/v1"' in prompt
    raw_wir = wir_path.read_text(encoding="utf-8")
    assert "weavec-source-span-v1" in raw_wir
    report = report_path.read_text(encoding="utf-8")
    assert "**Status:** OK" in report
    assert "Audit timestamp (UTC)" in report
    assert "weavec binary SHA-256" in report
    assert "weavec v0.3.0+git.test123" in report
    assert "weavec build kind:** `development`" in report
    assert "LLM endpoint:** `https://example.test/v1`" in report
    assert "LLM model:** `model`" in report
    assert "Provider-reported model:** `model-20260728`" in report
    assert "Provider response ID:** `chatcmpl-test`" in report
    assert "Provider system fingerprint:** `fp_test`" in report
    assert "Machine and running conditions" in report
    assert capsys.readouterr().out == report


def test_audit_executes_passing_runtime_matrix(
    tmp_path: Path, source_file: Path, fake_weavec: Path, capsys
) -> None:
    _write_runtime_cases(source_file, exit_code=7, actual=7)
    report_path = tmp_path / "demo.md"
    with (
        patch("weave_loupe.commands.audit.load_config", return_value=_config()),
        patch(
            "weave_loupe.commands.audit.chat_completion",
            return_value=_response("OK\n## Summary\nNative execution agrees."),
        ) as chat,
    ):
        code = run_audit(
            weave_files=[source_file],
            model="model",
            weavec=fake_weavec,
            llvm_out=None,
            wir_out=None,
            report_out=report_path,
            max_tokens=64,
            verbose=True,
        )

    assert code == 0
    prompt = chat.call_args.args[1]
    assert '"configured": true' in prompt
    assert '"exit_code": 7' in prompt
    report = report_path.read_text(encoding="utf-8")
    assert "### Runtime execution matrix" in report
    assert '"name": "native-result"' in report
    assert '"passed": true' in report
    assert capsys.readouterr().err == ""


def test_runtime_mismatch_overrides_model_ok_and_removes_report(
    tmp_path: Path, source_file: Path, fake_weavec: Path, capsys
) -> None:
    _write_runtime_cases(source_file, exit_code=2, actual=1)
    report_path = tmp_path / "demo.md"
    report_path.write_text("stale", encoding="utf-8")
    with (
        patch("weave_loupe.commands.audit.load_config", return_value=_config()),
        patch(
            "weave_loupe.commands.audit.chat_completion",
            return_value=_response("OK\n## Summary\nStatic evidence looks valid."),
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
            verbose=True,
        )

    captured = capsys.readouterr()
    assert code == 2
    assert not report_path.exists()
    assert "**Status:** FAILED" in captured.out
    assert "runtime-mismatch" in captured.out
    assert "exit code 1 did not match 2" in captured.out
    assert "FAILED [runtime-mismatch]" in captured.err


def test_audit_failure_returns_nonzero_and_removes_stale_report(
    tmp_path: Path, source_file: Path, fake_weavec: Path, capsys
) -> None:
    report_path = tmp_path / "demo.md"
    report_path.write_text("stale", encoding="utf-8")
    with (
        patch("weave_loupe.commands.audit.load_config", return_value=_config()),
        patch(
            "weave_loupe.commands.audit.chat_completion",
            return_value=_response(
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
            return_value=_response("Looks fine to me."),
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


def test_audit_verbose_embeds_cleaned_wir(
    source_file: Path, fake_weavec: Path, capsys
) -> None:
    with (
        patch("weave_loupe.commands.audit.load_config", return_value=_config()),
        patch(
            "weave_loupe.commands.audit.chat_completion",
            return_value=_response("OK\n## Summary\nNo defect."),
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
    assert "### WIR (provenance comments hidden)" in captured.out
    assert "(fn main (params) (returns i32)" in captured.out
    assert "weavec-source-span-v1" not in captured.out
    assert "### Raw LLVM IR" in captured.out
    assert "### Optimized LLVM IR" in captured.out
    assert "### Target assembly" in captured.out
    assert "### Linked executable disassembly" in captured.out
    assert "### Runtime execution matrix" in captured.out
    assert "### Deterministic analysis" in captured.out
    assert captured.err == ""
