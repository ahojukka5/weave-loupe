"""Discover and cache capability registries from exact compiler binaries."""

from __future__ import annotations

import copy
import hashlib
import json
import os
import stat
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from weave_loupe.bounded_process import (
    ProcessExecutionError,
    ProcessLimitError,
    ProcessLimits,
    run_bounded_process,
)
from weave_loupe.process_budget import with_user_process_baseline

from .capabilities import (
    CAPABILITIES_FORMAT,
    CAPABILITY_IDENTITY_FORMAT,
    CompilerCapabilityError,
    require_capture_capabilities,
    validate_capability_document,
)

CAPABILITIES_TIMEOUT_SECONDS = 5.0
MAX_CAPABILITIES_BYTES = 1024 * 1024


@dataclass(frozen=True)
class CompilerCapabilityRegistry:
    """Validated capability bytes and path-free compatibility identity."""

    document: Mapping[str, Any]
    raw_bytes: bytes
    identity: Mapping[str, Any]

    def document_copy(self) -> dict[str, Any]:
        return copy.deepcopy(dict(self.document))

    def identity_copy(self) -> dict[str, Any]:
        return copy.deepcopy(dict(self.identity))


_CACHE: dict[str, CompilerCapabilityRegistry] = {}


def clear_capability_cache() -> None:
    """Clear process-local immutable-registry cache for tests and embedders."""

    _CACHE.clear()


def load_compiler_capabilities(
    binary: Path,
    *,
    environment: Mapping[str, str] | None = None,
    timeout_seconds: float = CAPABILITIES_TIMEOUT_SECONDS,
    output_bytes: int = MAX_CAPABILITIES_BYTES,
) -> CompilerCapabilityRegistry:
    """Load one exact final-compiler registry through a bounded subprocess."""

    if timeout_seconds <= 0:
        raise ValueError("capability timeout must be positive")
    if isinstance(output_bytes, bool) or output_bytes <= 0:
        raise ValueError("capability output limit must be a positive integer")

    resolved = binary.expanduser().resolve()
    before = _binary_identity(resolved)
    cached = _CACHE.get(before["sha256"])
    if cached is not None:
        return cached

    limits = with_user_process_baseline(
        ProcessLimits(
            timeout_seconds=timeout_seconds,
            output_bytes=output_bytes,
            excerpt_bytes=output_bytes,
            cpu_seconds=max(1, int(timeout_seconds) + 1),
            address_space_bytes=512 * 1024 * 1024,
            file_size_bytes=output_bytes,
            process_count=8,
        )
    )
    try:
        execution = run_bounded_process(
            (str(resolved), "capabilities", "--json"),
            limits=limits,
            environment=environment,
        )
    except (OSError, ProcessExecutionError, ProcessLimitError) as exc:
        raise CompilerCapabilityError(
            "WEAVEC_CAPABILITIES_UNAVAILABLE",
            "weavec capabilities --json could not start",
        ) from exc

    if execution.termination_reason == "timed_out":
        raise CompilerCapabilityError(
            "WEAVEC_CAPABILITIES_TIMEOUT",
            f"weavec capabilities --json exceeded {timeout_seconds:g} seconds",
        )
    if execution.termination_reason == "output_limit":
        raise CompilerCapabilityError(
            "WEAVEC_CAPABILITIES_OUTPUT_LIMIT",
            "weavec capabilities --json exceeded the bounded output size",
        )
    if execution.exit_code != 0:
        raise CompilerCapabilityError(
            "WEAVEC_CAPABILITIES_FAILED",
            f"weavec capabilities --json exited {execution.exit_code}",
        )
    if (
        execution.stdout.truncated_bytes > 0
        or execution.stdout.observed_bytes > output_bytes
    ):
        raise CompilerCapabilityError(
            "WEAVEC_CAPABILITIES_OUTPUT_LIMIT",
            "weavec capabilities --json did not fit the bounded output size",
        )
    text = execution.stdout.text
    if "\ufffd" in text:
        raise CompilerCapabilityError(
            "WEAVEC_CAPABILITIES_INVALID_UTF8",
            "weavec capabilities --json did not return valid UTF-8",
        )
    raw_bytes = text.encode("utf-8")
    if len(raw_bytes) != execution.stdout.observed_bytes:
        raise CompilerCapabilityError(
            "WEAVEC_CAPABILITIES_INVALID_UTF8",
            "weavec capabilities --json byte count disagrees with UTF-8 text",
        )
    try:
        raw_document = json.loads(text)
    except json.JSONDecodeError as exc:
        raise CompilerCapabilityError(
            "WEAVEC_CAPABILITIES_INVALID_JSON",
            "weavec capabilities --json returned malformed JSON",
        ) from exc

    document = validate_capability_document(raw_document)
    profile = require_capture_capabilities(document)
    after = _binary_identity(resolved)
    if after != before:
        raise CompilerCapabilityError(
            "WEAVEC_CHANGED_DURING_CAPABILITIES",
            "the configured weavec changed during capability negotiation",
        )
    registry_sha256 = hashlib.sha256(raw_bytes).hexdigest()
    if registry_sha256 != execution.stdout.sha256:
        raise CompilerCapabilityError(
            "WEAVEC_CAPABILITIES_IDENTITY_MISMATCH",
            "capability output identity disagrees with captured bytes",
        )
    identity = {
        "format": CAPABILITY_IDENTITY_FORMAT,
        "registry_format": CAPABILITIES_FORMAT,
        "registry_sha256": registry_sha256,
        "registry_bytes": len(raw_bytes),
        "compiler_sha256": before["sha256"],
        "compiler_bytes": before["bytes"],
        "compiler_version": document["compiler"]["version"],
        "surface_version": document["language"]["surface_version"],
        "grammar_id": document["language"]["grammar_id"],
        "wir_core_version": document["language"]["wir_core_version"],
        "protocols": {item["id"]: item["version"] for item in document["protocols"]},
        "target": profile["target"],
        "capture_profile": profile,
    }
    result = CompilerCapabilityRegistry(
        document=document,
        raw_bytes=raw_bytes,
        identity=identity,
    )
    _CACHE[before["sha256"]] = result
    return result


def _binary_identity(path: Path) -> dict[str, Any]:
    flags = os.O_RDONLY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise CompilerCapabilityError(
            "WEAVEC_NOT_EXECUTABLE",
            "the configured weavec cannot be opened safely",
        ) from exc
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or not os.access(path, os.X_OK):
            raise CompilerCapabilityError(
                "WEAVEC_NOT_EXECUTABLE",
                "the configured weavec is not an executable regular file",
            )
        digest = hashlib.sha256()
        with os.fdopen(descriptor, "rb", closefd=False) as stream:
            while chunk := stream.read(1024 * 1024):
                digest.update(chunk)
        after = os.fstat(descriptor)
        if _stat_identity(before) != _stat_identity(after):
            raise CompilerCapabilityError(
                "WEAVEC_CHANGED_DURING_IDENTITY",
                "the configured weavec changed while being identified",
            )
        return {"sha256": digest.hexdigest(), "bytes": before.st_size}
    finally:
        os.close(descriptor)


def _stat_identity(value: os.stat_result) -> tuple[int, int, int, int, int]:
    return (
        value.st_dev,
        value.st_ino,
        value.st_size,
        value.st_mtime_ns,
        value.st_ctime_ns,
    )
