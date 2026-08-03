"""``loupe capture`` command."""

from __future__ import annotations

import sys
from pathlib import Path

from weave_loupe.bundle import BundleError, capture_bundle


def run_capture(
    *,
    weave_files: list[Path],
    output: Path,
    weavec: Path | None,
    include_executable: bool,
    compiler_timeout_seconds: float | None = None,
    compiler_output_bytes: int | None = None,
    audit_root: Path | None = None,
    source_names: list[str] | None = None,
) -> int:
    try:
        result = capture_bundle(
            sources=weave_files,
            output=output,
            weavec=weavec,
            include_executable=include_executable,
            compiler_timeout_seconds=compiler_timeout_seconds,
            compiler_output_bytes=compiler_output_bytes,
            audit_root=audit_root,
            source_names=source_names,
        )
    except BundleError as exc:
        print(f"loupe capture: {exc}", file=sys.stderr)
        return 1
    print(f"bundle: {result.bundle}")
    print(f"compiler exit: {result.compiler_exit_code}")
    return result.compiler_exit_code
