"""Tests for fail-closed native runtime isolation."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from weave_loupe.runtime_sandbox import (
    RuntimeSandbox,
    RuntimeSandboxError,
    sandbox_input_path,
    select_runtime_sandbox,
)


def _bubblewrap_namespaces_available() -> bool:
    binary = shutil.which("bwrap")
    limiter = shutil.which("prlimit")
    true_binary = shutil.which("true")
    if binary is None or limiter is None or true_binary is None:
        return False
    try:
        completed = subprocess.run(
            [
                binary,
                "--die-with-parent",
                "--unshare-all",
                "--ro-bind",
                "/",
                "/",
                "--",
                true_binary,
            ],
            capture_output=True,
            check=False,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return completed.returncode == 0


def test_sandbox_is_required_without_local_override(monkeypatch) -> None:
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.delenv("WEAVE_LOUPE_BWRAP", raising=False)
    monkeypatch.delenv("WEAVE_LOUPE_PRLIMIT", raising=False)
    monkeypatch.delenv("WEAVE_LOUPE_UNSAFE_NO_SANDBOX", raising=False)
    with (
        patch("weave_loupe.runtime_sandbox.shutil.which", return_value=None),
        pytest.raises(RuntimeSandboxError, match="bubblewrap is required"),
    ):
        select_runtime_sandbox()


def test_sandbox_requires_prlimit(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.delenv("WEAVE_LOUPE_BWRAP", raising=False)
    monkeypatch.delenv("WEAVE_LOUPE_PRLIMIT", raising=False)
    monkeypatch.delenv("WEAVE_LOUPE_UNSAFE_NO_SANDBOX", raising=False)
    bwrap = tmp_path / "bwrap"
    bwrap.write_text("fixture", encoding="utf-8")
    bwrap.chmod(0o755)

    def resolve(command: str) -> str | None:
        return str(bwrap) if command == "bwrap" else None

    with (
        patch("weave_loupe.runtime_sandbox.shutil.which", side_effect=resolve),
        pytest.raises(RuntimeSandboxError, match="prlimit is required"),
    ):
        select_runtime_sandbox()


def test_explicit_unsafe_override_is_local_only(monkeypatch) -> None:
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.delenv("WEAVE_LOUPE_BWRAP", raising=False)
    monkeypatch.delenv("WEAVE_LOUPE_PRLIMIT", raising=False)
    monkeypatch.setenv("WEAVE_LOUPE_UNSAFE_NO_SANDBOX", "1")
    with patch("weave_loupe.runtime_sandbox.shutil.which", return_value=None):
        sandbox = select_runtime_sandbox()

    assert sandbox.active is False
    assert sandbox.metadata()["backend"] == "unsafe-direct"
    assert sandbox.metadata()["process_count_enforcement"] == "runner-rlimit"


def test_explicit_unsafe_override_is_rejected_in_ci(monkeypatch) -> None:
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.delenv("WEAVE_LOUPE_BWRAP", raising=False)
    monkeypatch.delenv("WEAVE_LOUPE_PRLIMIT", raising=False)
    monkeypatch.setenv("WEAVE_LOUPE_UNSAFE_NO_SANDBOX", "true")
    with (
        patch("weave_loupe.runtime_sandbox.shutil.which", return_value=None),
        pytest.raises(RuntimeSandboxError, match="forbidden in GitHub Actions"),
    ):
        select_runtime_sandbox()


def test_bubblewrap_command_delegates_process_limit(
    tmp_path: Path,
) -> None:
    binary = tmp_path / "bwrap"
    limiter = tmp_path / "prlimit"
    executable = tmp_path / "program"
    source = tmp_path / "demo.weave"
    for path in (binary, limiter, executable, source):
        path.write_text("fixture", encoding="utf-8")
        path.chmod(0o755)

    sandbox = RuntimeSandbox(
        backend="bubblewrap",
        active=True,
        binary=binary,
        process_limiter=limiter,
    )
    invocation = sandbox.prepare(
        executable=executable,
        arguments=("--value",),
        inputs=(source,),
        environment={"VISIBLE": "yes"},
        working_directory=tmp_path,
        process_count_limit=123,
    )

    command = invocation.command
    assert "--unshare-all" in command
    assert "--clearenv" in command
    assert command[command.index("VISIBLE") - 1 : command.index("VISIBLE") + 2] == (
        "--setenv",
        "VISIBLE",
        "yes",
    )
    assert str(source.resolve()) in command
    assert sandbox_input_path(0, source) in command
    limiter_index = command.index(str(limiter))
    assert command[limiter_index : limiter_index + 5] == (
        str(limiter),
        "--nproc=123:123",
        "--",
        "/work/program",
        "--value",
    )
    assert command.index("--unshare-all") < limiter_index
    assert sandbox.metadata()["process_count_enforcement"] == "sandbox-prlimit"
    assert invocation.environment == {}
    assert invocation.working_directory is None


def test_bubblewrap_requires_positive_process_limit(tmp_path: Path) -> None:
    binary = tmp_path / "bwrap"
    limiter = tmp_path / "prlimit"
    executable = tmp_path / "program"
    for path in (binary, limiter, executable):
        path.write_text("fixture", encoding="utf-8")
        path.chmod(0o755)
    sandbox = RuntimeSandbox(
        backend="bubblewrap",
        active=True,
        binary=binary,
        process_limiter=limiter,
    )

    with pytest.raises(RuntimeSandboxError, match="positive process-count"):
        sandbox.prepare(
            executable=executable,
            arguments=(),
            inputs=(),
            environment={},
            working_directory=tmp_path,
            process_count_limit=None,
        )


@pytest.mark.skipif(
    not _bubblewrap_namespaces_available(),
    reason="bubblewrap namespace isolation is unavailable",
)
def test_bubblewrap_hides_host_files_and_network(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("WEAVE_LOUPE_UNSAFE_NO_SANDBOX", raising=False)
    executable = tmp_path / "probe.py"
    executable.write_text(
        """#!/usr/bin/python3
import pathlib
import socket
import sys

canary = pathlib.Path(sys.argv[1])
read_only = pathlib.Path(sys.argv[2])
if canary.exists():
    raise SystemExit(10)
try:
    read_only.write_text("changed", encoding="utf-8")
except OSError:
    pass
else:
    raise SystemExit(11)
probe = socket.socket()
probe.settimeout(0.2)
try:
    probe.connect(("1.1.1.1", 53))
except OSError:
    pass
else:
    raise SystemExit(12)
""",
        encoding="utf-8",
    )
    executable.chmod(0o755)
    canary = tmp_path / "host-secret"
    canary.write_text("secret", encoding="utf-8")
    declared_input = tmp_path / "input.txt"
    declared_input.write_text("original", encoding="utf-8")

    sandbox = select_runtime_sandbox()
    invocation = sandbox.prepare(
        executable=executable,
        arguments=(str(canary), sandbox_input_path(0, declared_input)),
        inputs=(declared_input,),
        environment={},
        working_directory=tmp_path,
        process_count_limit=4096,
    )
    completed = subprocess.run(
        invocation.command,
        cwd=invocation.working_directory,
        env=invocation.environment,
        capture_output=True,
        check=False,
        timeout=10,
    )

    assert completed.returncode == 0, completed.stderr.decode(errors="replace")
    assert declared_input.read_text(encoding="utf-8") == "original"
