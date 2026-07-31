"""Bounded subprocess execution with process-tree cleanup and evidence."""

from __future__ import annotations

import hashlib
import math
import os
import resource
import selectors
import signal
import subprocess
import tempfile
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import IO, Literal, cast

PROCESS_RESULT_FORMAT = "weave-loupe-process-result-v1"
PROCESS_LIMITS_FORMAT = "weave-loupe-process-limits-v1"
_READ_SIZE = 64 * 1024
_POLL_SECONDS = 0.05
_TERMINATION_GRACE_SECONDS = 0.5

ProcessKind = Literal["compiler", "runtime"]


class ProcessLimitError(ValueError):
    """Raised when configured subprocess limits are invalid."""


class ProcessExecutionError(RuntimeError):
    """Raised when a bounded subprocess cannot be launched or observed."""


@dataclass(frozen=True)
class ProcessLimits:
    """Effective limits for one external process tree."""

    timeout_seconds: float
    output_bytes: int
    excerpt_bytes: int
    cpu_seconds: float
    address_space_bytes: int
    file_size_bytes: int
    process_count: int

    def validate(self) -> ProcessLimits:
        """Validate every limit and return this immutable value."""
        _positive_number(self.timeout_seconds, "timeout_seconds")
        _positive_integer(self.output_bytes, "output_bytes")
        _positive_integer(self.excerpt_bytes, "excerpt_bytes")
        _positive_number(self.cpu_seconds, "cpu_seconds")
        _positive_integer(self.address_space_bytes, "address_space_bytes")
        _positive_integer(self.file_size_bytes, "file_size_bytes")
        _positive_integer(self.process_count, "process_count")
        if self.excerpt_bytes > self.output_bytes:
            raise ProcessLimitError("excerpt_bytes must not exceed output_bytes")
        return self

    def as_dict(self) -> dict[str, object]:
        """Return versioned machine-readable limit evidence."""
        return {
            "format": PROCESS_LIMITS_FORMAT,
            "timeout_seconds": self.timeout_seconds,
            "output_bytes_per_stream": self.output_bytes,
            "excerpt_bytes_per_stream": self.excerpt_bytes,
            "cpu_seconds": self.cpu_seconds,
            "address_space_bytes": self.address_space_bytes,
            "file_size_bytes": self.file_size_bytes,
            "process_count": self.process_count,
            "resource_limits_supported": os.name == "posix",
        }


@dataclass(frozen=True)
class StreamCapture:
    """Bounded evidence for one subprocess byte stream."""

    text: str
    sha256: str
    observed_bytes: int
    stored_bytes: int
    truncated_bytes: int
    overflowed: bool

    def as_dict(self) -> dict[str, object]:
        """Return deterministic stream evidence."""
        return {
            "text": self.text,
            "sha256": self.sha256,
            "observed_bytes": self.observed_bytes,
            "stored_bytes": self.stored_bytes,
            "truncated_bytes": self.truncated_bytes,
            "overflowed": self.overflowed,
        }


@dataclass(frozen=True)
class ProcessResult:
    """Complete bounded execution evidence."""

    command: tuple[str, ...]
    returncode: int | None
    termination_reason: str
    signal: int | None
    elapsed_seconds: float
    limits: ProcessLimits
    process_count_enforcement: str
    stdout: StreamCapture
    stderr: StreamCapture
    overflow_streams: tuple[str, ...]

    @property
    def exit_code(self) -> int | None:
        """Return a normal exit code, excluding signal termination."""
        if self.returncode is None or self.returncode < 0:
            return None
        return self.returncode

    @property
    def succeeded(self) -> bool:
        """Whether the process exited normally with status zero."""
        return self.termination_reason == "exited" and self.returncode == 0

    def as_dict(self) -> dict[str, object]:
        """Return versioned machine-readable process evidence."""
        return {
            "format": PROCESS_RESULT_FORMAT,
            "termination_reason": self.termination_reason,
            "exit_code": self.exit_code,
            "returncode": self.returncode,
            "signal": self.signal,
            "elapsed_seconds": self.elapsed_seconds,
            "overflow_streams": list(self.overflow_streams),
            "limits": self.limits.as_dict(),
            "process_count_enforcement": self.process_count_enforcement,
            "stdout": self.stdout.as_dict(),
            "stderr": self.stderr.as_dict(),
        }


_DEFAULTS: dict[ProcessKind, ProcessLimits] = {
    "compiler": ProcessLimits(
        timeout_seconds=120.0,
        output_bytes=8 * 1024 * 1024,
        excerpt_bytes=64 * 1024,
        cpu_seconds=120.0,
        address_space_bytes=4 * 1024 * 1024 * 1024,
        file_size_bytes=1024 * 1024 * 1024,
        process_count=256,
    ),
    "runtime": ProcessLimits(
        timeout_seconds=5.0,
        output_bytes=1024 * 1024,
        excerpt_bytes=16 * 1024,
        cpu_seconds=6.0,
        address_space_bytes=512 * 1024 * 1024,
        file_size_bytes=64 * 1024 * 1024,
        process_count=64,
    ),
}


def configured_process_limits(
    kind: ProcessKind,
    *,
    default_timeout_seconds: float | None = None,
    timeout_seconds: float | None = None,
    output_bytes: int | None = None,
    environment: Mapping[str, str] | None = None,
) -> ProcessLimits:
    """Resolve CLI, environment, and conservative default process limits."""
    defaults = _DEFAULTS[kind]
    values = os.environ if environment is None else environment
    prefix = f"WEAVE_LOUPE_{kind.upper()}"
    default_timeout = (
        defaults.timeout_seconds
        if default_timeout_seconds is None
        else default_timeout_seconds
    )
    timeout = _precedence_float(
        timeout_seconds,
        values.get(f"{prefix}_TIMEOUT_SECONDS"),
        default_timeout,
        f"{prefix}_TIMEOUT_SECONDS",
    )
    output = _precedence_int(
        output_bytes,
        values.get(f"{prefix}_OUTPUT_BYTES"),
        defaults.output_bytes,
        f"{prefix}_OUTPUT_BYTES",
    )
    excerpt = _environment_int(
        values.get(f"{prefix}_EXCERPT_BYTES"),
        min(defaults.excerpt_bytes, output),
        f"{prefix}_EXCERPT_BYTES",
    )
    cpu_default = max(defaults.cpu_seconds, math.ceil(timeout) + 1.0)
    limits = ProcessLimits(
        timeout_seconds=timeout,
        output_bytes=output,
        excerpt_bytes=excerpt,
        cpu_seconds=_environment_float(
            values.get(f"{prefix}_CPU_SECONDS"),
            cpu_default,
            f"{prefix}_CPU_SECONDS",
        ),
        address_space_bytes=_environment_int(
            values.get(f"{prefix}_ADDRESS_SPACE_BYTES"),
            defaults.address_space_bytes,
            f"{prefix}_ADDRESS_SPACE_BYTES",
        ),
        file_size_bytes=_environment_int(
            values.get(f"{prefix}_FILE_SIZE_BYTES"),
            defaults.file_size_bytes,
            f"{prefix}_FILE_SIZE_BYTES",
        ),
        process_count=_environment_int(
            values.get(f"{prefix}_PROCESS_COUNT"),
            defaults.process_count,
            f"{prefix}_PROCESS_COUNT",
        ),
    )
    return limits.validate()


def run_bounded_process(
    command: Sequence[str],
    *,
    limits: ProcessLimits,
    input_bytes: bytes = b"",
    cwd: Path | None = None,
    environment: Mapping[str, str] | None = None,
    apply_process_count_limit: bool = True,
) -> ProcessResult:
    """Run one process tree while bounding time, resources, and output."""
    effective = limits.validate()
    if not command:
        raise ProcessExecutionError("subprocess command must not be empty")
    normalized_command = tuple(str(argument) for argument in command)
    stdout_capture = _StreamAccumulator(
        effective.output_bytes,
        effective.excerpt_bytes,
    )
    stderr_capture = _StreamAccumulator(
        effective.output_bytes,
        effective.excerpt_bytes,
    )
    start = time.monotonic()

    with tempfile.TemporaryFile() as stdin_file:
        stdin_file.write(input_bytes)
        stdin_file.seek(0)
        try:
            process = subprocess.Popen(
                normalized_command,
                stdin=stdin_file,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cwd,
                env=dict(environment) if environment is not None else None,
                start_new_session=os.name == "posix",
                preexec_fn=_resource_limiter(
                    effective,
                    apply_process_count_limit=apply_process_count_limit,
                ),
            )
        except OSError as exc:
            raise ProcessExecutionError(
                f"could not launch {Path(normalized_command[0]).name}: {exc}"
            ) from exc

        forced_reason: str | None = None
        overflow_streams: set[str] = set()
        termination_started: float | None = None
        kill_sent = False
        selector = selectors.DefaultSelector()
        try:
            streams = (
                ("stdout", process.stdout, stdout_capture),
                ("stderr", process.stderr, stderr_capture),
            )
            for name, stream, accumulator in streams:
                if stream is None:
                    continue
                os.set_blocking(stream.fileno(), False)
                selector.register(
                    stream,
                    selectors.EVENT_READ,
                    _RegisteredStream(name, accumulator, stream),
                )

            deadline = start + effective.timeout_seconds
            while selector.get_map():
                now = time.monotonic()
                if forced_reason is None and now >= deadline:
                    forced_reason = "timed_out"
                    termination_started = now
                    _signal_process_tree(process, signal.SIGTERM)
                if (
                    termination_started is not None
                    and not kill_sent
                    and process.poll() is None
                    and now - termination_started >= _TERMINATION_GRACE_SECONDS
                ):
                    _signal_process_tree(process, signal.SIGKILL)
                    kill_sent = True

                wait = _POLL_SECONDS
                if forced_reason is None:
                    wait = min(wait, max(0.0, deadline - now))
                events = selector.select(wait)
                for key, _ in events:
                    registration = cast(_RegisteredStream, key.data)
                    try:
                        chunk = os.read(registration.stream.fileno(), _READ_SIZE)
                    except BlockingIOError:
                        continue
                    if not chunk:
                        selector.unregister(registration.stream)
                        registration.stream.close()
                        continue
                    registration.accumulator.append(chunk)
                    if registration.accumulator.overflowed:
                        overflow_streams.add(registration.name)
                        if forced_reason is None:
                            forced_reason = "output_limit"
                            termination_started = time.monotonic()
                            _signal_process_tree(process, signal.SIGTERM)

                if process.poll() is not None and not events:
                    time.sleep(0.001)
        except BaseException:
            _terminate_process_tree(process)
            raise
        finally:
            selector.close()

        if process.poll() is None:
            _terminate_process_tree(process)
        try:
            returncode = process.wait(timeout=1.0)
        except subprocess.TimeoutExpired:
            _signal_process_tree(process, signal.SIGKILL)
            returncode = process.wait(timeout=1.0)

    elapsed = time.monotonic() - start
    signal_number = -returncode if returncode < 0 else None
    if forced_reason is not None:
        termination_reason = forced_reason
    elif signal_number is not None:
        termination_reason = "signaled"
    else:
        termination_reason = "exited"
    process_count_enforcement = (
        "runner-rlimit" if apply_process_count_limit else "delegated"
    )
    return ProcessResult(
        command=normalized_command,
        returncode=returncode,
        termination_reason=termination_reason,
        signal=signal_number,
        elapsed_seconds=round(elapsed, 6),
        limits=effective,
        process_count_enforcement=process_count_enforcement,
        stdout=stdout_capture.finish(),
        stderr=stderr_capture.finish(),
        overflow_streams=tuple(sorted(overflow_streams)),
    )


@dataclass(frozen=True)
class _RegisteredStream:
    name: str
    accumulator: _StreamAccumulator
    stream: IO[bytes]


class _StreamAccumulator:
    def __init__(self, maximum: int, excerpt: int) -> None:
        self.maximum = maximum
        self.excerpt = excerpt
        self.observed = 0
        self.stored = 0
        self.overflowed = False
        self.digest = hashlib.sha256()
        self.spool = tempfile.TemporaryFile()

    def append(self, chunk: bytes) -> None:
        self.digest.update(chunk)
        self.observed += len(chunk)
        remaining = max(0, self.maximum - self.stored)
        if remaining:
            retained = chunk[:remaining]
            self.spool.write(retained)
            self.stored += len(retained)
        if self.observed > self.maximum:
            self.overflowed = True

    def finish(self) -> StreamCapture:
        self.spool.seek(0)
        excerpt = self.spool.read(self.excerpt)
        text = excerpt.decode("utf-8", errors="replace")
        truncated = max(0, self.observed - len(excerpt))
        if truncated:
            text += f"\n...[truncated {truncated} bytes]"
        self.spool.close()
        return StreamCapture(
            text=text,
            sha256=self.digest.hexdigest(),
            observed_bytes=self.observed,
            stored_bytes=self.stored,
            truncated_bytes=truncated,
            overflowed=self.overflowed,
        )


def _resource_limiter(
    limits: ProcessLimits,
    *,
    apply_process_count_limit: bool,
) -> Callable[[], None] | None:
    if os.name != "posix":
        return None

    def apply_limits() -> None:
        _set_resource_limit(resource.RLIMIT_CORE, 0, 0)
        cpu = max(1, math.ceil(limits.cpu_seconds))
        _set_resource_limit(resource.RLIMIT_CPU, cpu, cpu + 1)
        _set_resource_limit(
            resource.RLIMIT_AS,
            limits.address_space_bytes,
            limits.address_space_bytes,
        )
        _set_resource_limit(
            resource.RLIMIT_FSIZE,
            limits.file_size_bytes,
            limits.file_size_bytes,
        )
        if apply_process_count_limit:
            _set_resource_limit(
                resource.RLIMIT_NPROC,
                limits.process_count,
                limits.process_count,
            )

    return apply_limits


def _set_resource_limit(resource_id: int, soft: int, hard: int) -> None:
    current_soft, current_hard = resource.getrlimit(resource_id)
    if current_hard != resource.RLIM_INFINITY:
        hard = min(hard, current_hard)
    if current_soft != resource.RLIM_INFINITY:
        soft = min(soft, current_soft)
    soft = min(soft, hard)
    resource.setrlimit(resource_id, (soft, hard))


def _terminate_process_tree(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    _signal_process_tree(process, signal.SIGTERM)
    try:
        process.wait(timeout=_TERMINATION_GRACE_SECONDS)
    except subprocess.TimeoutExpired:
        _signal_process_tree(process, signal.SIGKILL)
        process.wait(timeout=1.0)


def _signal_process_tree(
    process: subprocess.Popen[bytes],
    sig: signal.Signals,
) -> None:
    if process.poll() is not None:
        return
    try:
        if os.name == "posix":
            os.killpg(process.pid, sig)
        else:
            process.send_signal(sig)
    except ProcessLookupError:
        return


def _precedence_float(
    explicit: float | None,
    environment: str | None,
    default: float,
    name: str,
) -> float:
    if explicit is not None:
        return _positive_number(explicit, name)
    return _environment_float(environment, default, name)


def _precedence_int(
    explicit: int | None,
    environment: str | None,
    default: int,
    name: str,
) -> int:
    if explicit is not None:
        return _positive_integer(explicit, name)
    return _environment_int(environment, default, name)


def _environment_float(raw: str | None, default: float, name: str) -> float:
    if raw is None:
        return _positive_number(default, name)
    try:
        value = float(raw)
    except ValueError as exc:
        raise ProcessLimitError(f"{name} must be a positive number") from exc
    return _positive_number(value, name)


def _environment_int(raw: str | None, default: int, name: str) -> int:
    if raw is None:
        return _positive_integer(default, name)
    try:
        value = int(raw)
    except ValueError as exc:
        raise ProcessLimitError(f"{name} must be a positive integer") from exc
    return _positive_integer(value, name)


def _positive_number(value: float, name: str) -> float:
    if not math.isfinite(value) or value <= 0:
        raise ProcessLimitError(f"{name} must be a positive finite number")
    return float(value)


def _positive_integer(value: int, name: str) -> int:
    if isinstance(value, bool) or value <= 0:
        raise ProcessLimitError(f"{name} must be a positive integer")
    return value
