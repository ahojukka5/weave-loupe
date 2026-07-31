"""Tests for ordered multi-source audit report verification."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

from weave_loupe.auditor_identity import AuditorIdentity, sha256_file
from weave_loupe.compiler_version import CompilerVersion
from weave_loupe.report_integrity import seal_audit_report
from weave_loupe.report_validity import (
    ReportIdentity,
    SourceIdentity,
    evaluate_identity,
    evaluate_report,
    read_report_identity,
)

_NOW = datetime(2026, 8, 1, tzinfo=UTC)


def _compiler() -> CompilerVersion:
    return CompilerVersion(
        display="weavec v0.3.0+git.multi",
        base="v0.3.0",
        git_sha="multi",
        development=True,
        source="command",
    )


def _auditor() -> AuditorIdentity:
    return AuditorIdentity(
        format="weave-loupe-auditor-identity-v1",
        sha256="b" * 64,
        files=(),
    )


def _source_identity(path: Path, *, recorded_path: str | None = None) -> SourceIdentity:
    return SourceIdentity(
        path=recorded_path or str(path),
        sha256=sha256_file(path),
        size=path.stat().st_size,
    )


def _identity(*sources: SourceIdentity) -> ReportIdentity:
    first = sources[0] if sources else None
    return ReportIdentity(
        timestamp=_NOW,
        version="weavec v0.3.0+git.multi",
        version_source="command",
        compiler_binary_sha256="a" * 64,
        auditor_sha256="b" * 64,
        model=None,
        source_path=first.path if first is not None else None,
        source_sha256=first.sha256 if first is not None else None,
        runtime_path=None,
        runtime_sha256=None,
        sources=tuple(sources),
    )


def _evaluate(
    report: Path,
    identity: ReportIdentity,
    sources: tuple[Path, ...],
):
    return evaluate_identity(
        report=report,
        source=sources[0] if sources else report.with_suffix(".weave"),
        sources=sources,
        identity=identity,
        compiler_identity=_compiler(),
        compiler_binary_sha256="a" * 64,
        auditor=_auditor(),
        now=_NOW + timedelta(hours=1),
        max_age=timedelta(days=30),
    )


def test_parser_preserves_every_source_in_order_with_sizes(tmp_path: Path) -> None:
    first = tmp_path / "first.weave"
    second = tmp_path / "second.weave"
    first.write_text("(first)\n", encoding="utf-8")
    second.write_text("(second)\n", encoding="utf-8")
    report = tmp_path / "report.md"
    report.write_text(
        "## Audited inputs\n\n"
        f"- Source `{first}` — SHA-256 `{sha256_file(first)}` — "
        f"{first.stat().st_size} bytes\n"
        f"- Source `{second}` — SHA-256 `{sha256_file(second)}` — "
        f"{second.stat().st_size} bytes\n\n"
        "## Captured evidence\n",
        encoding="utf-8",
    )

    identity = read_report_identity(report)

    assert identity.sources == (
        _source_identity(first),
        _source_identity(second),
    )
    assert identity.source_path == str(first)
    assert identity.source_sha256 == sha256_file(first)


def test_two_unchanged_sources_verify_in_compiler_order(tmp_path: Path) -> None:
    first = tmp_path / "first.weave"
    second = tmp_path / "second.weave"
    first.write_text("(first)\n", encoding="utf-8")
    second.write_text("(second)\n", encoding="utf-8")
    identity = _identity(_source_identity(first), _source_identity(second))

    result = _evaluate(tmp_path / "report.md", identity, (first, second))

    assert result.valid
    assert result.sources == (first, second)
    assert result.source_mismatches == ()


def test_modifying_second_source_identifies_exact_entry(tmp_path: Path) -> None:
    first = tmp_path / "first.weave"
    second = tmp_path / "second.weave"
    first.write_text("(first)\n", encoding="utf-8")
    second.write_text("(second)\n", encoding="utf-8")
    identity = _identity(_source_identity(first), _source_identity(second))
    second.write_text("(changed)\n", encoding="utf-8")

    result = _evaluate(tmp_path / "report.md", identity, (first, second))

    assert result.reasons == (f"source content changed at index 1: {second}",)
    mismatch = result.source_mismatches[0]
    assert mismatch.kind == "modified"
    assert mismatch.recorded_index == 1
    assert mismatch.current_index == 1
    assert mismatch.recorded_path == str(second)
    assert mismatch.current_path == str(second)
    assert mismatch.recorded_sha256 != mismatch.current_sha256
    assert mismatch.recorded_size != mismatch.current_size


def test_reordered_sources_are_detected_without_false_content_changes(
    tmp_path: Path,
) -> None:
    first = tmp_path / "first.weave"
    second = tmp_path / "second.weave"
    first.write_text("(first)\n", encoding="utf-8")
    second.write_text("(second)\n", encoding="utf-8")
    identity = _identity(_source_identity(first), _source_identity(second))

    result = _evaluate(tmp_path / "report.md", identity, (second, first))

    assert result.reasons == ("source order changed since audit",)
    assert [item.kind for item in result.source_mismatches] == ["reordered"]


def test_added_and_removed_sources_are_reported(tmp_path: Path) -> None:
    first = tmp_path / "first.weave"
    second = tmp_path / "second.weave"
    third = tmp_path / "third.weave"
    first.write_text("(first)\n", encoding="utf-8")
    second.write_text("(second)\n", encoding="utf-8")
    third.write_text("(third)\n", encoding="utf-8")
    identity = _identity(_source_identity(first), _source_identity(second))

    added = _evaluate(tmp_path / "report.md", identity, (first, second, third))
    removed = _evaluate(tmp_path / "report.md", identity, (first,))

    assert added.reasons == (f"source added since audit at index 2: {third}",)
    assert added.source_mismatches[0].kind == "added"
    assert removed.reasons == (f"source removed since audit at index 1: {second}",)
    assert removed.source_mismatches[0].kind == "removed"


def test_absolute_paths_resolve_after_checkout_moves(tmp_path: Path) -> None:
    checkout = tmp_path / "new-checkout"
    (checkout / ".git").mkdir(parents=True)
    source_dir = checkout / "src"
    source_dir.mkdir()
    first = source_dir / "first.weave"
    second = source_dir / "second.weave"
    first.write_text("(first)\n", encoding="utf-8")
    second.write_text("(second)\n", encoding="utf-8")
    report = checkout / "audit.md"
    recorded_first = "/old/worktree/src/first.weave"
    recorded_second = "/old/worktree/src/second.weave"
    timestamp = _NOW.isoformat()
    content = (
        "# Weave Loupe Audit Report\n\n"
        "## Reproducibility\n\n"
        f"- **Audit timestamp (UTC):** `{timestamp}`\n"
        f"- **Auditor content SHA-256:** `{'b' * 64}`\n"
        f"- **weavec binary SHA-256:** `{'a' * 64}`\n"
        "- **weavec version:** `weavec v0.3.0+git.multi`\n"
        "- **weavec version source:** `command`\n\n"
        "## Audited inputs\n\n"
        f"- Source `{recorded_first}` — SHA-256 `{sha256_file(first)}` — "
        f"{first.stat().st_size} bytes\n"
        f"- Source `{recorded_second}` — SHA-256 `{sha256_file(second)}` — "
        f"{second.stat().st_size} bytes\n\n"
        "## Captured evidence\n"
    )
    report.write_text(seal_audit_report(content), encoding="utf-8")

    result = evaluate_report(
        report=report,
        source=None,
        sources=None,
        compiler_identity=_compiler(),
        compiler_binary_sha256="a" * 64,
        auditor=_auditor(),
        now=_NOW + timedelta(hours=1),
        max_age=timedelta(days=30),
    )

    assert result.valid
    assert result.sources == (first, second)
