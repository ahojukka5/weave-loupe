"""Stage-aware localization for good/bad bundle comparison."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from weave_loupe.bundle.identity import identity_from_manifest
from weave_loupe.bundle.lineage import (
    STAGE_IDS,
    completeness_for_bundle,
    lineage_for_bundle,
    source_identities,
)
from weave_loupe.bundle.model import Bundle

LOCALIZATION_FORMAT = "weave-loupe-localization-v1"
_CAVEAT = (
    "The first changed stage is localization evidence, not a proven defect origin."
)


def localize_bundle_comparison(before: Bundle, after: Bundle) -> dict[str, Any]:
    """Identify the earliest stage whose retained artifacts materially diverge."""
    left = lineage_for_bundle(before)
    right = lineage_for_bundle(after)
    left_complete = completeness_for_bundle(before)
    right_complete = completeness_for_bundle(after)
    source_changed = source_identities(before.manifest) != source_identities(
        after.manifest
    )
    compiler_changed = identity_from_manifest(before.manifest) != (
        identity_from_manifest(after.manifest)
    )
    missing = _missing(left_complete, "before") + _missing(right_complete, "after")
    unchanged: list[str] = []
    first_changed: str | None = None
    stage_notes: list[dict[str, Any]] = []
    for stage_id in STAGE_IDS:
        left_stage = _stage(left, stage_id)
        right_stage = _stage(right, stage_id)
        note = {
            "id": stage_id,
            "before": left_stage.get("status"),
            "after": right_stage.get("status"),
            "changed": _stage_changed(left_stage, right_stage),
        }
        stage_notes.append(note)
        if not note["changed"]:
            unchanged.append(stage_id)
            continue
        if first_changed is None:
            first_changed = stage_id
    diagnostics_changed = _artifact_changed(before, after, "diagnostics")
    left_runtime = _stage(left, "runtime").get("status")
    right_runtime = _stage(right, "runtime").get("status")
    runtime_changed = left_runtime != right_runtime or _artifact_changed(
        before, after, "executable"
    )
    matched_inputs = not source_changed
    return {
        "format": LOCALIZATION_FORMAT,
        "matched_inputs": matched_inputs,
        "compiler_identity_changed": compiler_changed,
        "first_changed_stage": first_changed,
        "unchanged_stages": unchanged,
        "missing_evidence": missing,
        "diagnostics_changed": diagnostics_changed,
        "runtime_changed": runtime_changed,
        "incomplete": not left_complete["complete"] or not right_complete["complete"],
        "before_complete": left_complete["complete"],
        "after_complete": right_complete["complete"],
        "inferred_lineage": (
            left.get("inferred") is True or right.get("inferred") is True
        ),
        "stages": stage_notes,
        "caveat": _CAVEAT,
    }


def _stage(lineage: Mapping[str, Any], stage_id: str) -> Mapping[str, Any]:
    for item in lineage.get("stages", []):
        if isinstance(item, Mapping) and item.get("id") == stage_id:
            return item
    return {"id": stage_id, "status": "unavailable", "artifact_sha256": {}}


def _stage_changed(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    if left.get("status") != right.get("status"):
        return True
    return left.get("artifact_sha256") != right.get("artifact_sha256") or left.get(
        "source_sha256"
    ) != right.get("source_sha256")


def _artifact_changed(before: Bundle, after: Bundle, name: str) -> bool:
    left = before.manifest.get("artifacts")
    right = after.manifest.get("artifacts")
    left_item = left.get(name) if isinstance(left, Mapping) else None
    right_item = right.get(name) if isinstance(right, Mapping) else None
    return left_item != right_item


def _missing(completeness: Mapping[str, Any], side: str) -> list[dict[str, str]]:
    gaps = completeness.get("gaps")
    if not isinstance(gaps, list):
        return []
    result: list[dict[str, str]] = []
    for item in gaps:
        if not isinstance(item, Mapping):
            continue
        result.append(
            {
                "side": side,
                "stage": str(item.get("stage")),
                "status": str(item.get("status")),
                "reason": str(item.get("reason")),
            }
        )
    return result
