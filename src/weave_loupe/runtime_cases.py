"""Declarative execution matrices for compiled audit programs."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from weave_loupe.bundle import Bundle

RUNTIME_CASES_FORMAT = "weave-loupe-runtime-cases-v1"
_RUNTIME_RESULT_FORMAT = "weave-loupe-runtime-matrix-v1"
_MAX_TIMEOUT_SECONDS = 60.0
_MAX_CAPTURE_BYTES = 16 * 1024


class RuntimeCasesError(ValueError):
    """Raised when a runtime matrix is invalid or cannot be executed."""


@dataclass(frozen=True)
class RuntimeCase:
    """One native-program invocation and its exact expected observations."""

    name: str
    args: tuple[str, ...]
    environment: dict[str, str | None]
    stdin: str
    expected_exit_code: int
    expected_stdout: str | None
    expected_stderr: str | None


@dataclass(frozen=True)
class RuntimeCases:
    """Validated sidecar configuration for one audit program."""

    path: Path
    timeout_seconds: float
    inherit_environment: bool
    cases: tuple[RuntimeCase, ...]


def discover_runtime_cases(sources: list[Path]) -> RuntimeCases | None:
    """Load the single ``*.audit.json`` sidecar adjacent to audited sources."""
    candidates = [source.with_suffix(".audit.json") for source in sources]
    existing = [candidate for candidate in candidates if candidate.is_file()]
    if not existing:
        return None
    if len(existing) > 1:
        names = ", ".join(str(path) for path in existing)
        raise RuntimeCasesError(f"multiple runtime case sidecars found: {names}")
    return load_runtime_cases(existing[0])


def load_runtime_cases(path: Path) -> RuntimeCases:
    """Parse and validate one versioned runtime-case document."""
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeCasesError(f"invalid runtime case file {path}: {exc}") from exc
    if not isinstance(document, dict):
        raise RuntimeCasesError("runtime case document must be a JSON object")
    if document.get("format") != RUNTIME_CASES_FORMAT:
        raise RuntimeCasesError(
            f"runtime case format must be {RUNTIME_CASES_FORMAT!r}"
        )

    timeout = document.get("timeout_seconds", 5)
    if not isinstance(timeout, int | float) or isinstance(timeout, bool):
        raise RuntimeCasesError("timeout_seconds must be a number")
    timeout_seconds = float(timeout)
    if not 0 < timeout_seconds <= _MAX_TIMEOUT_SECONDS:
        raise RuntimeCasesError(
            f"timeout_seconds must be in (0, {_MAX_TIMEOUT_SECONDS:g}]"
        )

    inherit = document.get("inherit_environment", False)
    if not isinstance(inherit, bool):
        raise RuntimeCasesError("inherit_environment must be a boolean")

    raw_cases = document.get("cases")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise RuntimeCasesError("runtime case document must contain a non-empty cases list")

    cases = tuple(_parse_case(item, index) for index, item in enumerate(raw_cases))
    names = [case.name for case in cases]
    if len(names) != len(set(names)):
        raise RuntimeCasesError("runtime case names must be unique")
    return RuntimeCases(
        path=path,
        timeout_seconds=timeout_seconds,
        inherit_environment=inherit,
        cases=cases,
    )


def execute_runtime_cases(
    *, bundle: Bundle, sources: list[Path]
) -> dict[str, Any]:
    """Execute configured cases and return deterministic, report-ready evidence."""
    configuration = discover_runtime_cases(sources)
    if configuration is None:
        return {
            "format": _RUNTIME_RESULT_FORMAT,
            "configured": False,
            "passed": True,
            "case_count": 0,
            "cases": [],
        }

    executable = bundle.artifact_path("executable")
    if executable is None:
        raise RuntimeCasesError(
            f"runtime cases configured in {configuration.path}, but no executable was captured"
        )

    results = [
        _execute_case(
            executable=executable,
            source_directory=sources[0].resolve().parent,
            configuration=configuration,
            case=case,
        )
        for case in configuration.cases
    ]
    return {
        "format": _RUNTIME_RESULT_FORMAT,
        "configured": True,
        "sidecar": str(configuration.path),
        "sidecar_sha256": _sha256(configuration.path.read_bytes()),
        "executable_sha256": _sha256(executable.read_bytes()),
        "timeout_seconds": configuration.timeout_seconds,
        "inherit_environment": configuration.inherit_environment,
        "passed": all(result["passed"] for result in results),
        "case_count": len(results),
        "cases": results,
    }


def _parse_case(value: object, index: int) -> RuntimeCase:
    if not isinstance(value, dict):
        raise RuntimeCasesError(f"case {index} must be a JSON object")
    name = value.get("name")
    if not isinstance(name, str) or not name.strip():
        raise RuntimeCasesError(f"case {index} requires a non-empty name")

    raw_args = value.get("args", [])
    if not isinstance(raw_args, list) or not all(
        isinstance(argument, str) for argument in raw_args
    ):
        raise RuntimeCasesError(f"case {name!r} args must be a list of strings")

    raw_environment = value.get("env", {})
    if not isinstance(raw_environment, dict):
        raise RuntimeCasesError(f"case {name!r} env must be an object")
    environment: dict[str, str | None] = {}
    for key, item in raw_environment.items():
        if not isinstance(key, str) or not key or "=" in key or "\x00" in key:
            raise RuntimeCasesError(f"case {name!r} contains an invalid environment name")
        if item is not None and not isinstance(item, str):
            raise RuntimeCasesError(
                f"case {name!r} environment values must be strings or null"
            )
        environment[key] = item

    stdin = value.get("stdin", "")
    if not isinstance(stdin, str):
        raise RuntimeCasesError(f"case {name!r} stdin must be a string")

    expectation = value.get("expect")
    if not isinstance(expectation, dict):
        raise RuntimeCasesError(f"case {name!r} requires an expect object")
    exit_code = expectation.get("exit_code")
    if not isinstance(exit_code, int) or isinstance(exit_code, bool):
        raise RuntimeCasesError(f"case {name!r} expect.exit_code must be an integer")
    if not -255 <= exit_code <= 255:
        raise RuntimeCasesError(
            f"case {name!r} expect.exit_code must be between -255 and 255"
        )
    stdout = _optional_string(expectation, "stdout", name)
    stderr = _optional_string(expectation, "stderr", name)

    return RuntimeCase(
        name=name,
        args=tuple(raw_args),
        environment=environment,
        stdin=stdin,
        expected_exit_code=exit_code,
        expected_stdout=stdout,
        expected_stderr=stderr,
    )


def _optional_string(
    mapping: dict[str, object], key: str, case_name: str
) -> str | None:
    value = mapping.get(key)
    if value is not None and not isinstance(value, str):
        raise RuntimeCasesError(f"case {case_name!r} expect.{key} must be a string")
    return value


def _execute_case(
    *,
    executable: Path,
    source_directory: Path,
    configuration: RuntimeCases,
    case: RuntimeCase,
) -> dict[str, Any]:
    environment = os.environ.copy() if configuration.inherit_environment else {}
    for key, value in case.environment.items():
        if value is None:
            environment.pop(key, None)
        else:
            environment[key] = value

    command = [str(executable), *case.args]
    timed_out = False
    try:
        completed = subprocess.run(
            command,
            input=case.stdin.encode(),
            capture_output=True,
            cwd=source_directory,
            env=environment,
            check=False,
            timeout=configuration.timeout_seconds,
        )
        return_code: int | None = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        return_code = None
        stdout = exc.stdout or b""
        stderr = exc.stderr or b""

    stdout_text = stdout.decode("utf-8", errors="replace")
    stderr_text = stderr.decode("utf-8", errors="replace")
    failures: list[str] = []
    if timed_out:
        failures.append(f"timed out after {configuration.timeout_seconds:g} seconds")
    elif return_code != case.expected_exit_code:
        failures.append(
            f"exit code {return_code} did not match {case.expected_exit_code}"
        )
    if case.expected_stdout is not None and stdout_text != case.expected_stdout:
        failures.append("stdout did not match the expected text")
    if case.expected_stderr is not None and stderr_text != case.expected_stderr:
        failures.append("stderr did not match the expected text")

    return {
        "name": case.name,
        "command": [executable.name, *case.args],
        "environment": dict(sorted(case.environment.items())),
        "stdin": case.stdin,
        "expected": {
            "exit_code": case.expected_exit_code,
            "stdout": case.expected_stdout,
            "stderr": case.expected_stderr,
        },
        "actual": {
            "exit_code": return_code,
            "stdout": _capture_text(stdout),
            "stdout_sha256": _sha256(stdout),
            "stderr": _capture_text(stderr),
            "stderr_sha256": _sha256(stderr),
        },
        "timed_out": timed_out,
        "passed": not failures,
        "failures": failures,
    }


def _capture_text(value: bytes) -> str:
    truncated = value[:_MAX_CAPTURE_BYTES]
    text = truncated.decode("utf-8", errors="replace")
    if len(value) > _MAX_CAPTURE_BYTES:
        text += f"\n...[truncated {len(value) - _MAX_CAPTURE_BYTES} bytes]"
    return text


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()
