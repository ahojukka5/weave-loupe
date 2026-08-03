from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

from weave_loupe.auditor_identity import AuditorIdentity, sha256_file
from weave_loupe.compiler_version import CompilerVersion
from weave_loupe.report_validity import ReportIdentity, evaluate_identity


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


def _identity(path: str, digest: str) -> ReportIdentity:
    return ReportIdentity(
        timestamp=datetime(2026, 8, 3, tzinfo=UTC),
        version="weavec v0.3.0+git.abc",
        version_source="command",
        compiler_binary_sha256="a" * 64,
        auditor_sha256="b" * 64,
        model=None,
        source_path=path,
        source_sha256=digest,
        runtime_path=None,
        runtime_sha256=None,
    )


def _evaluate(
    *,
    checkout: Path,
    recorded_path: str,
    digest: str,
) -> tuple[str, ...]:
    source = checkout / "src" / "demo.weave"
    report = checkout / "docs" / "demo.md"
    return evaluate_identity(
        report=report,
        source=source,
        identity=_identity(recorded_path, digest),
        compiler_identity=_compiler(),
        compiler_binary_sha256="a" * 64,
        auditor=_auditor(),
        now=datetime(2026, 8, 3, 1, tzinfo=UTC),
        max_age=timedelta(days=30),
    ).reasons


def test_relative_identity_survives_checkout_move(tmp_path: Path) -> None:
    checkout = tmp_path / "second"
    (checkout / ".git").mkdir(parents=True)
    source = checkout / "src" / "demo.weave"
    source.parent.mkdir()
    source.write_text("(program)\n", encoding="utf-8")
    (checkout / "docs").mkdir()

    assert (
        _evaluate(
            checkout=checkout,
            recorded_path="src/demo.weave",
            digest=sha256_file(source),
        )
        == ()
    )


def test_legacy_absolute_identity_survives_checkout_move(
    tmp_path: Path,
) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    old_source = first / "src" / "demo.weave"
    current_source = second / "src" / "demo.weave"
    old_source.parent.mkdir(parents=True)
    current_source.parent.mkdir(parents=True)
    (second / ".git").mkdir()
    (second / "docs").mkdir()
    old_source.write_text("(program)\n", encoding="utf-8")
    current_source.write_text("(program)\n", encoding="utf-8")

    assert (
        _evaluate(
            checkout=second,
            recorded_path=str(old_source.resolve()),
            digest=sha256_file(old_source),
        )
        == ()
    )


def test_moved_checkout_still_detects_content_change(tmp_path: Path) -> None:
    checkout = tmp_path / "second"
    (checkout / ".git").mkdir(parents=True)
    source = checkout / "src" / "demo.weave"
    source.parent.mkdir()
    source.write_text("changed\n", encoding="utf-8")
    (checkout / "docs").mkdir()

    reasons = _evaluate(
        checkout=checkout,
        recorded_path="src/demo.weave",
        digest="0" * 64,
    )

    assert reasons == ("source content changed since audit",)
