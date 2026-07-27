"""Tests for compiler release and development build identification."""

from __future__ import annotations

from pathlib import Path

from weave_loupe.compiler_version import identify_weavec


def _script(path: Path, body: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("#!/bin/sh\n" + body, encoding="utf-8")
    path.chmod(0o755)
    return path


def test_identify_weavec_prefers_command_version(tmp_path: Path) -> None:
    binary = _script(tmp_path / "weavec", "echo 'weavec v0.4.0+git.abc123'\n")
    identity = identify_weavec(binary)
    assert identity.display == "weavec v0.4.0+git.abc123"
    assert identity.base == "v0.4.0"
    assert identity.git_sha == "abc123"
    assert identity.development
    assert identity.source == "command"


def test_identify_weavec_falls_back_to_version_file(tmp_path: Path) -> None:
    root = tmp_path / "package"
    binary = _script(root / "bin" / "weavec", "exit 1\n")
    (root / "VERSION").write_text("0.3.0\n", encoding="utf-8")
    identity = identify_weavec(binary)
    assert identity.display == "weavec v0.3.0"
    assert identity.base == "v0.3.0"
    assert identity.git_sha is None
    assert not identity.development
    assert identity.source == "version-file"
