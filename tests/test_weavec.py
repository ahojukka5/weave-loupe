"""Tests for compiler invocation helpers."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from weave_loupe.weavec import (
    BuildRequest,
    WeavecError,
    build_command,
    normalize_sources,
    resolve_weavec,
    run_build,
)


def _request(tmp_path: Path, source: Path) -> BuildRequest:
    return BuildRequest(
        sources=(source,),
        executable=tmp_path / "program",
        wir=tmp_path / "program.wir",
        llvm=tmp_path / "program.ll",
        diagnostics=tmp_path / "diagnostics.json",
        trace=tmp_path / "trace.json",
        build_manifest=tmp_path / "build.json",
    )


def test_resolve_weavec_explicit(fake_weavec: Path) -> None:
    assert resolve_weavec(fake_weavec) == fake_weavec.resolve()


def test_resolve_weavec_env(fake_weavec: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WEAVEC_BIN", str(fake_weavec))
    assert resolve_weavec() == fake_weavec.resolve()


def test_resolve_weavec_path(
    fake_weavec: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("WEAVEC_BIN", raising=False)
    with patch("weave_loupe.weavec.shutil.which", return_value=str(fake_weavec)):
        assert resolve_weavec() == fake_weavec.resolve()


def test_resolve_weavec_missing(tmp_path: Path) -> None:
    with pytest.raises(WeavecError, match="binary not found"):
        resolve_weavec(tmp_path / "missing")


def test_normalize_sources_requires_input() -> None:
    with pytest.raises(WeavecError, match="at least one"):
        normalize_sources([])


def test_normalize_sources_preserves_order(tmp_path: Path) -> None:
    left = tmp_path / "a.weave"
    right = tmp_path / "b.weave"
    left.write_text("a")
    right.write_text("b")
    assert normalize_sources([right, left]) == (right.resolve(), left.resolve())


def test_build_command_uses_public_artifact_flags(
    tmp_path: Path, source_file: Path, fake_weavec: Path
) -> None:
    command = build_command(fake_weavec, _request(tmp_path, source_file))
    assert command[1] == "build"
    assert "--emit-wir" in command
    assert "--emit-llvm" in command
    assert "--diagnostics-json" in command
    assert "--trace-json" in command
    assert "--manifest-json" in command
    assert command[-1] == "--llvm-provenance"


def test_run_build_retains_outputs(
    tmp_path: Path, source_file: Path, fake_weavec: Path
) -> None:
    request = _request(tmp_path, source_file)
    result = run_build(request, weavec=fake_weavec)
    assert result.returncode == 0
    assert result.stdout == "compiled\n"
    assert request.wir.is_file()
    assert request.llvm.is_file()
