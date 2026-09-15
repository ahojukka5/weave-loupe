"""``loupe inspect`` command."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from weave_loupe.bundle import BundleError, load_bundle
from weave_loupe.bundle.inspection import inspect_bundle, render_inspection_text
from weave_loupe.bundle.views import VIEW_NAMES, evidence_view


def run_inspect(
    *,
    bundle_path: Path,
    json_out: Path | None,
    stage: str | None,
    view: str | None,
) -> int:
    try:
        bundle = load_bundle(bundle_path)
        if view is not None:
            payload = evidence_view(bundle, view)
        else:
            payload = inspect_bundle(bundle)
            if stage is not None:
                lineage = payload.get("lineage")
                stages_raw = lineage.get("stages") if isinstance(lineage, dict) else []
                if not isinstance(stages_raw, list):
                    stages_raw = []
                match = next(
                    (
                        item
                        for item in stages_raw
                        if isinstance(item, dict) and item.get("id") == stage
                    ),
                    None,
                )
                if match is None:
                    raise BundleError(f"unknown stage {stage!r}")
                payload = {
                    "format": "weave-loupe-stage-v1",
                    "stage": match,
                }
        text = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
        if json_out is not None:
            json_out.parent.mkdir(parents=True, exist_ok=True)
            json_out.write_text(text, encoding="utf-8")
            print(f"inspection: {json_out.resolve()}")
        elif view is not None or stage is not None:
            sys.stdout.write(text)
        else:
            sys.stdout.write(render_inspection_text(payload))
    except (BundleError, OSError, ValueError) as exc:
        print(f"loupe inspect: {exc}", file=sys.stderr)
        return 1
    return 0


def inspect_view_names() -> tuple[str, ...]:
    return VIEW_NAMES
