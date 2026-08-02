"""Deterministic comparison of normalized WIR analyses."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any, Literal

Classification = Literal["semantic", "quality", "provenance", "evidence"]
Severity = Literal["info", "warning", "error"]

_WARNING_METRICS = frozenset(
    {
        "anonymous_identifiers",
        "duplicate_declarations",
        "malformed_provenance",
        "unreachable_blocks",
        "unresolved_symbols",
    }
)
_CROSS_STAGE_SETS = (
    "duplicate_llvm_declarations",
    "duplicate_llvm_definitions",
    "missing_definitions",
    "missing_externs",
    "unexpected_definitions",
)


def compare_wir_analysis(
    before: Mapping[str, Any],
    after: Mapping[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Return one normalized WIR section and stable classified changes."""
    section: dict[str, Any] = {
        name: _scalar(before.get(name), after.get(name))
        for name in ("available", "valid", "failure_reason", "core_version")
    }
    section.update(
        {
            "metrics": _numeric(
                _mapping(before.get("metrics")),
                _mapping(after.get("metrics")),
            ),
            "opcodes": _numeric(
                _mapping(before.get("opcodes")),
                _mapping(after.get("opcodes")),
            ),
            "types": _numeric(
                _mapping(before.get("types")),
                _mapping(after.get("types")),
            ),
            "declarations": _records(
                _record_map(before.get("declarations"), "declaration"),
                _record_map(after.get("declarations"), "declaration"),
            ),
            "functions": _functions(
                _mapping(before.get("functions")),
                _mapping(after.get("functions")),
            ),
            "call_graph": _set_mapping(
                _mapping(before.get("call_graph")),
                _mapping(after.get("call_graph")),
            ),
            "duplicate_declarations": _set_delta(
                before.get("duplicate_declarations"),
                after.get("duplicate_declarations"),
            ),
            "anonymous_identifiers": _set_delta(
                before.get("anonymous_identifiers"),
                after.get("anonymous_identifiers"),
            ),
            "unresolved_symbols": _set_delta(
                before.get("unresolved_symbols"),
                after.get("unresolved_symbols"),
            ),
            "provenance": _recursive(
                before.get("provenance"),
                after.get("provenance"),
            ),
            "cross_stage": _cross_stage(
                _mapping(before.get("cross_stage")),
                _mapping(after.get("cross_stage")),
            ),
        }
    )
    changes = _changes(section)
    section["changed"] = bool(changes)
    section["change_count"] = len(changes)
    return section, changes


def _changes(section: Mapping[str, Any]) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    for name in ("available", "valid", "failure_reason", "core_version"):
        value = _mapping(section.get(name))
        if value.get("changed") is True:
            _add(
                changes,
                name,
                "changed",
                "evidence",
                "error",
                value.get("before"),
                value.get("after"),
            )
    for prefix in ("metrics", "opcodes", "types"):
        _numeric_changes(_mapping(section.get(prefix)), prefix, changes)
    _record_changes(
        _mapping(section.get("declarations")),
        "declarations",
        changes,
    )
    _function_changes(_mapping(section.get("functions")), changes)
    for name, value in sorted(_mapping(section.get("call_graph")).items()):
        _set_changes(
            _mapping(value),
            f"call_graph.{name}",
            "semantic",
            "error",
            changes,
        )
    for name in (
        "duplicate_declarations",
        "anonymous_identifiers",
        "unresolved_symbols",
    ):
        _set_changes(
            _mapping(section.get(name)),
            name,
            "quality",
            "warning",
            changes,
        )
    _recursive_changes(
        _mapping(section.get("provenance")),
        "provenance",
        "provenance",
        "warning",
        changes,
    )
    _cross_stage_changes(_mapping(section.get("cross_stage")), changes)
    return sorted(changes, key=_change_key)


def _numeric_changes(
    values: Mapping[str, Any],
    prefix: str,
    changes: list[dict[str, Any]],
) -> None:
    for name, raw in sorted(values.items()):
        value = _mapping(raw)
        if value.get("changed") is not True:
            continue
        classification: Classification = "quality"
        warning = prefix == "metrics" and name in _WARNING_METRICS
        severity: Severity = "warning" if warning else "info"
        if prefix == "metrics" and name == "malformed_provenance":
            classification = "evidence"
            severity = "error"
        delta = value.get("delta")
        _add(
            changes,
            f"{prefix}.{name}",
            "delta",
            classification,
            severity,
            value.get("before"),
            value.get("after"),
            delta=_number(delta),
        )


def _record_changes(
    values: Mapping[str, Any],
    prefix: str,
    changes: list[dict[str, Any]],
) -> None:
    for kind in ("added", "removed"):
        for name in _strings(values.get(kind)):
            _add(
                changes,
                f"{prefix}.{name}",
                kind,
                "semantic",
                "error",
                name if kind == "removed" else None,
                name if kind == "added" else None,
            )
    items = _mapping(values.get("items"))
    for name in _strings(values.get("modified")):
        item = _mapping(items.get(name))
        _add(
            changes,
            f"{prefix}.{name}",
            "modified",
            "semantic",
            "error",
            item.get("before"),
            item.get("after"),
        )


def _function_changes(
    values: Mapping[str, Any],
    changes: list[dict[str, Any]],
) -> None:
    _record_changes(values, "functions", changes)
    items = _mapping(values.get("items"))
    for name in _strings(values.get("modified")):
        function = _mapping(items.get(name))
        differences = function.get("differences")
        if not isinstance(differences, list):
            continue
        for raw in differences:
            difference = _mapping(raw)
            path = str(difference.get("path", "value"))
            classification: Classification = (
                "provenance" if path.startswith("provenance") else "quality"
            )
            severity: Severity = (
                "warning" if _suspicious_function_path(path) else "info"
            )
            _add(
                changes,
                f"functions.{name}.{path}",
                str(difference.get("kind", "changed")),
                classification,
                severity,
                difference.get("before"),
                difference.get("after"),
            )


def _cross_stage_changes(
    values: Mapping[str, Any],
    changes: list[dict[str, Any]],
) -> None:
    for name in _CROSS_STAGE_SETS:
        _set_changes(
            _mapping(values.get(name)),
            f"cross_stage.{name}",
            "semantic",
            "error",
            changes,
        )
    _numeric_changes(
        _mapping(values.get("metrics")),
        "cross_stage.metrics",
        changes,
    )
    _recursive_changes(
        _mapping(values.get("functions")),
        "cross_stage.functions",
        "quality",
        "info",
        changes,
    )


def _set_changes(
    values: Mapping[str, Any],
    path: str,
    classification: Classification,
    severity: Severity,
    changes: list[dict[str, Any]],
) -> None:
    for kind in ("added", "removed"):
        for name in _strings(values.get(kind)):
            _add(
                changes,
                f"{path}.{name}",
                kind,
                classification,
                severity,
                name if kind == "removed" else None,
                name if kind == "added" else None,
            )


def _recursive_changes(
    values: Mapping[str, Any],
    prefix: str,
    classification: Classification,
    severity: Severity,
    changes: list[dict[str, Any]],
) -> None:
    differences = values.get("differences")
    if not isinstance(differences, list):
        return
    for raw in differences:
        difference = _mapping(raw)
        _add(
            changes,
            f"{prefix}.{difference.get('path', 'value')}",
            str(difference.get("kind", "changed")),
            classification,
            severity,
            difference.get("before"),
            difference.get("after"),
        )


def _add(
    changes: list[dict[str, Any]],
    path: str,
    kind: str,
    classification: Classification,
    severity: Severity,
    before: Any,
    after: Any,
    *,
    delta: int | float | None = None,
) -> None:
    if before == after:
        return
    item: dict[str, Any] = {
        "id": f"analysis.wir:{path}:{kind}",
        "section": "analysis.wir",
        "path": path,
        "kind": kind,
        "classification": classification,
        "severity": severity,
        "before": before,
        "after": after,
    }
    if delta is not None:
        item["delta"] = delta
    changes.append(item)


def _scalar(before: Any, after: Any) -> dict[str, Any]:
    left, right = _stable(before), _stable(after)
    return {"before": left, "after": right, "changed": left != right}


def _numeric(
    before: Mapping[str, Any],
    after: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for name in sorted(set(before) | set(after)):
        left, right = _number(before.get(name)), _number(after.get(name))
        result[name] = {
            "before": left,
            "after": right,
            "delta": (right - left if left is not None and right is not None else None),
            "changed": left != right,
        }
    return result


def _records(
    before: Mapping[str, Any],
    after: Mapping[str, Any],
) -> dict[str, Any]:
    left_names, right_names = set(before), set(after)
    modified = sorted(
        name
        for name in left_names & right_names
        if _stable(before[name]) != _stable(after[name])
    )
    return {
        "added": sorted(right_names - left_names),
        "removed": sorted(left_names - right_names),
        "modified": modified,
        "items": {
            name: {
                "before": _stable(before[name]),
                "after": _stable(after[name]),
            }
            for name in modified
        },
    }


def _functions(
    before: Mapping[str, Any],
    after: Mapping[str, Any],
) -> dict[str, Any]:
    result = _records(before, after)
    items = dict(_mapping(result.get("items")))
    for name in _strings(result.get("modified")):
        left, right = _stable(before[name]), _stable(after[name])
        items[name] = {
            "before": left,
            "after": right,
            "differences": _deep_differences(left, right),
        }
    result["items"] = items
    return result


def _set_mapping(
    before: Mapping[str, Any],
    after: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        name: _set_delta(before.get(name), after.get(name))
        for name in sorted(set(before) | set(after))
    }


def _set_delta(before: Any, after: Any) -> dict[str, Any]:
    left, right = set(_strings(before)), set(_strings(after))
    return {
        "added": sorted(right - left),
        "removed": sorted(left - right),
        "unchanged": sorted(left & right),
        "changed": left != right,
    }


def _recursive(before: Any, after: Any) -> dict[str, Any]:
    left, right = _stable(before), _stable(after)
    differences = _deep_differences(left, right)
    return {
        "before_sha256": _digest(left),
        "after_sha256": _digest(right),
        "changed": bool(differences),
        "differences": differences,
    }


def _cross_stage(
    before: Mapping[str, Any],
    after: Mapping[str, Any],
) -> dict[str, Any]:
    set_names = (
        "wir_functions",
        "wir_externs",
        "llvm_definitions",
        "llvm_declarations",
        *_CROSS_STAGE_SETS,
    )
    return {
        **{name: _set_delta(before.get(name), after.get(name)) for name in set_names},
        "metrics": _numeric(
            _mapping(before.get("metrics")),
            _mapping(after.get("metrics")),
        ),
        "functions": _recursive(
            before.get("functions"),
            after.get("functions"),
        ),
    }


def _record_map(value: Any, prefix: str) -> dict[str, Any]:
    if not isinstance(value, list):
        return {}
    records: dict[str, Any] = {}
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            continue
        name = item.get("name")
        key = str(name) if isinstance(name, str) else f"<{prefix}-{index}>"
        if key in records:
            key = f"{key}#{index}"
        records[key] = _stable(item)
    return records


def _deep_differences(
    before: Any,
    after: Any,
    path: str = "",
) -> list[dict[str, Any]]:
    if before == after:
        return []
    differences: list[dict[str, Any]] = []
    if isinstance(before, Mapping) and isinstance(after, Mapping):
        for key in sorted(set(before) | set(after), key=str):
            child = f"{path}.{key}" if path else str(key)
            if key not in before:
                differences.append(
                    {
                        "path": child,
                        "kind": "added",
                        "before": None,
                        "after": after[key],
                    }
                )
            elif key not in after:
                differences.append(
                    {
                        "path": child,
                        "kind": "removed",
                        "before": before[key],
                        "after": None,
                    }
                )
            else:
                differences.extend(_deep_differences(before[key], after[key], child))
        return differences
    if isinstance(before, list) and isinstance(after, list):
        length = max(len(before), len(after))
        for index in range(length):
            child = f"{path}[{index}]" if path else f"[{index}]"
            if index >= len(before):
                differences.append(
                    {
                        "path": child,
                        "kind": "added",
                        "before": None,
                        "after": after[index],
                    }
                )
            elif index >= len(after):
                differences.append(
                    {
                        "path": child,
                        "kind": "removed",
                        "before": before[index],
                        "after": None,
                    }
                )
            else:
                differences.extend(
                    _deep_differences(before[index], after[index], child)
                )
        return differences
    return [
        {
            "path": path or "value",
            "kind": "changed",
            "before": before,
            "after": after,
        }
    ]


def _stable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): _stable(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, (list, tuple)):
        return [_stable(item) for item in value]
    return value


def _digest(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _suspicious_function_path(path: str) -> bool:
    return any(
        token in path
        for token in (
            "anonymous_identifiers",
            "duplicate_locals",
            "unreachable",
            "unresolved_symbols",
        )
    )


def _change_key(item: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(
        str(item[name])
        for name in (
            "section",
            "path",
            "kind",
            "classification",
            "severity",
        )
    )


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _number(value: Any) -> int | float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return value
