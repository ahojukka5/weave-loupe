"""Deterministic parsing and comparison of LLVM optimization remarks."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

import yaml  # type: ignore[import-untyped]

OPTIMIZATION_REMARKS_FORMAT = "weave-loupe-optimization-remarks-v1"
OPTIMIZATION_REMARKS_DIFF_FORMAT = "weave-loupe-optimization-remarks-diff-v1"

_CATEGORY_ALIASES = {
    "passed": "passed",
    "missed": "missed",
    "analysis": "analysis",
    "failure": "failure",
    "analysisfpcommute": "analysis-fp-commute",
}
_KNOWN_FIELDS = {
    "Args",
    "DebugLoc",
    "Function",
    "Hotness",
    "Name",
    "Pass",
    "RemarkType",
    "Type",
}


def analyze_optimization_remarks(text: str | None) -> dict[str, Any]:
    """Parse LLVM YAML remarks into a stable machine-readable summary."""
    if text is None:
        return {
            "format": OPTIMIZATION_REMARKS_FORMAT,
            "available": False,
            "valid": False,
            "failure_reason": "optimization record is unavailable",
            "documents": 0,
            "records": [],
            "errors": [],
            "summary": _summary([]),
        }

    documents = _split_documents(text)
    records: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for index, (tag, document) in enumerate(documents):
        try:
            loaded = yaml.safe_load(document)
        except yaml.YAMLError as exc:
            errors.append(
                {
                    "document_index": index,
                    "code": "malformed-yaml",
                    "detail": _yaml_error(exc),
                }
            )
            continue
        if not isinstance(loaded, Mapping):
            errors.append(
                {
                    "document_index": index,
                    "code": "unsupported-document",
                    "detail": "optimization remark document must be a YAML mapping",
                }
            )
            continue
        record, error = _normalize_record(index, tag, loaded)
        records.append(record)
        if error is not None:
            errors.append(error)

    records.sort(key=lambda item: (str(item["identity"]), item["document_index"]))
    failure_reason = None
    if errors:
        failure_reason = "; ".join(
            f"document {item['document_index']}: {item['detail']}" for item in errors
        )
    return {
        "format": OPTIMIZATION_REMARKS_FORMAT,
        "available": True,
        "valid": not errors,
        "failure_reason": failure_reason,
        "documents": len(documents),
        "records": records,
        "errors": errors,
        "summary": _summary(records),
    }


def compare_optimization_remarks(
    before: Mapping[str, Any],
    after: Mapping[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Compare normalized optimization remarks and return diff changes."""
    left = _records(before.get("records"))
    right = _records(after.get("records"))
    left_by_id = _records_by_identity(left)
    right_by_id = _records_by_identity(right)
    left_counts: Counter[str] = Counter(item["identity"] for item in left)
    right_counts: Counter[str] = Counter(item["identity"] for item in right)
    added_ids = sorted((right_counts - left_counts).elements())
    removed_ids = sorted((left_counts - right_counts).elements())
    added = _select_records(right_by_id, added_ids)
    removed = _select_records(left_by_id, removed_ids)

    changes: list[dict[str, Any]] = []
    _add_scalar_change(
        changes,
        path="available",
        before=bool(before.get("available", False)),
        after=bool(after.get("available", False)),
    )
    _add_scalar_change(
        changes,
        path="valid",
        before=bool(before.get("valid", False)),
        after=bool(after.get("valid", False)),
    )
    for occurrence, item in enumerate(added):
        changes.append(
            _record_change(
                item,
                kind="added",
                occurrence=occurrence,
                before=None,
                after=item,
            )
        )
    for occurrence, item in enumerate(removed):
        changes.append(
            _record_change(
                item,
                kind="removed",
                occurrence=occurrence,
                before=item,
                after=None,
            )
        )

    counters = {
        name: _counter_diff(
            _summary_counter(before, name),
            _summary_counter(after, name),
        )
        for name in ("by_category", "by_pass", "by_function")
    }
    comparison = {
        "format": OPTIMIZATION_REMARKS_DIFF_FORMAT,
        "changed": bool(changes),
        "available": {
            "before": bool(before.get("available", False)),
            "after": bool(after.get("available", False)),
        },
        "valid": {
            "before": bool(before.get("valid", False)),
            "after": bool(after.get("valid", False)),
        },
        "record_counts": {
            "before": len(left),
            "after": len(right),
            "delta": len(right) - len(left),
        },
        "counters": counters,
        "added": added,
        "removed": removed,
        "errors": {
            "before": _mapping_list(before.get("errors")),
            "after": _mapping_list(after.get("errors")),
        },
    }
    return comparison, sorted(changes, key=_change_key)


def remark_matches(record: Mapping[str, Any], selector: Mapping[str, str]) -> bool:
    """Return whether one normalized remark matches an audit selector."""
    for field in ("category", "pass", "name", "function"):
        expected = selector.get(field)
        if expected is not None and str(record.get(field, "")) != expected:
            return False
    message = selector.get("message_contains")
    return message is None or message in str(record.get("message", ""))


def _split_documents(text: str) -> list[tuple[str | None, str]]:
    documents: list[tuple[str | None, str]] = []
    tag: str | None = None
    lines: list[str] = []
    active = False

    def finish() -> None:
        nonlocal tag, lines, active
        if active:
            documents.append((tag, "\n".join(lines).rstrip() + "\n"))
        tag = None
        lines = []
        active = False

    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    for raw in normalized.split("\n"):
        stripped = raw.strip()
        if stripped == "---" or stripped.startswith("--- "):
            finish()
            active = True
            marker = stripped[3:].strip()
            tag = marker or None
            continue
        if stripped == "...":
            finish()
            continue
        lines.append(raw.rstrip())
        if stripped and not stripped.startswith("#"):
            active = True
    finish()
    return documents


def _normalize_record(
    index: int,
    tag: str | None,
    raw: Mapping[object, object],
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    category = _category(tag, raw)
    location = _location(raw.get("DebugLoc"))
    arguments = _arguments(raw.get("Args"))
    unknown = {
        str(key): _stable(value)
        for key, value in sorted(raw.items(), key=lambda item: str(item[0]))
        if str(key) not in _KNOWN_FIELDS
    }
    normalized: dict[str, Any] = {
        "category": category,
        "pass": _text(raw.get("Pass")),
        "name": _text(raw.get("Name")),
        "function": _text(raw.get("Function")),
        "location": location,
        "hotness": _number(raw.get("Hotness")),
        "arguments": arguments,
        "message": _message(arguments),
        "unknown_fields": unknown,
    }
    canonical = json.dumps(
        normalized,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    record = {
        "document_index": index,
        "identity": hashlib.sha256(canonical).hexdigest(),
        **normalized,
    }
    if category != "unsupported":
        return record, None
    marker = tag or _text(raw.get("RemarkType")) or _text(raw.get("Type")) or "none"
    return record, {
        "document_index": index,
        "code": "unsupported-remark-kind",
        "detail": f"unsupported LLVM optimization remark kind {marker!r}",
    }


def _category(tag: str | None, raw: Mapping[object, object]) -> str:
    candidates = (
        tag,
        _text(raw.get("RemarkType")),
        _text(raw.get("Type")),
        _text(raw.get("Name")),
    )
    for candidate in candidates:
        if not candidate:
            continue
        normalized = candidate.lstrip("!").replace("-", "").replace("_", "")
        category = _CATEGORY_ALIASES.get(normalized.lower())
        if category is not None:
            return category
    return "unsupported"


def _location(value: object) -> dict[str, Any] | None:
    if not isinstance(value, Mapping):
        return None
    result = {
        "file": _text(value.get("File")),
        "line": _integer(value.get("Line")),
        "column": _integer(value.get("Column")),
    }
    return result if any(item is not None for item in result.values()) else None


def _arguments(value: object) -> list[dict[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    result: list[dict[str, Any]] = []
    for item in value:
        if isinstance(item, Mapping):
            result.append(
                {
                    str(key): _stable(raw)
                    for key, raw in sorted(item.items(), key=lambda pair: str(pair[0]))
                }
            )
        else:
            result.append({"value": _stable(item)})
    return result


def _message(arguments: Sequence[Mapping[str, Any]]) -> str:
    fragments: list[str] = []
    for argument in arguments:
        for key, value in argument.items():
            if key == "DebugLoc" or isinstance(value, (Mapping, list)):
                continue
            if value is not None:
                fragments.append(str(value))
    return "".join(fragments).strip()


def _summary(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    categories: Counter[str] = Counter(
        str(item.get("category", "unsupported")) for item in records
    )
    passes: Counter[str] = Counter(
        str(item.get("pass") or "unknown") for item in records
    )
    functions: Counter[str] = Counter(
        str(item.get("function") or "unknown") for item in records
    )
    by_pass_and_category: dict[str, Counter[str]] = {}
    for item in records:
        pass_name = str(item.get("pass") or "unknown")
        category = str(item.get("category") or "unsupported")
        by_pass_and_category.setdefault(pass_name, Counter())[category] += 1
    missed = [item for item in records if item.get("category") == "missed"]
    missed.sort(key=_missed_key)
    return {
        "total": len(records),
        "by_category": dict(sorted(categories.items())),
        "by_pass": dict(sorted(passes.items())),
        "by_function": dict(sorted(functions.items())),
        "by_pass_and_category": {
            name: dict(sorted(counts.items()))
            for name, counts in sorted(by_pass_and_category.items())
        },
        "highest_value_missed": [_public_record(item) for item in missed[:20]],
    }


def _missed_key(item: Mapping[str, Any]) -> tuple[Any, ...]:
    hotness = item.get("hotness")
    numeric = float(hotness) if isinstance(hotness, (int, float)) else -1.0
    return (
        -numeric,
        str(item.get("function") or ""),
        str(item.get("pass") or ""),
        str(item.get("name") or ""),
        str(item.get("identity") or ""),
    )


def _records(value: object) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [dict(item) for item in value if isinstance(item, Mapping)]


def _records_by_identity(
    records: Sequence[Mapping[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for item in records:
        identity = str(item.get("identity", ""))
        result.setdefault(identity, []).append(dict(item))
    return result


def _select_records(
    records: Mapping[str, list[dict[str, Any]]],
    identities: Sequence[str],
) -> list[dict[str, Any]]:
    offsets: Counter[str] = Counter()
    result: list[dict[str, Any]] = []
    for identity in identities:
        index = offsets[identity]
        result.append(records[identity][index])
        offsets[identity] += 1
    return result


def _record_change(
    item: Mapping[str, Any],
    *,
    kind: str,
    occurrence: int,
    before: object,
    after: object,
) -> dict[str, Any]:
    category = str(item.get("category", "unsupported"))
    if kind == "added":
        severity = "warning" if category in {"missed", "failure"} else "info"
    else:
        severity = "warning" if category == "passed" else "info"
    if category == "unsupported":
        severity = "error"
    identity = str(item.get("identity", ""))
    return {
        "id": f"optimization_remarks:{identity}:{kind}:{occurrence}",
        "section": "optimization_remarks",
        "path": identity,
        "kind": kind,
        "classification": "quality",
        "severity": severity,
        "before": before,
        "after": after,
    }


def _add_scalar_change(
    changes: list[dict[str, Any]],
    *,
    path: str,
    before: bool,
    after: bool,
) -> None:
    if before == after:
        return
    changes.append(
        {
            "id": f"optimization_remarks:{path}:changed",
            "section": "optimization_remarks",
            "path": path,
            "kind": "changed",
            "classification": "evidence",
            "severity": "error" if not after else "info",
            "before": before,
            "after": after,
        }
    )


def _counter_diff(
    before: Mapping[str, int],
    after: Mapping[str, int],
) -> dict[str, dict[str, Any]]:
    return {
        name: {
            "before": before.get(name, 0),
            "after": after.get(name, 0),
            "delta": after.get(name, 0) - before.get(name, 0),
            "changed": before.get(name, 0) != after.get(name, 0),
        }
        for name in sorted(set(before) | set(after))
    }


def _summary_counter(document: Mapping[str, Any], name: str) -> dict[str, int]:
    summary = document.get("summary")
    if not isinstance(summary, Mapping):
        return {}
    value = summary.get(name)
    if not isinstance(value, Mapping):
        return {}
    return {
        str(key): count
        for key, count in value.items()
        if isinstance(count, int) and not isinstance(count, bool)
    }


def _public_record(item: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: _stable(item.get(key))
        for key in (
            "identity",
            "category",
            "pass",
            "name",
            "function",
            "location",
            "hotness",
            "message",
        )
    }


def _mapping_list(value: object) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [dict(item) for item in value if isinstance(item, Mapping)]


def _change_key(item: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(
        str(item.get(name, ""))
        for name in ("section", "path", "kind", "classification", "severity", "id")
    )


def _yaml_error(error: Any) -> str:
    problem = getattr(error, "problem", None)
    mark = getattr(error, "problem_mark", None)
    if isinstance(problem, str) and mark is not None:
        line = getattr(mark, "line", None)
        column = getattr(mark, "column", None)
        if isinstance(line, int) and isinstance(column, int):
            return f"{problem} at line {line + 1}, column {column + 1}"
    return str(error).splitlines()[0]


def _stable(value: object) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): _stable(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return [_stable(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _text(value: object) -> str | None:
    return value if isinstance(value, str) and value else None


def _integer(value: object) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _number(value: object) -> int | float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value
    return None
