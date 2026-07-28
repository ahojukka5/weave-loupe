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


def test_audit_parser_supports_multiple_sources_and_report_output() -> None:
    args = build_parser().parse_args(
        ["audit", "a.weave", "b.weave", "--report-out", "a.md"]
    )
    assert args.weave_files == [Path("a.weave"), Path("b.weave")]
    assert args.report_out == Path("a.md")


def test_verify_report_parser_supports_explicit_identity_inputs() -> None:
    args = build_parser().parse_args(
        [
            "verify-report",
            "a.md",
            "--source",
            "source.weave",
            "--weavec",
            "bin/weavec",
            "--max-age-days",
            "14",
            "--json-out",
            "validity.json",
        ]
    )
    assert args.command == "verify-report"
    assert args.report == Path("a.md")
    assert args.source == Path("source.weave")
    assert args.weavec == Path("bin/weavec")
    assert args.max_age_days == 14
    assert args.json_out == Path("validity.json")


def test_main_dispatches_capture() -> None:
    with patch("weave_loupe.cli.run_capture", return_value=0) as command:
        assert main(["capture", "a.weave", "-o", "a.loupe"]) == 0
    command.assert_called_once()


def test_main_dispatches_report_verification() -> None:
    with patch("weave_loupe.cli.run_verify_report", return_value=2) as command:
        result = main(
            [
                "verify-report",
                "a.md",
                "--source",
                "a.weave",
                "--weavec",
                "weavec",
            ]
        )
    assert result == 2
    command.assert_called_once_with(
        report=Path("a.md"),
        source=Path("a.weave"),
        weavec=Path("weavec"),
        max_age_days=30,
        json_out=None,
    )
