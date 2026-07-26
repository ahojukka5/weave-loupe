"""Tests for CLI parsing and dispatch."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from weave_loupe.cli import build_parser, main


def test_capture_parser() -> None:
    args = build_parser().parse_args(["capture", "a.weave", "-o", "a.loupe"])
    assert args.command == "capture"
    assert args.weave_files == [Path("a.weave")]
    assert args.output == Path("a.loupe")


def test_report_parser() -> None:
    args = build_parser().parse_args(
        ["report", "a.loupe", "-o", "a.html", "--analysis-json", "a.json"]
    )
    assert args.command == "report"
    assert args.analysis_json == Path("a.json")


def test_diff_parser() -> None:
    args = build_parser().parse_args(["diff", "a.loupe", "b.loupe"])
    assert args.command == "diff"
    assert args.before == Path("a.loupe")


def test_audit_parser_supports_multiple_sources() -> None:
    args = build_parser().parse_args(["audit", "a.weave", "b.weave"])
    assert args.weave_files == [Path("a.weave"), Path("b.weave")]


def test_main_dispatches_capture() -> None:
    with patch("weave_loupe.cli.run_capture", return_value=0) as command:
        assert main(["capture", "a.weave", "-o", "a.loupe"]) == 0
    command.assert_called_once()
