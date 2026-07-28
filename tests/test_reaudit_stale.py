"""Tests for the scheduled stale-report selection policy."""

from __future__ import annotations

import hashlib
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


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_report(
    path: Path,
    *,
    timestamp: datetime,
    version: str,
    version_source: str | None = "command",
    include_source_hash: bool = True,
    source_sha256: str | None = None,
    explicit_source_label: bool = True,
    runtime_path: Path | None = None,
    runtime_sha256: str | None = None,
) -> None:
    source = path.with_suffix(".weave")
    source_line = ""
    if include_source_hash:
        digest = source_sha256 or _sha256(source)
        prefix = "Source " if explicit_source_label else ""
        source_line = f"- {prefix}`{source}` — SHA-256 `{digest}`\n"
    version_source_line = (
        f"- **weavec version source:** `{version_source}`\n"
        if version_source is not None
        else ""
    )
    runtime_line = ""
    if runtime_path is not None:
        digest = runtime_sha256 or _sha256(runtime_path)
        runtime_line = (
            f"- Runtime matrix `{runtime_path}` — SHA-256 `{digest}`\n"
        )
    path.write_text(
        "# report\n\n"
        f"- **Audit timestamp (UTC):** `{timestamp.isoformat()}`\n"
        f"- **weavec version:** `{version}`\n"
        f"{version_source_line}\n"
        "## Audited inputs\n\n"
        f"{source_line}{runtime_line}",
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


def _states(
    module: ModuleType,
    *,
    root: Path,
    identity: CompilerVersion,
    now: datetime,
) -> list[object]:
    return module._report_states(
        source_root=root,
        identity=identity,
        now=now,
        max_age=timedelta(days=30),
        force=False,
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
    states = _states(
        module,
        root=root,
        identity=_identity("weavec v0.3.0+git.new", development=True),
        now=now,
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

    states = _states(
        module,
        root=root,
        identity=_identity("weavec v0.3.0+git.same", development=True),
        now=now,
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

    states = _states(
        module,
        root=root,
        identity=_identity("weavec v0.3.0", development=False),
        now=now,
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

    states = _states(
        module,
        root=root,
        identity=_identity(
            "weavec v0.3.0+git.same",
            development=True,
            source="repository",
        ),
        now=now,
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
    fresh = _states(module, root=root, identity=identity, now=now)
    assert fresh[0].reason is None

    _write_report(
        report,
        timestamp=now - timedelta(days=30),
        version="weavec v0.2.0",
    )
    stale = _states(module, root=root, identity=identity, now=now)
    assert stale[0].reason == "report age is at least 30 days"


def test_changed_source_hash_invalidates_fresh_report(tmp_path: Path) -> None:
    module = _load_script()
    root = tmp_path / "docs" / "audit"
    root.mkdir(parents=True)
    source = root / "demo.weave"
    source.write_text("(program (version \"old\"))\n", encoding="utf-8")
    now = datetime(2026, 7, 27, tzinfo=UTC)
    _write_report(
        source.with_suffix(".md"),
        timestamp=now - timedelta(hours=1),
        version="weavec v0.3.0",
    )
    source.write_text("(program (version \"new\"))\n", encoding="utf-8")

    states = _states(
        module,
        root=root,
        identity=_identity("weavec v0.3.0", development=False),
        now=now,
    )

    assert states[0].reason == "source content changed since audit"


def test_missing_source_hash_invalidates_legacy_report(tmp_path: Path) -> None:
    module = _load_script()
    root = tmp_path / "docs" / "audit"
    root.mkdir(parents=True)
    source = root / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")
    now = datetime(2026, 7, 27, tzinfo=UTC)
    _write_report(
        source.with_suffix(".md"),
        timestamp=now - timedelta(hours=1),
        version="weavec v0.3.0",
        include_source_hash=False,
    )

    states = _states(
        module,
        root=root,
        identity=_identity("weavec v0.3.0", development=False),
        now=now,
    )

    assert states[0].reason == "report does not record audited source hash"


def test_added_runtime_matrix_invalidates_report(tmp_path: Path) -> None:
    module = _load_script()
    root = tmp_path / "docs" / "audit"
    root.mkdir(parents=True)
    source = root / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")
    now = datetime(2026, 7, 27, tzinfo=UTC)
    _write_report(
        source.with_suffix(".md"),
        timestamp=now - timedelta(hours=1),
        version="weavec v0.3.0",
    )
    source.with_suffix(".audit.json").write_text("{}\n", encoding="utf-8")

    states = _states(
        module,
        root=root,
        identity=_identity("weavec v0.3.0", development=False),
        now=now,
    )

    assert states[0].reason == "runtime matrix was added or not recorded"


def test_changed_runtime_matrix_invalidates_report(tmp_path: Path) -> None:
    module = _load_script()
    root = tmp_path / "docs" / "audit"
    root.mkdir(parents=True)
    source = root / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")
    runtime = source.with_suffix(".audit.json")
    runtime.write_text('{"cases": [1]}\n', encoding="utf-8")
    now = datetime(2026, 7, 27, tzinfo=UTC)
    _write_report(
        source.with_suffix(".md"),
        timestamp=now - timedelta(hours=1),
        version="weavec v0.3.0",
        runtime_path=runtime,
    )
    runtime.write_text('{"cases": [2]}\n', encoding="utf-8")

    states = _states(
        module,
        root=root,
        identity=_identity("weavec v0.3.0", development=False),
        now=now,
    )

    assert states[0].reason == "runtime matrix content changed since audit"


def test_removed_runtime_matrix_invalidates_report(tmp_path: Path) -> None:
    module = _load_script()
    root = tmp_path / "docs" / "audit"
    root.mkdir(parents=True)
    source = root / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")
    runtime = source.with_suffix(".audit.json")
    runtime.write_text('{"cases": []}\n', encoding="utf-8")
    now = datetime(2026, 7, 27, tzinfo=UTC)
    _write_report(
        source.with_suffix(".md"),
        timestamp=now - timedelta(hours=1),
        version="weavec v0.3.0",
        runtime_path=runtime,
    )
    runtime.unlink()

    states = _states(
        module,
        root=root,
        identity=_identity("weavec v0.3.0", development=False),
        now=now,
    )

    assert states[0].reason == "runtime matrix was removed since audit"


def test_report_identity_parser_reads_inputs_and_attestation(tmp_path: Path) -> None:
    module = _load_script()
    source = tmp_path / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")
    runtime = tmp_path / "demo.audit.json"
    runtime.write_text('{"cases": []}\n', encoding="utf-8")
    report = source.with_suffix(".md")
    timestamp = datetime(2026, 7, 27, 12, 30, tzinfo=UTC)
    _write_report(
        report,
        timestamp=timestamp,
        version="weavec v0.3.0+git.abc",
        version_source="command",
        runtime_path=runtime,
    )

    identity = module._read_report_identity(report)

    assert identity.timestamp == timestamp
    assert identity.version == "weavec v0.3.0+git.abc"
    assert identity.version_source == "command"
    assert identity.source_path == str(source)
    assert identity.source_sha256 == _sha256(source)
    assert identity.runtime_path == str(runtime)
    assert identity.runtime_sha256 == _sha256(runtime)


def test_parser_accepts_legacy_unlabelled_source_input(tmp_path: Path) -> None:
    module = _load_script()
    source = tmp_path / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")
    report = source.with_suffix(".md")
    _write_report(
        report,
        timestamp=datetime(2026, 7, 27, tzinfo=UTC),
        version="weavec v0.3.0",
        explicit_source_label=False,
    )

    identity = module._read_report_identity(report)

    assert identity.source_path == str(source)
    assert identity.source_sha256 == _sha256(source)
