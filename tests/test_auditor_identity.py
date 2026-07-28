"""Tests for content-addressed audit implementation identity."""

from __future__ import annotations

from pathlib import Path

from weave_loupe.auditor_identity import (
    AUDITOR_IDENTITY_FORMAT,
    identify_auditor,
    sha256_file,
)


def _fake_source_tree(tmp_path: Path) -> Path:
    package = tmp_path / "src" / "weave_loupe"
    scripts = tmp_path / "scripts"
    package.mkdir(parents=True)
    scripts.mkdir()
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n")
    (tmp_path / "uv.lock").write_text("version = 1\n")
    (package / "audit.py").write_text("VALUE = 1\n")
    (package / "ignored.txt").write_text("not executable audit code\n")
    (scripts / "audit_pr.py").write_text("print('audit')\n")
    (scripts / "reaudit_stale.py").write_text("print('refresh')\n")
    return package / "audit.py"


def test_auditor_identity_is_stable_for_identical_content(tmp_path: Path) -> None:
    anchor = _fake_source_tree(tmp_path)

    first = identify_auditor(anchor)
    second = identify_auditor(anchor)

    assert first == second
    assert first.format == AUDITOR_IDENTITY_FORMAT
    assert len(first.sha256) == 64
    assert [item.path for item in first.files] == [
        "pyproject.toml",
        "scripts/audit_pr.py",
        "scripts/reaudit_stale.py",
        "src/weave_loupe/audit.py",
        "uv.lock",
    ]


def test_auditor_identity_changes_with_code_or_lockfile(tmp_path: Path) -> None:
    anchor = _fake_source_tree(tmp_path)
    original = identify_auditor(anchor)

    anchor.write_text("VALUE = 2\n")
    code_changed = identify_auditor(anchor)
    (tmp_path / "uv.lock").write_text("version = 2\n")
    lock_changed = identify_auditor(anchor)

    assert code_changed.sha256 != original.sha256
    assert lock_changed.sha256 != code_changed.sha256


def test_nonsemantic_files_do_not_change_auditor_identity(tmp_path: Path) -> None:
    anchor = _fake_source_tree(tmp_path)
    original = identify_auditor(anchor)

    (tmp_path / "src" / "weave_loupe" / "ignored.txt").write_text("changed\n")
    (tmp_path / "docs.md").write_text("changed documentation\n")

    assert identify_auditor(anchor) == original


def test_sha256_file_streams_exact_bytes(tmp_path: Path) -> None:
    path = tmp_path / "binary"
    path.write_bytes(b"\x00audit\xff")

    assert sha256_file(path) == (
        "8a2481e84d49bdc43ed99b6d0b7a0c61dc193680d7f4f68699647ebd91a6e454"
    )
