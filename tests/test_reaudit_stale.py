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


def _write_report(
    path: Path,
    *,
    timestamp: datetime,
    version: str,
    version_source: str | None = "command",
) -> None:
    source_line = (
        f"- **weavec version source:** `{version_source}`\n"
        if version_source is not None
        else ""
    )
    path.write_text(
        "# report\n\n"
        f"- **Audit timestamp (UTC):** `{timestamp.isoformat()}`\n"
        f"- **weavec version:** `{version}`\n"
        f"{source_line}",
        encoding="utf-8",
    )


def _identity(
    display: str,
    *,
    development: bool,
    source: str = "command",
) -> CompilerVersion:
    return CompilerVersion(
        display=display,
        base="v0.3.0",
        git_sha="new" if development else None,
        development=development,
        source=source,
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
    states = module._report_states(
        source_root=root,
        identity=_identity("weavec v0.3.0+git.new", development=True),
        now=now,
        max_age=timedelta(days=30),
        force=False,
    )
    assert states[0].reason == (
        "development compiler changed from weavec v0.3.0+git.old "
        "to weavec v0.3.0+git.new"
    )


def test_command_identity_replaces_repository_inference(tmp_path: Path) -> None:
    module = _load_script()
    root = tmp_path / "docs" / "audit"
    root.mkdir(parents=True)
    source = root / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")
    now = datetime(2026, 7, 27, tzinfo=UTC)
    _write_report(
        source.with_suffix(".md"),
        timestamp=now - timedelta(days=1),
        version="weavec v0.3.0+git.same",
        version_source="repository",
    )

    states = module._report_states(
        source_root=root,
        identity=_identity("weavec v0.3.0+git.same", development=True),
        now=now,
        max_age=timedelta(days=30),
        force=False,
    )

    assert states[0].version_source == "repository"
    assert states[0].reason == (
        "compiler identity source changed from repository to command"
    )


def test_missing_identity_source_is_reaudited(tmp_path: Path) -> None:
    module = _load_script()
    root = tmp_path / "docs" / "audit"
    root.mkdir(parents=True)
    source = root / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")
    now = datetime(2026, 7, 27, tzinfo=UTC)
    _write_report(
        source.with_suffix(".md"),
        timestamp=now - timedelta(days=1),
        version="weavec v0.3.0",
        version_source=None,
    )

    states = module._report_states(
        source_root=root,
        identity=_identity("weavec v0.3.0", development=False),
        now=now,
        max_age=timedelta(days=30),
        force=False,
    )

    assert states[0].version_source is None
    assert states[0].reason == (
        "compiler identity source changed from unknown to command"
    )


def test_repository_fallback_does_not_claim_command_attestation(
    tmp_path: Path,
) -> None:
    module = _load_script()
    root = tmp_path / "docs" / "audit"
    root.mkdir(parents=True)
    source = root / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")
    now = datetime(2026, 7, 27, tzinfo=UTC)
    _write_report(
        source.with_suffix(".md"),
        timestamp=now - timedelta(days=1),
        version="weavec v0.3.0+git.same",
        version_source="repository",
    )

    states = module._report_states(
        source_root=root,
        identity=_identity(
            "weavec v0.3.0+git.same",
            development=True,
            source="repository",
        ),
        now=now,
        max_age=timedelta(days=30),
        force=False,
    )

    assert states[0].reason is None


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
    identity = _identity("weavec v0.3.0", development=False)
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


def test_report_identity_parser_reads_all_attestation_fields(tmp_path: Path) -> None:
    module = _load_script()
    report = tmp_path / "demo.md"
    timestamp = datetime(2026, 7, 27, 12, 30, tzinfo=UTC)
    _write_report(
        report,
        timestamp=timestamp,
        version="weavec v0.3.0+git.abc",
        version_source="command",
    )

    identity = module._read_report_identity(report)

    assert identity.timestamp == timestamp
    assert identity.version == "weavec v0.3.0+git.abc"
    assert identity.version_source == "command"
