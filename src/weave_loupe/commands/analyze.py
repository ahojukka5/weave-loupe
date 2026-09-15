"""``loupe analyze`` command."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from weave_loupe.bundle import BundleError, load_bundle
from weave_loupe.bundle.inspection import analyze_evidence, render_analysis_text


def run_analyze(
    *,
    bundle_path: Path,
    json_out: Path | None,
    markdown_out: Path | None,
) -> int:
    try:
        document = analyze_evidence(load_bundle(bundle_path))
        payload = (
            json.dumps(document, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
        )
        markdown = render_analysis_text(document)
        if json_out is not None:
            json_out.parent.mkdir(parents=True, exist_ok=True)
            json_out.write_text(payload, encoding="utf-8")
        else:
            sys.stdout.write(markdown)
        if markdown_out is not None:
            markdown_out.parent.mkdir(parents=True, exist_ok=True)
            markdown_out.write_text(markdown, encoding="utf-8")
    except (BundleError, OSError, ValueError) as exc:
        print(f"loupe analyze: {exc}", file=sys.stderr)
        return 1
    if json_out is not None:
        print(f"analysis: {json_out.resolve()}")
    if markdown_out is not None:
        print(f"report: {markdown_out.resolve()}")
    return 0
