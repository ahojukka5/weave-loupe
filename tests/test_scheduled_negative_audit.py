"""Scheduled refresh coverage for expected compiler failures."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

from weave_loupe.auditor_identity import AuditorIdentity
from weave_loupe.compiler_version import CompilerVersion


def _load_script() -> ModuleType:
    path = Path(__file__).parents[1] / "scripts" / "reaudit_stale.py"
    spec = importlib.util.spec_from_file_location("scheduled_negative_module", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _compiler() -> CompilerVersion:
    return CompilerVersion(
        display="weavec v0.3.0",
        base="v0.3.0",
        git_sha=None,
        development=False,
        source="command",
    )


def _auditor() -> AuditorIdentity:
    return AuditorIdentity(
        format="weave-loupe-auditor-identity-v1",
        sha256="b" * 64,
        files=(),
    )


def _write_case(root: Path) -> tuple[Path, Path]:
    root.mkdir(parents=True)
    source = root / "missing_module.weave"
    source.write_text(
        "module app\nimport absent\n",
        encoding="utf-8",
    )
    contract = root / "missing_module.audit.failure.toml"
    contract.write_text(
        'format = "weave-loupe-expected-failure-v1"\n'
        'sources = ["missing_module.weave"]\n'
        "exit_code = 10\n"
        'phase = "frontend"\n'
        'forbidden_artifacts = ["executable", "assembly", "disassembly"]\n\n'
        "[[diagnostics]]\n"
        'code = "frontend.module.import-missing-module"\n'
        'severity = "error"\n'
        'phase = "frontend"\n'
        "source_index = 0\n"
        "start_line = 2\n"
        "start_column = 8\n"
        "end_line = 2\n"
        "end_column = 14\n"
        'span_text = "absent"\n',
        encoding="utf-8",
    )
    return source, contract


def test_missing_negative_report_is_scheduled(tmp_path: Path) -> None:
    module = _load_script()
    root = tmp_path / "docs" / "negative-audit"
    source, contract = _write_case(root)

    states = module._expected_failure_states(
        negative_root=root,
        identity=_compiler(),
        compiler_binary_sha256="a" * 64,
        auditor=_auditor(),
        model="model",
        endpoint="https://example.test/v1",
        max_tokens=4096,
        now=datetime(2026, 8, 3, tzinfo=UTC),
        max_age=timedelta(days=30),
        force=False,
    )

    assert len(states) == 1
    assert states[0].source == source
    assert states[0].sources == (source,)
    assert states[0].report == root / "missing_module.md"
    assert states[0].expected_failure == contract
    assert states[0].kind == "expected failure"
    assert states[0].reason == "missing audit report"


def test_negative_audit_uses_deterministic_runner_and_records_timing(
    tmp_path: Path,
) -> None:
    module = _load_script()
    root = tmp_path / "negative"
    source, contract = _write_case(root)
    state = module.ReportState(
        source=source,
        sources=(source,),
        report=root / "missing_module.md",
        timestamp=None,
        version=None,
        version_source=None,
        compiler_binary_sha256=None,
        auditor_sha256=None,
        model=None,
        endpoint=None,
        max_tokens=None,
        source_sha256=None,
        runtime_sha256=None,
        reason="manual force",
        expected_failure=contract,
    )
    logs = tmp_path / "logs"
    logs.mkdir()
    completed = subprocess.CompletedProcess(
        args=[],
        returncode=2,
        stdout="report\n",
        stderr="contract mismatch\n",
    )

    with (
        patch.object(module.subprocess, "run", return_value=completed) as run,
        patch.object(module.time, "monotonic", side_effect=[10.0, 10.125]),
    ):
        outcome = module._audit(
            state=state,
            candidate_root=tmp_path / "candidates",
            weavec=tmp_path / "weavec",
            model="model",
            max_tokens=4096,
            logs_dir=logs,
            endpoint="https://example.test/v1",
        )

    command = run.call_args.args[0]
    assert command[:3] == [
        sys.executable,
        "-m",
        "weave_loupe.expected_failure_audit",
    ]
    assert str(contract) in command
    assert command[command.index("--llm-endpoint") + 1] == ("https://example.test/v1")
    assert outcome.run.kind == "expected failure"
    assert outcome.run.compiler_finding
    assert outcome.run.failure_class == "compiler finding"
    assert outcome.run.duration_seconds == 0.125


def test_summary_reports_case_kind_duration_and_failure_class() -> None:
    module = _load_script()
    run = module.AuditRun(
        source="docs/negative-audit/missing_module.weave",
        report="docs/negative-audit/missing_module.md",
        reason="manual force",
        returncode=2,
        stdout_log="stdout.md",
        stderr_log="stderr.txt",
        kind="expected failure",
        duration_seconds=0.125,
    )

    summary = module._render_summary(
        identity=_compiler(),
        compiler_binary_sha256="a" * 64,
        auditor=_auditor(),
        model="model",
        endpoint="https://example.test/v1",
        max_tokens=4096,
        states=[],
        runs=[run],
        now=datetime(2026, 8, 3, tzinfo=UTC),
    )

    assert "FAILED: compiler finding" in summary
    assert "expected failure" in summary
    assert "0.125 s" in summary
    assert module._run_document(run)["failure_class"] == "compiler finding"
