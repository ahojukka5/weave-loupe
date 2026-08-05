"""``loupe ingest`` command."""

from __future__ import annotations

import sys
from pathlib import Path

from weave_loupe.bundle import BundleError, ingest_bundle


def run_ingest(*, request: Path, output: Path) -> int:
    """Publish one retained compiler invocation as a verified Loupe bundle."""
    try:
        result = ingest_bundle(request=request, output=output)
    except BundleError as exc:
        print(f"loupe ingest: {exc}", file=sys.stderr)
        return 1
    print(f"bundle: {result.bundle}")
    print(f"retained compiler exit: {result.compiler_exit_code}")
    return 0
