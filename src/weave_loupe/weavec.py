"""Helpers for invoking the public ``weavec build`` artifact interface."""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence


class WeavecError(RuntimeError):
    """Raised when weavec cannot be found or cannot be invoked."""


@dataclass(frozen=True)
class BuildRequest:
    """Paths used by one instrumented compiler invocation."""

    sources: tuple[Path, ...]
    executable: Path
    wir: Path
    llvm: Path
    diagnostics: Path
    trace: Path
    build_manifest: Path


@dataclass(frozen=True)
class BuildResult:
    """Result of one instrumented compiler invocation."""

    request: BuildRequest
    command: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str


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
) -> BuildResult:
    """Run ``weavec build`` and retain output even when compilation fails."""
    if not request.sources:
        raise WeavecError("at least one Weave source is required")
    for source in request.sources:
        if not source.is_file():
            raise WeavecError(f"weave source not found: {source}")

    binary = resolve_weavec(weavec)
    command = build_command(binary, request)
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            env=dict(environment) if environment is not None else None,
        )
    except OSError as exc:
        raise WeavecError(f"could not run weavec: {exc}") from exc

    return BuildResult(
        request=request,
        command=command,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def normalize_sources(sources: Sequence[Path]) -> tuple[Path, ...]:
    """Resolve and validate ordered source paths."""
    normalized = tuple(source.expanduser() for source in sources)
    if not normalized:
        raise WeavecError("at least one Weave source is required")
    for source in normalized:
        if not source.is_file():
            raise WeavecError(f"weave source not found: {source}")
    return normalized
