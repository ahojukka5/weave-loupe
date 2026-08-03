"""CLI tests for differential compiler audits."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from weave_loupe.cli import build_parser, main
from weave_loupe.commands.compiler_audit import run_compiler_audit


def _result(*, passed: bool, category: str | None = None) -> dict[str, object]:
    failures = []
    if category is not None:
        failures.append(
            {
                "category": category,
                "code": "test-failure",
                "detail": "configured test failure",
            }
        )
    compiler = {"version": "weavec v0.3.0", "sha256": "a" * 64}
    return {
        "format": "weave-loupe-compiler-audit-v1",
        "status": "pass" if passed else "regression",
        "passed": passed,
        "baseline": {"compiler": compiler},
        "candidate": {"compiler": compiler},
        "comparison": {"metric_deltas": []},
        "failures": failures,
        "review": None,
        "seal": {"sha256": "b" * 64},
    }


def test_compiler_audit_parser_accepts_complete_configuration() -> None:
    args = build_parser().parse_args(
        [
            "compiler-audit",
            "a.weave",
            "b.weave",
            "--baseline-weavec",
            "bin/baseline",
            "--candidate-weavec",
            "bin/candidate",
            "--work-dir",
            "build/compare",
            "--policy",
            "policy.json",
            "--json-out",
            "result.json",
            "--report-out",
            "result.md",
            "--review-model",
            "reviewer",
            "--review-max-tokens",
            "2048",
            "--allow-unsafe-http",
            "--compiler-timeout-seconds",
            "90",
            "--compiler-output-bytes",
            "8192",
            "--runtime-timeout-seconds",
            "5",
            "--runtime-output-bytes",
            "4096",
            "--audit-root",
            "checkout",
            "--source-name",
            "src/a.weave",
            "--source-name",
            "src/b.weave",
        ]
    )

    assert args.command == "compiler-audit"
    assert args.weave_files == [Path("a.weave"), Path("b.weave")]
    assert args.baseline_weavec == Path("bin/baseline")
    assert args.candidate_weavec == Path("bin/candidate")
    assert args.work_dir == Path("build/compare")
    assert args.policy == Path("policy.json")
    assert args.review_model == "reviewer"
    assert args.review_max_tokens == 2048
    assert args.allow_unsafe_http is True
    assert args.compiler_timeout_seconds == 90.0
    assert args.compiler_output_bytes == 8192
    assert args.runtime_timeout_seconds == 5.0
    assert args.runtime_output_bytes == 4096
    assert args.audit_root == Path("checkout")
    assert args.source_names == ["src/a.weave", "src/b.weave"]


def test_main_dispatches_compiler_audit() -> None:
    with patch("weave_loupe.cli.run_compiler_audit", return_value=2) as command:
        code = main(
            [
                "compiler-audit",
                "a.weave",
                "--baseline-weavec",
                "baseline",
                "--candidate-weavec",
                "candidate",
            ]
        )

    assert code == 2
    command.assert_called_once_with(
        weave_files=[Path("a.weave")],
        baseline_weavec=Path("baseline"),
        candidate_weavec=Path("candidate"),
        work_dir=Path("build/compiler-audit"),
        policy=None,
        json_out=None,
        report_out=None,
        review_model=None,
        review_max_tokens=4096,
        allow_unsafe_http=None,
        compiler_timeout_seconds=None,
        compiler_output_bytes=None,
        runtime_timeout_seconds=None,
        runtime_output_bytes=None,
        audit_root=None,
        source_names=None,
    )


def test_command_writes_sealed_outputs_and_returns_regression(tmp_path: Path) -> None:
    json_out = tmp_path / "result.json"
    report_out = tmp_path / "result.md"
    with patch(
        "weave_loupe.commands.compiler_audit.audit_compilers",
        return_value=_result(passed=False, category="semantic"),
    ):
        code = run_compiler_audit(
            weave_files=[Path("a.weave")],
            baseline_weavec=Path("baseline"),
            candidate_weavec=Path("candidate"),
            work_dir=tmp_path / "work",
            policy=None,
            json_out=json_out,
            report_out=report_out,
            review_model=None,
            review_max_tokens=4096,
            allow_unsafe_http=None,
            compiler_timeout_seconds=None,
            compiler_output_bytes=None,
            runtime_timeout_seconds=None,
            runtime_output_bytes=None,
        )

    assert code == 2
    assert json.loads(json_out.read_text())["passed"] is False
    markdown = report_out.read_text()
    assert "# Weave Loupe Compiler Audit" in markdown
    assert "Report content SHA-256" in markdown
    assert "semantic:test-failure" in markdown


def test_command_returns_infrastructure_exit(tmp_path: Path) -> None:
    with patch(
        "weave_loupe.commands.compiler_audit.audit_compilers",
        return_value=_result(passed=False, category="infrastructure"),
    ):
        code = run_compiler_audit(
            weave_files=[Path("a.weave")],
            baseline_weavec=Path("baseline"),
            candidate_weavec=Path("candidate"),
            work_dir=tmp_path,
            policy=None,
            json_out=tmp_path / "result.json",
            report_out=None,
            review_model=None,
            review_max_tokens=4096,
            allow_unsafe_http=None,
            compiler_timeout_seconds=None,
            compiler_output_bytes=None,
            runtime_timeout_seconds=None,
            runtime_output_bytes=None,
        )

    assert code == 1
