"""Tests for weavec discovery and compilation helpers."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from weave_loupe.weavec import (
    CompilationArtifacts,
    WeavecError,
    compile_weave,
    resolve_weavec,
)


def test_resolve_weavec_explicit_path(tmp_path: Path) -> None:
    binary = tmp_path / "weavec"
    binary.write_text("#!/bin/sh\n", encoding="utf-8")
    binary.chmod(0o755)
    assert resolve_weavec(binary) == binary.resolve()


def test_resolve_weavec_missing_explicit_path(tmp_path: Path) -> None:
    with pytest.raises(WeavecError, match="weavec binary not found"):
        resolve_weavec(tmp_path / "missing")


def test_resolve_weavec_from_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    binary = tmp_path / "weavec"
    binary.write_text("#!/bin/sh\n", encoding="utf-8")
    monkeypatch.setenv("WEAVEC_BIN", str(binary))
    assert resolve_weavec() == binary.resolve()


def test_resolve_weavec_from_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    binary = tmp_path / "weavec"
    binary.write_text("#!/bin/sh\n", encoding="utf-8")
    monkeypatch.delenv("WEAVEC_BIN", raising=False)
    with patch("weave_loupe.weavec.shutil.which", return_value=str(binary)):
        assert resolve_weavec() == binary.resolve()


def test_resolve_weavec_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("WEAVEC_BIN", raising=False)
    with (
        patch("weave_loupe.weavec.shutil.which", return_value=None),
        pytest.raises(WeavecError, match="weavec not found"),
    ):
        resolve_weavec()


def test_compile_weave_runs_frontend_and_backend(tmp_path: Path) -> None:
    source = tmp_path / "demo.weave"
    source.write_text("(program)", encoding="utf-8")
    binary = tmp_path / "weavec"
    binary.write_text("#!/bin/sh\n", encoding="utf-8")

    def fake_run(cmd: list[str], *, label: str) -> None:
        del label
        if cmd[1] == "--frontend":
            Path(cmd[2]).write_text("(core-module)", encoding="utf-8")
        elif cmd[1] == "--backend":
            Path(cmd[3]).write_text("define i32 @main()", encoding="utf-8")
        else:
            raise AssertionError(cmd)

    with (
        patch("weave_loupe.weavec.resolve_weavec", return_value=binary),
        patch("weave_loupe.weavec._run", side_effect=fake_run) as run_mock,
    ):
        artifacts = compile_weave(source)

    assert artifacts == CompilationArtifacts(
        weave_source="(program)",
        wir="(core-module)",
        llvm_ir="define i32 @main()",
    )
    assert run_mock.call_count == 2
    assert run_mock.call_args_list[0].args[0][1] == "--frontend"
    assert run_mock.call_args_list[1].args[0][1] == "--backend"


def test_compile_weave_missing_source(tmp_path: Path) -> None:
    with pytest.raises(WeavecError, match="weave source not found"):
        compile_weave(tmp_path / "missing.weave")


def test_run_raises_on_nonzero_exit() -> None:
    from weave_loupe.weavec import _run

    result = SimpleNamespace(returncode=7, stderr="nope", stdout="")
    with (
        patch("weave_loupe.weavec.subprocess.run", return_value=result),
        pytest.raises(WeavecError, match="failed with exit 7"),
    ):
        _run(["weavec", "--frontend", "out.wir", "in.weave"], label="frontend")
