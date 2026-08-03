"""Tests for CLI parsing and dispatch."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from weave_loupe.cli import build_parser, main


def test_capture_parser() -> None:
    args = build_parser().parse_args(
        [
            "capture",
            "a.weave",
            "-o",
            "a.loupe",
            "--compiler-timeout-seconds",
            "30",
            "--compiler-output-bytes",
            "4096",
            "--audit-root",
            "checkout",
            "--source-name",
            "src/a.weave",
        ]
    )
    assert args.command == "capture"
    assert args.weave_files == [Path("a.weave")]
    assert args.output == Path("a.loupe")
    assert args.compiler_timeout_seconds == 30.0
    assert args.compiler_output_bytes == 4096
    assert args.audit_root == Path("checkout")
    assert args.source_names == ["src/a.weave"]


def test_report_parser() -> None:
    args = build_parser().parse_args(
        ["report", "a.loupe", "-o", "a.html", "--analysis-json", "a.json"]
    )
    assert args.command == "report"
    assert args.analysis_json == Path("a.json")


def test_diff_parser_defaults_to_v2_and_accepts_v1() -> None:
    default = build_parser().parse_args(["diff", "a.loupe", "b.loupe"])
    legacy = build_parser().parse_args(
        ["diff", "a.loupe", "b.loupe", "--format-version", "v1"]
    )

    assert default.command == "diff"
    assert default.before == Path("a.loupe")
    assert default.format_version == "v2"
    assert legacy.format_version == "v1"


def test_audit_parser_supports_sources_reports_and_process_limits() -> None:
    args = build_parser().parse_args(
        [
            "audit",
            "a.weave",
            "b.weave",
            "--report-out",
            "a.md",
            "--review-total-tokens",
            "120000",
            "--review-request-tokens",
            "30000",
            "--review-artifact-tokens",
            "60000",
            "--allow-unsafe-http",
            "--compiler-timeout-seconds",
            "45",
            "--compiler-output-bytes",
            "8192",
            "--runtime-timeout-seconds",
            "3.5",
            "--runtime-output-bytes",
            "2048",
            "--audit-root",
            "checkout",
            "--source-name",
            "src/a.weave",
            "--source-name",
            "src/b.weave",
        ]
    )
    assert args.weave_files == [Path("a.weave"), Path("b.weave")]
    assert args.report_out == Path("a.md")
    assert args.review_total_tokens == 120000
    assert args.review_request_tokens == 30000
    assert args.review_artifact_tokens == 60000
    assert args.allow_unsafe_http is True
    assert args.compiler_timeout_seconds == 45.0
    assert args.compiler_output_bytes == 8192
    assert args.runtime_timeout_seconds == 3.5
    assert args.runtime_output_bytes == 2048
    assert args.audit_root == Path("checkout")
    assert args.source_names == ["src/a.weave", "src/b.weave"]


def test_audit_parser_defers_unsafe_http_policy_to_environment() -> None:
    args = build_parser().parse_args(["audit", "a.weave"])

    assert args.allow_unsafe_http is None
    assert args.review_total_tokens == 524_288
    assert args.review_request_tokens == 98_304
    assert args.review_artifact_tokens == 262_144


def test_verify_bundle_parser_supports_policy_and_json_output() -> None:
    args = build_parser().parse_args(
        [
            "verify-bundle",
            "a.loupe",
            "--allow-undeclared",
            "--json-out",
            "verification.json",
        ]
    )
    assert args.command == "verify-bundle"
    assert args.bundle == Path("a.loupe")
    assert args.allow_undeclared is True
    assert args.json_out == Path("verification.json")


def test_verify_report_parser_supports_explicit_identity_inputs() -> None:
    args = build_parser().parse_args(
        [
            "verify-report",
            "a.md",
            "--source",
            "first.weave",
            "--source",
            "second.weave",
            "--weavec",
            "bin/weavec",
            "--model",
            "z-ai/glm-5.2",
            "--llm-endpoint",
            "http://example.test/v1",
            "--allow-unsafe-http",
            "--max-tokens",
            "4096",
            "--max-age-days",
            "14",
            "--json-out",
            "validity.json",
        ]
    )
    assert args.command == "verify-report"
    assert args.report == Path("a.md")
    assert args.sources == [Path("first.weave"), Path("second.weave")]
    assert args.weavec == Path("bin/weavec")
    assert args.model == "z-ai/glm-5.2"
    assert args.llm_endpoint == "http://example.test/v1"
    assert args.allow_unsafe_http is True
    assert args.max_tokens == 4096
    assert args.max_age_days == 14
    assert args.json_out == Path("validity.json")


def test_verify_report_identity_defaults_to_environment(monkeypatch) -> None:
    monkeypatch.setenv("WEAVE_LLM_MODEL", "configured-model")
    monkeypatch.setenv("WEAVE_LLM_ENDPOINT", "https://example.test/v1")

    args = build_parser().parse_args(["verify-report", "a.md"])

    assert args.model == "configured-model"
    assert args.llm_endpoint == "https://example.test/v1"
    assert args.allow_unsafe_http is None
    assert args.max_tokens is None
    assert args.sources is None


def test_main_dispatches_capture_limits() -> None:
    with patch("weave_loupe.cli.run_capture", return_value=0) as command:
        result = main(
            [
                "capture",
                "a.weave",
                "-o",
                "a.loupe",
                "--compiler-timeout-seconds",
                "12",
                "--compiler-output-bytes",
                "2048",
            ]
        )

    assert result == 0
    command.assert_called_once_with(
        weave_files=[Path("a.weave")],
        output=Path("a.loupe"),
        weavec=None,
        include_executable=False,
        compiler_timeout_seconds=12.0,
        compiler_output_bytes=2048,
        audit_root=None,
        source_names=None,
    )


def test_main_dispatches_diff_format() -> None:
    with patch("weave_loupe.cli.run_diff", return_value=0) as command:
        result = main(
            [
                "diff",
                "before.loupe",
                "after.loupe",
                "--format-version",
                "v1",
            ]
        )

    assert result == 0
    command.assert_called_once_with(
        before=Path("before.loupe"),
        after=Path("after.loupe"),
        json_out=None,
        html_out=None,
        format_version="v1",
    )


def test_main_dispatches_audit_limits() -> None:
    with patch("weave_loupe.cli.run_audit", return_value=0) as command:
        result = main(
            [
                "audit",
                "a.weave",
                "--review-total-tokens",
                "100000",
                "--review-request-tokens",
                "25000",
                "--review-artifact-tokens",
                "50000",
                "--allow-unsafe-http",
                "--compiler-timeout-seconds",
                "60",
                "--compiler-output-bytes",
                "4096",
                "--runtime-timeout-seconds",
                "4",
                "--runtime-output-bytes",
                "1024",
            ]
        )

    assert result == 0
    command.assert_called_once_with(
        weave_files=[Path("a.weave")],
        model="z-ai/glm-5.2",
        weavec=None,
        llvm_out=None,
        wir_out=None,
        report_out=None,
        max_tokens=4096,
        verbose=False,
        compiler_timeout_seconds=60.0,
        compiler_output_bytes=4096,
        runtime_timeout_seconds=4.0,
        runtime_output_bytes=1024,
        allow_unsafe_http=True,
        review_total_tokens=100000,
        review_request_tokens=25000,
        review_artifact_tokens=50000,
        audit_root=None,
        source_names=None,
    )


def test_main_dispatches_bundle_verification() -> None:
    with patch("weave_loupe.cli.run_verify_bundle", return_value=2) as command:
        result = main(
            [
                "verify-bundle",
                "a.loupe",
                "--allow-undeclared",
                "--json-out",
                "verification.json",
            ]
        )

    assert result == 2
    command.assert_called_once_with(
        bundle=Path("a.loupe"),
        json_out=Path("verification.json"),
        allow_undeclared=True,
    )


def test_main_dispatches_report_verification() -> None:
    with patch("weave_loupe.cli.run_verify_report", return_value=2) as command:
        result = main(
            [
                "verify-report",
                "a.md",
                "--source",
                "a.weave",
                "--source",
                "b.weave",
                "--weavec",
                "weavec",
                "--model",
                "z-ai/glm-5.2",
                "--llm-endpoint",
                "http://example.test/v1",
                "--allow-unsafe-http",
                "--max-tokens",
                "4096",
            ]
        )
    assert result == 2
    command.assert_called_once_with(
        report=Path("a.md"),
        source=None,
        sources=[Path("a.weave"), Path("b.weave")],
        weavec=Path("weavec"),
        model="z-ai/glm-5.2",
        endpoint="http://example.test/v1",
        max_tokens=4096,
        max_age_days=30,
        json_out=None,
        allow_unsafe_http=True,
    )
