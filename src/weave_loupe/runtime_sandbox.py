"""Fail-closed isolation for native runtime audit cases."""

from __future__ import annotations

import os
import re
import shutil
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

SANDBOX_POLICY_FORMAT = "weave-loupe-runtime-sandbox-v1"
_SANDBOX_PROGRAM = "/work/program"
_SANDBOX_INPUT_ROOT = "/inputs"
_SYSTEM_PATHS = ("/usr", "/bin", "/lib", "/lib64", "/sbin")
_RUNTIME_FILES = (
    "/etc/ld.so.cache",
    "/etc/ld.so.conf",
    "/etc/ld.so.conf.d",
    "/etc/nsswitch.conf",
    "/etc/passwd",
    "/etc/group",
)
_SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]+")


class RuntimeSandboxError(RuntimeError):
    """Raised when secure runtime isolation is unavailable or invalid."""


@dataclass(frozen=True)
class SandboxInvocation:
    """One prepared host-side subprocess invocation."""

    command: tuple[str, ...]
    working_directory: Path | None
    environment: dict[str, str]


@dataclass(frozen=True)
class RuntimeSandbox:
    """Selected native runtime isolation backend and effective policy."""

    backend: str
    active: bool
    binary: Path | None
    process_limiter: Path | None = None

    def metadata(self) -> dict[str, object]:
        """Return stable evidence describing the effective isolation policy."""
        if self.active:
            return {
                "format": SANDBOX_POLICY_FORMAT,
                "active": True,
                "backend": self.backend,
                "network": "disabled",
                "filesystem": "read-only-system-and-declared-inputs",
                "writable_paths": ["/tmp", "/work"],
                "environment": "explicit-only",
                "namespaces": ["user", "network", "pid", "ipc", "uts", "cgroup"],
                "process_count_enforcement": "sandbox-prlimit",
            }
        return {
            "format": SANDBOX_POLICY_FORMAT,
            "active": False,
            "backend": self.backend,
            "network": "host",
            "filesystem": "host",
            "writable_paths": "host",
            "environment": "configured-direct-execution",
            "namespaces": [],
            "process_count_enforcement": "runner-rlimit",
        }

    def prepare(
        self,
        *,
        executable: Path,
        arguments: Sequence[str],
        inputs: Sequence[Path],
        environment: Mapping[str, str],
        working_directory: Path,
        process_count_limit: int | None = None,
    ) -> SandboxInvocation:
        """Prepare a sandboxed or explicitly unsafe native invocation."""
        if not self.active:
            return SandboxInvocation(
                command=(str(executable), *arguments),
                working_directory=working_directory,
                environment=dict(environment),
            )
        if self.binary is None:
            raise RuntimeSandboxError("sandbox backend is active without a binary")
        if self.process_limiter is None:
            raise RuntimeSandboxError(
                "sandbox backend is active without a process-count limiter"
            )
        if (
            not isinstance(process_count_limit, int)
            or isinstance(process_count_limit, bool)
            or process_count_limit <= 0
        ):
            raise RuntimeSandboxError(
                "sandboxed runtime requires a positive process-count limit"
            )

        command = [
            str(self.binary),
            "--die-with-parent",
            "--new-session",
            "--unshare-all",
            "--clearenv",
            "--proc",
            "/proc",
            "--dev",
            "/dev",
            "--tmpfs",
            "/tmp",
            "--dir",
            "/work",
            "--dir",
            _SANDBOX_INPUT_ROOT,
            "--dir",
            "/etc",
        ]
        for system_path in _SYSTEM_PATHS:
            command.extend(("--ro-bind-try", system_path, system_path))
        for runtime_path in _RUNTIME_FILES:
            command.extend(("--ro-bind-try", runtime_path, runtime_path))

        command.extend(("--ro-bind", str(executable.resolve()), _SANDBOX_PROGRAM))
        for index, input_path in enumerate(inputs):
            target = sandbox_input_path(index, input_path)
            command.extend(("--ro-bind", str(input_path.resolve()), target))

        command.extend(("--chdir", "/work"))
        defaults = {
            "HOME": "/nonexistent",
            "PATH": "/usr/bin:/bin",
            "TMPDIR": "/tmp",
        }
        for name, value in sorted({**defaults, **dict(environment)}.items()):
            command.extend(("--setenv", name, value))
        command.extend(
            (
                "--",
                str(self.process_limiter),
                f"--nproc={process_count_limit}:{process_count_limit}",
                "--",
                _SANDBOX_PROGRAM,
                *arguments,
            )
        )
        return SandboxInvocation(
            command=tuple(command),
            working_directory=None,
            environment={},
        )


def select_runtime_sandbox() -> RuntimeSandbox:
    """Select bubblewrap or fail unless an explicit local unsafe override is set."""
    allow_unsafe_unsandboxed = _environment_flag("WEAVE_LOUPE_UNSAFE_NO_SANDBOX")
    in_ci = os.environ.get("GITHUB_ACTIONS", "").lower() == "true"
    if allow_unsafe_unsandboxed and in_ci:
        raise RuntimeSandboxError(
            "unsandboxed native runtime execution is forbidden in GitHub Actions"
        )
    if allow_unsafe_unsandboxed:
        return RuntimeSandbox(backend="unsafe-direct", active=False, binary=None)

    binary = _resolve_executable(
        configured=os.environ.get("WEAVE_LOUPE_BWRAP"),
        command="bwrap",
        variable="WEAVE_LOUPE_BWRAP",
    )
    if binary is None:
        raise RuntimeSandboxError(
            "bubblewrap is required for native runtime cases; install bwrap or use "
            "WEAVE_LOUPE_UNSAFE_NO_SANDBOX=1 for an explicit local-only override"
        )
    process_limiter = _resolve_executable(
        configured=os.environ.get("WEAVE_LOUPE_PRLIMIT"),
        command="prlimit",
        variable="WEAVE_LOUPE_PRLIMIT",
    )
    if process_limiter is None:
        raise RuntimeSandboxError(
            "util-linux prlimit is required to enforce sandboxed process-count "
            "limits; install prlimit or configure WEAVE_LOUPE_PRLIMIT"
        )
    return RuntimeSandbox(
        backend="bubblewrap",
        active=True,
        binary=binary,
        process_limiter=process_limiter,
    )


def sandbox_input_path(index: int, path: Path) -> str:
    """Return the deterministic read-only path for one declared input."""
    safe_name = _SAFE_NAME.sub("_", path.name).strip("._") or "input"
    return f"{_SANDBOX_INPUT_ROOT}/{index:03d}-{safe_name}"


def _resolve_executable(
    *,
    configured: str | None,
    command: str,
    variable: str,
) -> Path | None:
    if configured:
        candidate = Path(configured).expanduser().resolve()
        if not candidate.is_file() or not os.access(candidate, os.X_OK):
            raise RuntimeSandboxError(
                f"{variable} is not an executable file: {candidate}"
            )
        return candidate
    found = shutil.which(command)
    return Path(found).resolve() if found is not None else None


def _environment_flag(name: str) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return False
    normalized = raw.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off", ""}:
        return False
    raise RuntimeSandboxError(
        f"{name} must be a boolean value such as 1, true, 0, or false"
    )
