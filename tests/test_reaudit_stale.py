"""Tests for the scheduled stale-report selection policy."""

from __future__ import annotations

import importlib.util
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import ModuleType

from weave_loupe.compiler_version import CompilerVersion


def _load_script() -> ModuleType:
    path = Path(__file__).parents[1] / "scripts" / "reaudit_stale.py"
    spec = importlib.util.spec_from_file_location("reaudit_stale_test_module", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_report(path: Path, *, timestamp: datetime, version: str) -> None:
    path.write_text(
        "# report\n\n"
        f"- **Audit timestamp (UTC):** `{timestamp.isoformat()}`\n"
        f"- **weavec version:** `{version}`\n",
        encoding="utf-8",
    )


def test_development_version_change_is_due_immediately(tmp_path: Path) -> None:
    module = _load_script()
    root = tmp_path / "docs" / "audit"
    root.mkdir(parents=True)
    source = root / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")
    now = datetime(2026, 7, 27, tzinfo=UTC)
    _write_report(
        source.with_suffix(".md"),
        timestamp=now - timedelta(days=1),
        version="weavec v0.3.0+git.old",
    )
    identity = CompilerVersion(
        display="weavec v0.3.0+git.new",
        base="v0.3.0",
        git_sha="new",
        development=True,
        source="command",
    )
    states = module._report_states(
        source_root=root,
        identity=identity,
        now=now,
        max_age=timedelta(days=30),
        force=False,
    )
    assert states[0].reason == (
        "development compiler changed from weavec v0.3.0+git.old "
        "to weavec v0.3.0+git.new"
    )


def test_release_report_uses_monthly_expiry(tmp_path: Path) -> None:
    module = _load_script()
    root = tmp_path / "docs" / "audit"
    root.mkdir(parents=True)
    source = root / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")
    now = datetime(2026, 7, 27, tzinfo=UTC)
    report = source.with_suffix(".md")
    _write_report(
        report,
        timestamp=now - timedelta(days=29),
        version="weavec v0.2.0",
    )
    identity = CompilerVersion(
        display="weavec v0.3.0",
        base="v0.3.0",
        git_sha=None,
        development=False,
        source="command",
    )
    fresh = module._report_states(
        source_root=root,
        identity=identity,
        now=now,
        max_age=timedelta(days=30),
        force=False,
    )
    assert fresh[0].reason is None

    _write_report(
        report,
        timestamp=now - timedelta(days=30),
        version="weavec v0.2.0",
    )
    stale = module._report_states(
        source_root=root,
        identity=identity,
        now=now,
        max_age=timedelta(days=30),
        force=False,
    )
    assert stale[0].reason == "report age is at least 30 days"
