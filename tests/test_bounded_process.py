"""Tests for bounded external process execution."""

from __future__ import annotations

import hashlib
import os
import signal
import sys
import time
from pathlib import Path

import pytest

from weave_loupe.bounded_process import (
    ProcessLimitError,
    ProcessLimits,
    configured_process_limits,
    run_bounded_process,
)
from weave_loupe.process_budget import with_user_process_baseline


def _limits(
    *,
    timeout: float = 2.0,
    output: int = 4096,
    excerpt: int = 1024,
) -> ProcessLimits:
    return ProcessLimits(
        timeout_seconds=timeout,
        output_bytes=output,
        excerpt_bytes=excerpt,
        cpu_seconds=max(2.0, timeout + 1.0),
        address_space_bytes=1024 * 1024 * 1024,
        file_size_bytes=16 * 1024 * 1024,
        process_count=32,
    )


def test_bounded_process_records_successful_execution() -> None:
    result = run_bounded_process(
        [
            sys.executable,
            "-c",
            "import sys; sys.stdout.write('answer\\n'); "
            "sys.stderr.write('diagnostic\\n')",
        ],
        limits=_limits(),
    )

    assert result.succeeded is True
    assert result.termination_reason == "exited"
    assert result.exit_code == 0
    assert result.signal is None
    assert result.process_count_enforcement == "runner-rlimit"
    assert result.stdout.text == "answer\n"
    assert result.stderr.text == "diagnostic\n"
    assert result.stdout.sha256 == hashlib.sha256(b"answer\n").hexdigest()
    assert result.stdout.observed_bytes == 7
    assert result.as_dict()["format"] == "weave-loupe-process-result-v1"


def test_bounded_process_records_delegated_process_limit() -> None:
    result = run_bounded_process(
        [sys.executable, "-c", "raise SystemExit(0)"],
        limits=_limits(),
        apply_process_count_limit=False,
    )

    assert result.succeeded is True
    assert result.process_count_enforcement == "delegated"
    assert result.as_dict()["process_count_enforcement"] == "delegated"


def test_configured_limits_prefer_explicit_then_environment() -> None:
    environment = {
        "WEAVE_LOUPE_COMPILER_TIMEOUT_SECONDS": "9.5",
        "WEAVE_LOUPE_COMPILER_OUTPUT_BYTES": "2048",
        "WEAVE_LOUPE_COMPILER_EXCERPT_BYTES": "512",
        "WEAVE_LOUPE_COMPILER_CPU_SECONDS": "11",
        "WEAVE_LOUPE_COMPILER_ADDRESS_SPACE_BYTES": str(2 * 1024 * 1024),
        "WEAVE_LOUPE_COMPILER_FILE_SIZE_BYTES": str(1024 * 1024),
        "WEAVE_LOUPE_COMPILER_PROCESS_COUNT": "12",
    }

    configured = configured_process_limits(
        "compiler",
        timeout_seconds=3.0,
        environment=environment,
    )

    assert configured.timeout_seconds == 3.0
    assert configured.output_bytes == 2048
    assert configured.excerpt_bytes == 512
    assert configured.cpu_seconds == 11.0
    assert configured.process_count == 12


def test_configured_limits_reject_invalid_environment() -> None:
    with pytest.raises(ProcessLimitError, match="positive integer"):
        configured_process_limits(
            "runtime",
            environment={"WEAVE_LOUPE_RUNTIME_OUTPUT_BYTES": "unbounded"},
        )


def test_process_limits_reject_excerpt_larger_than_output() -> None:
    with pytest.raises(ProcessLimitError, match="must not exceed"):
        _limits(output=10, excerpt=11).validate()


def test_bounded_process_terminates_on_timeout() -> None:
    result = run_bounded_process(
        [sys.executable, "-c", "while True: pass"],
        limits=_limits(timeout=0.2),
    )

    assert result.termination_reason == "timed_out"
    assert result.exit_code is None
    assert result.signal in {signal.SIGTERM, signal.SIGKILL}
    assert result.elapsed_seconds < 2.0


def test_bounded_process_stops_output_overflow() -> None:
    result = run_bounded_process(
        [
            sys.executable,
            "-c",
            "import sys; sys.stdout.buffer.write(b'x' * 100000); "
            "sys.stdout.buffer.flush()",
        ],
        limits=_limits(output=1024, excerpt=64),
    )

    assert result.termination_reason == "output_limit"
    assert result.overflow_streams == ("stdout",)
    assert result.stdout.overflowed is True
    assert result.stdout.observed_bytes > 1024
    assert result.stdout.stored_bytes == 1024
    assert "truncated" in result.stdout.text


def test_bounded_process_records_signal_termination() -> None:
    result = run_bounded_process(
        [
            sys.executable,
            "-c",
            "import os, signal; os.kill(os.getpid(), signal.SIGTERM)",
        ],
        limits=_limits(),
    )

    assert result.termination_reason == "signaled"
    assert result.signal == signal.SIGTERM
    assert result.exit_code is None


@pytest.mark.skipif(
    os.name != "posix" or not Path("/proc").is_dir(),
    reason="process-tree probe requires Linux /proc",
)
def test_timeout_terminates_forked_descendants(tmp_path: Path) -> None:
    child_pid_file = tmp_path / "child.pid"
    script = tmp_path / "fork_tree.py"
    script.write_text(
        """import os
import pathlib
import time

child = os.fork()
if child == 0:
    while True:
        time.sleep(1)
pathlib.Path(os.environ["CHILD_PID_FILE"]).write_text(str(child))
while True:
    time.sleep(1)
""",
        encoding="utf-8",
    )

    result = run_bounded_process(
        [sys.executable, str(script)],
        limits=with_user_process_baseline(_limits(timeout=0.5)),
        environment={"CHILD_PID_FILE": str(child_pid_file)},
    )

    assert result.termination_reason == "timed_out"
    child_pid = int(child_pid_file.read_text(encoding="utf-8"))
    child_proc = Path("/proc") / str(child_pid)
    deadline = time.monotonic() + 2.0
    while child_proc.exists() and time.monotonic() < deadline:
        time.sleep(0.02)
    assert not child_proc.exists()
