"""Tests for the loupe CLI parser and entrypoint."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from weave_loupe.cli import build_parser, main


def test_build_parser_audit_defaults() -> None:
    parser = build_parser()
    args = parser.parse_args(["audit", "demo.weave"])
    assert args.command == "audit"
    assert args.weave_file == Path("demo.weave")
    assert args.model == "z-ai/glm-5.2"
    assert args.weavec is None
    assert args.wir_out is None
    assert args.llvm_out is None
    assert args.max_tokens == 4096
    assert args.verbose is False


def test_build_parser_audit_flags() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "audit",
            "demo.weave",
            "--model",
            "test-model",
            "--weavec",
            "/bin/weavec",
            "--wir-out",
            "out.wir",
            "--llvm-out",
            "out.ll",
            "--max-tokens",
            "128",
            "--verbose",
        ]
    )
    assert args.model == "test-model"
    assert args.weavec == Path("/bin/weavec")
    assert args.wir_out == Path("out.wir")
    assert args.llvm_out == Path("out.ll")
    assert args.max_tokens == 128
    assert args.verbose is True


def test_main_dispatches_audit() -> None:
    with patch("weave_loupe.cli.run_audit", return_value=0) as audit:
        code = main(["audit", "demo.weave", "-v"])
    assert code == 0
    audit.assert_called_once()
    kwargs = audit.call_args.kwargs
    assert kwargs["weave_file"] == Path("demo.weave")
    assert kwargs["verbose"] is True
