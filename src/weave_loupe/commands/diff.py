"""``loupe diff`` command."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from weave_loupe.bundle import BundleError, load_bundle
from weave_loupe.diffing import compare_bundles
from weave_loupe.reporting import render_diff_report, write_report


def run_diff(
    *,
    before: Path,
    after: Path,
    json_out: Path | None,
    html_out: Path | None,
) -> int:
    try:
        comparison = compare_bundles(load_bundle(before), load_bundle(after))
        payload = json.dumps(
            comparison, indent=2, sort_keys=True, ensure_ascii=False
        ) + "\n"
        if json_out is not None:
            json_out.parent.mkdir(parents=True, exist_ok=True)
            json_out.write_text(payload, encoding="utf-8")
        else:
            sys.stdout.write(payload)
        if html_out is not None:
            write_report(html_out, render_diff_report(comparison))
    except (BundleError, OSError, ValueError) as exc:
        print(f"loupe diff: {exc}", file=sys.stderr)
        return 1
    if json_out is not None:
        print(f"comparison: {json_out.resolve()}")
    if html_out is not None:
        print(f"report: {html_out.resolve()}")
    return 0
