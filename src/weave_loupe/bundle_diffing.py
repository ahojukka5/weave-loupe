"""Public bundle comparison including normalized WIR evidence."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from typing import Any

from weave_loupe.analysis import analyze_bundle
from weave_loupe.bundle import Bundle
from weave_loupe.diffing import DIFF_FORMAT, LEGACY_DIFF_FORMAT
from weave_loupe.diffing import compare_bundles as _compare_without_wir
from weave_loupe.wir_diffing import compare_wir_analysis


def compare_bundles(
    before: Bundle,
    after: Bundle,
    *,
    format_version: str = "v2",
    before_context: Mapping[str, Any] | None = None,
    after_context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Compare complete stable bundle evidence, including WIR structure."""
    result = _compare_without_wir(
        before,
        after,
        format_version=format_version,
        before_context=before_context,
        after_context=after_context,
    )
    if result.get("format") == LEGACY_DIFF_FORMAT:
        return result
    if result.get("format") != DIFF_FORMAT:
        return result

    left = analyze_bundle(before)
    right = analyze_bundle(after)
    wir, wir_changes = compare_wir_analysis(
        _mapping(left.get("wir")),
        _mapping(right.get("wir")),
    )
    changes = sorted(
        [*_change_list(result.get("changes")), *wir_changes],
        key=_change_key,
    )
    analysis = dict(_mapping(result.get("analysis")))
    result["analysis"] = {"wir": wir, **analysis}
    result["changes"] = changes
    result["summary"] = _summary(changes)
    return result


def compare_bundles_v1(before: Bundle, after: Bundle) -> dict[str, Any]:
    """Return the original compact v1 comparison shape."""
    return compare_bundles(before, after, format_version="v1")


def _summary(changes: list[dict[str, Any]]) -> dict[str, Any]:
    classifications = Counter(str(item.get("classification")) for item in changes)
    severities = Counter(str(item.get("severity")) for item in changes)
    sections = sorted({str(item.get("section")) for item in changes})
    return {
        "changed": bool(changes),
        "total_changes": len(changes),
        "by_classification": dict(sorted(classifications.items())),
        "by_severity": dict(sorted(severities.items())),
        "changed_sections": sections,
        "has_errors": severities.get("error", 0) > 0,
        "has_warnings": severities.get("warning", 0) > 0,
    }


def _change_key(item: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(
        str(item.get(name, ""))
        for name in (
            "section",
            "path",
            "kind",
            "classification",
            "severity",
        )
    )


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _change_list(value: object) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [dict(item) for item in value if isinstance(item, Mapping)]
