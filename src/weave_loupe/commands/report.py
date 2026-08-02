"""``loupe report`` command."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from weave_loupe.analysis import analyze_bundle
from weave_loupe.bundle import BundleError, load_bundle
from weave_loupe.complete_reporting import render_bundle_report
from weave_loupe.reporting import write_report


def run_report(*, bundle_path: Path, output: Path, analysis_json: Path | None) -> int:
    try:
        bundle = load_bundle(bundle_path)
        analysis = analyze_bundle(bundle)
        write_report(output, render_bundle_report(bundle))
        if analysis_json is not None:
            analysis_json.parent.mkdir(parents=True, exist_ok=True)
            analysis_json.write_text(
                json.dumps(analysis, indent=2, sort_keys=True, ensure_ascii=False)
                + "\n",
                encoding="utf-8",
            )
    except (BundleError, OSError, ValueError) as exc:
        print(f"loupe report: {exc}", file=sys.stderr)
        return 1
    print(f"report: {output.resolve()}")
    if analysis_json is not None:
        print(f"analysis: {analysis_json.resolve()}")
    return 0
