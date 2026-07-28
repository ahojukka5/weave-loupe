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
    workflows = tmp_path / ".github" / "workflows"
    package.mkdir(parents=True)
    scripts.mkdir()
    workflows.mkdir(parents=True)
    (tmp_path / "pyproject.toml").write_text(
        "[project]\nname='demo'\n", encoding="utf-8"
    )
    (tmp_path / "uv.lock").write_text("version = 1\n", encoding="utf-8")
    (package / "audit.py").write_text("VALUE = 1\n", encoding="utf-8")
    (package / "ignored.txt").write_text(
        "not executable audit code\n", encoding="utf-8"
    )
    (scripts / "audit_pr.py").write_text("print('audit')\n", encoding="utf-8")
    (scripts / "reaudit_stale.py").write_text("print('refresh')\n", encoding="utf-8")
    (workflows / "weave-audit.yml").write_text("name: audit\n", encoding="utf-8")
    (workflows / "scheduled-reaudit.yml").write_text(
        "name: scheduled\n", encoding="utf-8"
    )
    return package / "audit.py"


def test_auditor_identity_is_stable_for_identical_content(tmp_path: Path) -> None:
    anchor = _fake_source_tree(tmp_path)

    first = identify_auditor(anchor)
    second = identify_auditor(anchor)

    assert first == second
    assert first.format == AUDITOR_IDENTITY_FORMAT
    assert len(first.sha256) == 64
    assert [item.path for item in first.files] == [
        ".github/workflows/scheduled-reaudit.yml",
        ".github/workflows/weave-audit.yml",
        "pyproject.toml",
        "scripts/audit_pr.py",
        "scripts/reaudit_stale.py",
        "src/weave_loupe/audit.py",
        "uv.lock",
    ]


def test_auditor_identity_changes_with_code_lockfile_or_workflow(
    tmp_path: Path,
) -> None:
    anchor = _fake_source_tree(tmp_path)
    original = identify_auditor(anchor)

    anchor.write_text("VALUE = 2\n", encoding="utf-8")
    code_changed = identify_auditor(anchor)
    (tmp_path / "uv.lock").write_text("version = 2\n", encoding="utf-8")
    lock_changed = identify_auditor(anchor)
    (tmp_path / ".github" / "workflows" / "weave-audit.yml").write_text(
        "name: stronger-audit\n", encoding="utf-8"
    )
    workflow_changed = identify_auditor(anchor)

    assert code_changed.sha256 != original.sha256
    assert lock_changed.sha256 != code_changed.sha256
    assert workflow_changed.sha256 != lock_changed.sha256


def test_nonsemantic_files_do_not_change_auditor_identity(tmp_path: Path) -> None:
    anchor = _fake_source_tree(tmp_path)
    original = identify_auditor(anchor)

    (tmp_path / "src" / "weave_loupe" / "ignored.txt").write_text(
        "changed\n", encoding="utf-8"
    )
    (tmp_path / "docs.md").write_text("changed documentation\n", encoding="utf-8")

    assert identify_auditor(anchor) == original


def test_sha256_file_streams_exact_bytes(tmp_path: Path) -> None:
    path = tmp_path / "binary"
    path.write_bytes(b"\x00audit\xff")

    assert sha256_file(path) == (
        "8a4f3ca9e9af05d6845b55b8f9f25f2812b8654f4f0769b328e86f584ec7ea69"
    )
