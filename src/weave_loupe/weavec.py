"""Helpers for invoking the public ``weavec build`` artifact interface."""

from __future__ import annotations

import os
import shutil
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from weave_loupe.bounded_process import (
    ProcessExecutionError,
    ProcessLimitError,
    ProcessLimits,
    ProcessResult,
    configured_process_limits,
    run_bounded_process,
)
from weave_loupe.process_budget import with_user_process_baseline


class WeavecError(RuntimeError):
    """Raised when weavec cannot be found or cannot be invoked."""


@dataclass(frozen=True)
class BuildRequest:
    """Paths used by one instrumented compiler invocation."""

    sources: tuple[Path, ...]
    executable: Path
    wir: Path
    llvm: Path
    optimized_llvm: Path
    assembly: Path
    disassembly: Path
    optimization_record: Path
    diagnostics: Path
    trace: Path
    build_manifest: Path


@dataclass(frozen=True)
class BuildResult:
    """Result of one instrumented compiler invocation."""

    request: BuildRequest
    execution: ProcessResult

    @property
    def command(self) -> tuple[str, ...]:
        """Return the exact host command passed to the bounded runner."""
        return self.execution.command

    @property
    def returncode(self) -> int:
        """Return a stable shell-compatible result code."""
        if self.execution.exit_code is not None:
            return self.execution.exit_code
        if self.execution.termination_reason == "timed_out":
            return 124
        if self.execution.termination_reason == "output_limit":
            return 125
        if self.execution.signal is not None:
            return 128 + self.execution.signal
        return 1

    @property
    def stdout(self) -> str:
        """Return the bounded compiler stdout excerpt."""
        return self.execution.stdout.text

    @property
    def stderr(self) -> str:
        """Return the bounded compiler stderr excerpt."""
        return self.execution.stderr.text


def resolve_weavec(explicit: Path | None = None) -> Path:
    """Resolve the compiler from an explicit path, ``WEAVEC_BIN``, or ``PATH``."""
    if explicit is not None:
        path = explicit.expanduser().resolve()
        if not path.is_file():
            raise WeavecError(f"weavec binary not found: {path}")
        return path

    env = os.environ.get("WEAVEC_BIN")
    if env:
        path = Path(env).expanduser().resolve()
        if not path.is_file():
            raise WeavecError(f"WEAVEC_BIN does not point to a file: {path}")
        return path

    found = shutil.which("weavec")
    if found is None:
        raise WeavecError("weavec not found; set WEAVEC_BIN or add weavec to PATH")
    return Path(found).resolve()


def build_command(binary: Path, request: BuildRequest) -> tuple[str, ...]:
    """Return the stable public command used to capture compiler evidence."""
    return (
        str(binary),
        "build",
        *(str(source) for source in request.sources),
        "-o",
        str(request.executable),
        "--emit-wir",
        str(request.wir),
        "--emit-llvm",
        str(request.llvm),
        "--emit-optimized-llvm",
        str(request.optimized_llvm),
        "--emit-assembly",
        str(request.assembly),
        "--emit-disassembly",
        str(request.disassembly),
        "--optimization-record",
        str(request.optimization_record),
        "-O3",
        "--native",
        "--diagnostics-json",
        str(request.diagnostics),
        "--trace-json",
        str(request.trace),
        "--manifest-json",
        str(request.build_manifest),
        "--llvm-provenance",
    )


def run_build(
    request: BuildRequest,
    *,
    weavec: Path | None = None,
    environment: Mapping[str, str] | None = None,
    limits: ProcessLimits | None = None,
    timeout_seconds: float | None = None,
    output_bytes: int | None = None,
) -> BuildResult:
    """Run ``weavec build`` with bounded resources and diagnostic evidence."""
    if not request.sources:
        raise WeavecError("at least one Weave source is required")
    for source in request.sources:
        if not source.is_file():
            raise WeavecError(f"weave source not found: {source}")
    if limits is not None and (timeout_seconds is not None or output_bytes is not None):
        raise WeavecError(
            "explicit process limits cannot be combined with timeout or output options"
        )

    binary = resolve_weavec(weavec)
    command = build_command(binary, request)
    try:
        configured_limits = limits or configured_process_limits(
            "compiler",
            timeout_seconds=timeout_seconds,
            output_bytes=output_bytes,
        )
        effective_limits = with_user_process_baseline(configured_limits)
        execution = run_bounded_process(
            command,
            limits=effective_limits,
            environment=environment,
        )
    except (ProcessExecutionError, ProcessLimitError) as exc:
        raise WeavecError(str(exc)) from exc

    return BuildResult(request=request, execution=execution)


def normalize_sources(sources: Sequence[Path]) -> tuple[Path, ...]:
    """Resolve and validate ordered source paths."""
    normalized = tuple(source.expanduser().resolve() for source in sources)
    if not normalized:
        raise WeavecError("at least one Weave source is required")
    for source in normalized:
        if not source.is_file():
            raise WeavecError(f"weave source not found: {source}")
    return normalized
