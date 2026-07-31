"""Scheduled refresh coverage for multi-source audit reports."""

from __future__ import annotations

import hashlib
import importlib.util
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

from weave_loupe.compiler_version import CompilerVersion


def _load_script() -> ModuleType:
    path = Path(__file__).parents[1] / "scripts" / "reaudit_stale.py"
    spec = importlib.util.spec_from_file_location("reaudit_multisource_module", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _identity() -> CompilerVersion:
    return CompilerVersion(
        display="weavec v0.3.0",
        base="v0.3.0",
        git_sha=None,
        development=False,
        source="command",
    )


def test_scheduled_discovery_owns_every_recorded_source(tmp_path: Path) -> None:
    module = _load_script()
    root = tmp_path / "docs" / "audit"
    root.mkdir(parents=True)
    first = root / "first.weave"
    second = root / "second.weave"
    first.write_text("(first)\n", encoding="utf-8")
    second.write_text("(second)\n", encoding="utf-8")
    now = datetime(2026, 8, 1, tzinfo=UTC)
    report = first.with_suffix(".md")
    report.write_text(
        "# report\n\n"
        f"- **Audit timestamp (UTC):** `{now.isoformat()}`\n"
        "- **weavec version:** `weavec v0.3.0`\n"
        "- **weavec version source:** `command`\n\n"
        "## Audited inputs\n\n"
        f"- Source `{first}` — SHA-256 `{_sha256(first)}` — "
        f"{first.stat().st_size} bytes\n"
        f"- Source `{second}` — SHA-256 `{_sha256(second)}` — "
        f"{second.stat().st_size} bytes\n",
        encoding="utf-8",
    )

    states = module._report_states(
        source_root=root,
        identity=_identity(),
        now=now + timedelta(hours=1),
        max_age=timedelta(days=30),
        force=False,
    )

    assert len(states) == 1
    assert states[0].source == first
    assert states[0].sources == (first, second)
    assert states[0].report == report


def test_scheduled_audit_passes_sources_in_recorded_order(tmp_path: Path) -> None:
    module = _load_script()
    first = tmp_path / "first.weave"
    second = tmp_path / "second.weave"
    first.write_text("(first)\n", encoding="utf-8")
    second.write_text("(second)\n", encoding="utf-8")
    report = tmp_path / "combined.md"
    state = module.ReportState(
        source=first,
        sources=(first, second),
        report=report,
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
    )
    logs = tmp_path / "logs"
    logs.mkdir()
    completed = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout="OK\n",
        stderr="",
    )

    with patch.object(module.subprocess, "run", return_value=completed) as run:
        outcome = module._audit(
            state=state,
            candidate_root=tmp_path / "candidates",
            weavec=tmp_path / "weavec",
            model="model",
            max_tokens=4096,
            logs_dir=logs,
        )

    command = run.call_args.args[0]
    audit_index = command.index("audit")
    weavec_index = command.index("--weavec")
    assert command[audit_index + 1 : weavec_index] == [str(first), str(second)]
    assert Path(outcome.run.stdout_log).parent == logs
    assert Path(outcome.run.stderr_log).parent == logs
    assert Path(outcome.run.stdout_log).read_text(encoding="utf-8") == "OK\n"
