"""Tests for shared audit report validity evaluation."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

from weave_loupe.auditor_identity import AuditorIdentity, sha256_file
from weave_loupe.compiler_version import CompilerVersion
from weave_loupe.report_validity import (
    ReportIdentity,
    evaluate_identity,
    read_report_identity,
)


def _compiler() -> CompilerVersion:
    return CompilerVersion(
        display="weavec v0.3.0+git.abc",
        base="v0.3.0",
        git_sha="abc",
        development=True,
        source="command",
    )


def _auditor() -> AuditorIdentity:
    return AuditorIdentity(
        format="weave-loupe-auditor-identity-v1",
        sha256="b" * 64,
        files=(),
    )


def _identity(source: Path) -> ReportIdentity:
    return ReportIdentity(
        timestamp=datetime(2026, 7, 28, tzinfo=UTC),
        version="weavec v0.3.0+git.abc",
        version_source="command",
        compiler_binary_sha256="a" * 64,
        auditor_sha256="b" * 64,
        source_path=str(source),
        source_sha256=sha256_file(source),
        runtime_path=None,
        runtime_sha256=None,
    )


def test_exact_identity_is_valid(tmp_path: Path) -> None:
    source = tmp_path / "demo.weave"
    source.write_text("(program)\n")

    result = evaluate_identity(
        report=source.with_suffix(".md"),
        source=source,
        identity=_identity(source),
        compiler_identity=_compiler(),
        compiler_binary_sha256="a" * 64,
        auditor=_auditor(),
        now=datetime(2026, 7, 28, 1, tzinfo=UTC),
        max_age=timedelta(days=30),
    )

    assert result.valid
    assert result.primary_reason is None
    assert result.reasons == ()


def test_evaluator_reports_every_independent_stale_reason(tmp_path: Path) -> None:
    source = tmp_path / "demo.weave"
    source.write_text("changed\n")
    identity = ReportIdentity(
        timestamp=datetime(2026, 6, 1, tzinfo=UTC),
        version="weavec v0.3.0+git.old",
        version_source="repository",
        compiler_binary_sha256="c" * 64,
        auditor_sha256="d" * 64,
        source_path=str(tmp_path / "renamed.weave"),
        source_sha256="e" * 64,
        runtime_path=None,
        runtime_sha256=None,
    )

    result = evaluate_identity(
        report=source.with_suffix(".md"),
        source=source,
        identity=identity,
        compiler_identity=_compiler(),
        compiler_binary_sha256="a" * 64,
        auditor=_auditor(),
        now=datetime(2026, 7, 28, tzinfo=UTC),
        max_age=timedelta(days=30),
    )

    assert result.reasons == (
        "source path changed since audit",
        "source content changed since audit",
        "compiler binary changed since audit",
        "audit implementation changed since audit",
        "report age is at least 30 days",
        "development compiler changed from weavec v0.3.0+git.old "
        "to weavec v0.3.0+git.abc",
        "compiler identity source changed from repository to command",
    )


def test_runtime_path_and_content_are_verified(tmp_path: Path) -> None:
    source = tmp_path / "demo.weave"
    source.write_text("(program)\n")
    runtime = source.with_suffix(".audit.json")
    runtime.write_text('{"cases": []}\n')
    identity = _identity(source)
    identity = ReportIdentity(
        **{
            **identity.__dict__,
            "runtime_path": str(tmp_path / "other.audit.json"),
            "runtime_sha256": "f" * 64,
        }
    )

    result = evaluate_identity(
        report=source.with_suffix(".md"),
        source=source,
        identity=identity,
        compiler_identity=_compiler(),
        compiler_binary_sha256="a" * 64,
        auditor=_auditor(),
        now=datetime(2026, 7, 28, 1, tzinfo=UTC),
        max_age=timedelta(days=30),
    )

    assert result.reasons == (
        "runtime matrix path changed since audit",
        "runtime matrix content changed since audit",
    )


def test_parser_ignores_identity_like_model_prose(tmp_path: Path) -> None:
    source = tmp_path / "demo.weave"
    source.write_text("(program)\n")
    report = source.with_suffix(".md")
    report.write_text(
        "# report\n\n"
        "- **Audit timestamp (UTC):** `2026-07-28T00:00:00+00:00`\n"
        f"- **Auditor content SHA-256:** `{'b' * 64}`\n"
        f"- **weavec binary SHA-256:** `{'a' * 64}`\n"
        "- **weavec version:** `weavec v0.3.0+git.abc`\n"
        "- **weavec version source:** `command`\n\n"
        "## Audited inputs\n\n"
        f"- Source `{source}` — SHA-256 `{sha256_file(source)}`\n\n"
        "## LLM review\n\n"
        f"- Source `{source}` — SHA-256 `{'0' * 64}`\n",
        encoding="utf-8",
    )

    identity = read_report_identity(report)

    assert identity.source_sha256 == sha256_file(source)
    assert identity.compiler_binary_sha256 == "a" * 64
    assert identity.auditor_sha256 == "b" * 64
