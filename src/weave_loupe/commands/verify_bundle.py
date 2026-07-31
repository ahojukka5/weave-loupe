"""``loupe verify-bundle`` command."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from weave_loupe.bundle import verify_bundle


def run_verify_bundle(
    *,
    bundle: Path,
    json_out: Path | None,
    allow_undeclared: bool,
) -> int:
    """Verify a bundle and publish deterministic machine-readable evidence."""
    verification = verify_bundle(bundle, closed=not allow_undeclared)
    payload = (
        json.dumps(
            verification.as_dict(),
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
        + "\n"
    )
    try:
        if json_out is None:
            sys.stdout.write(payload)
        else:
            json_out.parent.mkdir(parents=True, exist_ok=True)
            json_out.write_text(payload, encoding="utf-8")
            print(f"verification: {json_out.resolve()}")
    except OSError as exc:
        print(f"loupe verify-bundle: {exc}", file=sys.stderr)
        return 1

    if verification.valid:
        return 0
    print(
        f"loupe verify-bundle: {len(verification.problems)} integrity problem(s)",
        file=sys.stderr,
    )
    return 2
