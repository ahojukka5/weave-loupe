"""Complete deterministic comparison of compiler-evidence bundles."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Literal, cast

from weave_loupe.analysis import analyze_bundle
from weave_loupe.bundle import Bundle

DIFF_FORMAT = "weave-loupe-diff-v2"
LEGACY_DIFF_FORMAT = "weave-loupe-diff-v1"
_FORMATS = {"v1", "v2", DIFF_FORMAT, LEGACY_DIFF_FORMAT}
Classification = Literal["semantic", "quality", "provenance", "evidence"]
Severity = Literal["info", "warning", "error"]

_VOLATILE_KEYS = frozenset(
    {
        "created_at",
        "cwd",
        "duration",
        "duration_seconds",
        "elapsed",
        "elapsed_seconds",
        "finished_at",
        "pid",
        "started_at",
        "timestamp",
        "timestamp_utc",
        "workspace",
    }
)
_RUNTIME_VOLATILE_KEYS = _VOLATILE_KEYS | frozenset(
    {
        "executable_sha256",
        "limits",
        "sandbox",
        "sidecar",
        "timeout_seconds",
    }
)
_NATIVE_SCALARS = (
    "available",
    "supported",
    "architecture",
    "object_format",
    "disassembler",
    "disassembler_version",
    "parser_format",
    "failure_reason",
    "entry_point",
    "reachability_complete",
    "unreachable_program_instructions",
    "reachable_indirect_calls",
)
_NATIVE_SETS = (
    "llvm_functions",
    "runtime_functions",
    "program_owned_functions",
    "reachable_program_functions",
    "unreachable_program_functions",
)


@dataclass
class _Collector:
    changes: list[dict[str, Any]] = field(default_factory=list)

    def add(
        self,
        section: str,
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
            "id": f"{section}:{path}:{kind}",
            "section": section,
            "path": path,
            "kind": kind,
            "classification": classification,
            "severity": severity,
            "before": before,
            "after": after,
        }
        if delta is not None:
            item["delta"] = delta
        self.changes.append(item)

    def ordered(self) -> list[dict[str, Any]]:
        return sorted(
            self.changes,
            key=lambda item: (
                str(item["section"]),
                str(item["path"]),
                str(item["kind"]),
                str(item["classification"]),
                str(item["severity"]),
            ),
        )


def compare_bundles(
    before: Bundle,
    after: Bundle,
    *,
    format_version: str = "v2",
    before_context: Mapping[str, Any] | None = None,
    after_context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Compare every stable evidence section available from two bundles."""
    if format_version not in _FORMATS:
        raise ValueError(
            f"unknown diff format version {format_version!r}; expected v1 or v2"
        )
    left = analyze_bundle(before)
    right = analyze_bundle(after)
    if format_version in {"v1", LEGACY_DIFF_FORMAT}:
        return _legacy(left, right)

    collector = _Collector()
    analysis = {
        "llvm": _metrics(
            _mapping(left.get("llvm")),
            _mapping(right.get("llvm")),
            "analysis.llvm",
            collector,
        ),
        "optimized_llvm": _metrics(
            _mapping(left.get("optimized_llvm")),
            _mapping(right.get("optimized_llvm")),
            "analysis.optimized_llvm",
            collector,
        ),
        "native": _native(
            _mapping(left.get("native")),
            _mapping(right.get("native")),
            collector,
        ),
        "diagnostics": _diagnostics(before, after, collector),
        "trace": _trace(before, after, collector),
        "evidence": _evidence(
            _mapping(left.get("evidence")),
            _mapping(right.get("evidence")),
            collector,
        ),
    }
    compiler = _compiler(left, right, collector)
    sources = _identity_section(
        _source_identities(before),
        _source_identities(after),
        "sources",
        collector,
    )
    artifacts = _identity_section(
        _entry_identities(before.manifest.get("artifacts")),
        _entry_identities(after.manifest.get("artifacts")),
        "artifacts",
        collector,
    )
    logs = _identity_section(
        _entry_identities(before.manifest.get("logs")),
        _entry_identities(after.manifest.get("logs")),
        "logs",
        collector,
    )
    manifest = _manifest(before, after, collector)
    remarks = _optimization_remarks(before, after, collector)
    supplemental = {
        "runtime": _supplemental(
            "runtime",
            before_context,
            after_context,
            "semantic",
            collector,
        ),
        "native_budget": _supplemental(
            "native_budget",
            before_context,
            after_context,
            "quality",
            collector,
        ),
        "optimized_llvm_budget": _supplemental(
            "optimized_llvm_budget",
            before_context,
            after_context,
            "quality",
            collector,
        ),
    }
    changes = collector.ordered()
    return {
        "format": DIFF_FORMAT,
        "summary": _summary(changes),
        "changes": changes,
        "compiler": compiler,
        "analysis": analysis,
        "sources": sources,
        "artifacts": artifacts,
        "logs": logs,
        "manifest": manifest,
        "optimization_remarks": remarks,
        "supplemental": supplemental,
        "compatibility": {
            "legacy_format": LEGACY_DIFF_FORMAT,
            "legacy_projection": _legacy(left, right),
            "usage": (
                "Pass format_version='v1' or use --format-version v1 for the "
                "original compact comparison."
            ),
        },
    }


def compare_bundles_v1(before: Bundle, after: Bundle) -> dict[str, Any]:
    """Return the original compact comparison shape."""
    return compare_bundles(before, after, format_version="v1")


def _legacy(left: Mapping[str, Any], right: Mapping[str, Any]) -> dict[str, Any]:
    left_llvm = cast(Mapping[str, int], left["llvm"])
    right_llvm = cast(Mapping[str, int], right["llvm"])
    left_trace = _mapping(left.get("trace"))
    right_trace = _mapping(right.get("trace"))
    return {
        "format": LEGACY_DIFF_FORMAT,
        "llvm_metrics": _counter_diff(left_llvm, right_llvm),
        "trace_actions": _counter_diff(
            _int_mapping(left_trace.get("actions")),
            _int_mapping(right_trace.get("actions")),
        ),
        "trace_passes": _counter_diff(
            _int_mapping(left_trace.get("passes")),
            _int_mapping(right_trace.get("passes")),
        ),
    }


def _compiler(
    left: Mapping[str, Any],
    right: Mapping[str, Any],
    collector: _Collector,
) -> dict[str, Any]:
    before = left.get("compiler_exit_code")
    after = right.get("compiler_exit_code")
    delta = _delta(before, after)
    collector.add(
        "compiler",
        "exit_code",
        "changed",
        "semantic",
        "error",
        before,
        after,
        delta=delta,
    )
    return {
        "changed": before != after,
        "exit_code": {"before": before, "after": after, "delta": delta},
    }


def _metrics(
    before: Mapping[str, Any],
    after: Mapping[str, Any],
    section: str,
    collector: _Collector,
) -> dict[str, Any]:
    metrics: dict[str, dict[str, Any]] = {}
    for name in sorted(set(before) | set(after)):
        left = before.get(name, 0)
        right = after.get(name, 0)
        delta = _delta(left, right)
        changed = left != right
        metrics[name] = {
            "before": left,
            "after": right,
            "delta": delta,
            "changed": changed,
        }
        collector.add(
            section,
            name,
            "metric-changed",
            "quality",
            _metric_severity(name, delta),
            left,
            right,
            delta=delta,
        )
    return {
        "changed": any(item["changed"] for item in metrics.values()),
        "metrics": metrics,
    }


def _metric_severity(name: str, delta: int | float | None) -> Severity:
    suspicious = {
        "alloca",
        "anonymous_ssa_lines",
        "identity_adds",
        "load",
        "poison_uses",
        "store",
        "undef_uses",
        "unreachable_program_instructions",
    }
    return "warning" if name in suspicious and delta not in {None, 0} else "info"


def _native(
    before: Mapping[str, Any],
    after: Mapping[str, Any],
    collector: _Collector,
) -> dict[str, Any]:
    scalars: dict[str, dict[str, Any]] = {}
    for name in _NATIVE_SCALARS:
        left = before.get(name)
        right = after.get(name)
        delta = _delta(left, right)
        scalars[name] = {
            "before": left,
            "after": right,
            "delta": delta,
            "changed": left != right,
        }
        collector.add(
            "analysis.native",
            name,
            "changed",
            _native_classification(name),
            _native_severity(name, right),
            left,
            right,
            delta=delta,
        )

    sets: dict[str, dict[str, Any]] = {}
    for name in _NATIVE_SETS:
        left = _string_set(before.get(name))
        right = _string_set(after.get(name))
        added = sorted(right - left)
        removed = sorted(left - right)
        sets[name] = {
            "before": sorted(left),
            "after": sorted(right),
            "added": added,
            "removed": removed,
            "changed": bool(added or removed),
        }
        for value in added:
            collector.add(
                "analysis.native",
                f"{name}.{value}",
                "added",
                "quality",
                "warning" if name == "unreachable_program_functions" else "info",
                None,
                value,
            )
        for value in removed:
            collector.add(
                "analysis.native",
                f"{name}.{value}",
                "removed",
                "quality",
                "warning",
                value,
                None,
            )

    functions = _native_functions(
        _mapping(before.get("functions")),
        _mapping(after.get("functions")),
        collector,
    )
    return {
        "changed": (
            any(item["changed"] for item in scalars.values())
            or any(item["changed"] for item in sets.values())
            or functions["changed"]
        ),
        "scalars": scalars,
        "sets": sets,
        "functions": functions,
    }


def _native_classification(name: str) -> Classification:
    if name in {"available", "supported", "failure_reason"}:
        return "evidence"
    if name in {"architecture", "object_format", "disassembler", "parser_format"}:
        return "provenance"
    return "quality"


def _native_severity(name: str, after: Any) -> Severity:
    if name in {"available", "supported", "reachability_complete"} and after is False:
        return "error"
    if name in {
        "failure_reason",
        "unreachable_program_instructions",
        "reachable_indirect_calls",
    }:
        return "warning"
    return "info"


def _native_functions(
    before: Mapping[str, Any],
    after: Mapping[str, Any],
    collector: _Collector,
) -> dict[str, Any]:
    left_names = set(before)
    right_names = set(after)
    added = sorted(right_names - left_names)
    removed = sorted(left_names - right_names)
    modified: dict[str, dict[str, Any]] = {}
    warning_metrics = {
        "indirect_calls",
        "padding_instructions",
        "backward_branches",
    }
    for name in sorted(left_names & right_names):
        left = _mapping(before.get(name))
        right = _mapping(after.get(name))
        fields: dict[str, Any] = {}
        for metric in sorted(set(left) | set(right)):
            before_value = left.get(metric)
            after_value = right.get(metric)
            if before_value == after_value:
                continue
            delta = _delta(before_value, after_value)
            fields[metric] = {
                "before": before_value,
                "after": after_value,
                "delta": delta,
            }
            collector.add(
                "analysis.native.functions",
                f"{name}.{metric}",
                "changed",
                "quality",
                "warning" if metric in warning_metrics else "info",
                before_value,
                after_value,
                delta=delta,
            )
        if fields:
            modified[name] = fields
    for name in added:
        collector.add(
            "analysis.native.functions",
            name,
            "added",
            "quality",
            "info",
            None,
            after[name],
        )
    for name in removed:
        collector.add(
            "analysis.native.functions",
            name,
            "removed",
            "quality",
            "warning",
            before[name],
            None,
        )
    return {
        "changed": bool(added or removed or modified),
        "added": added,
        "removed": removed,
        "modified": modified,
        "unchanged_count": len(left_names & right_names) - len(modified),
    }


def _diagnostics(
    before: Bundle,
    after: Bundle,
    collector: _Collector,
) -> dict[str, Any]:
    left_available, left = _diagnostic_records(before)
    right_available, right = _diagnostic_records(after)
    collector.add(
        "analysis.diagnostics",
        "available",
        "changed",
        "evidence",
        "error" if not right_available else "info",
        left_available,
        right_available,
    )
    left_by_id = {str(item["identity"]): item for item in left}
    right_by_id = {str(item["identity"]): item for item in right}
    added = [right_by_id[key] for key in sorted(set(right_by_id) - set(left_by_id))]
    removed = [left_by_id[key] for key in sorted(set(left_by_id) - set(right_by_id))]
    for item in added:
        severity = str(item.get("severity", "")).lower()
        collector.add(
            "analysis.diagnostics",
            str(item["identity"]),
            "added",
            "semantic",
            "error" if severity in {"error", "fatal"} else "warning",
            None,
            item,
        )
    for item in removed:
        collector.add(
            "analysis.diagnostics",
            str(item["identity"]),
            "removed",
            "semantic",
            "info",
            item,
            None,
        )
    return {
        "changed": left_available != right_available or bool(added or removed),
        "available": {"before": left_available, "after": right_available},
        "counts": {
            "before": len(left),
            "after": len(right),
            "delta": len(right) - len(left),
        },
        "severity_counts": {
            "before": _severity_counts(left),
            "after": _severity_counts(right),
        },
        "added": added,
        "removed": removed,
    }


def _diagnostic_records(bundle: Bundle) -> tuple[bool, list[dict[str, Any]]]:
    document = bundle.artifact_json("diagnostics")
    if not isinstance(document, Mapping):
        return False, []
    raw_items = document.get("diagnostics")
    items = raw_items if isinstance(raw_items, list) else []
    records: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, Mapping):
            continue
        record = {
            "code": _first_text(item, "code", "id", "diagnostic_code"),
            "severity": _first_text(item, "severity", "level"),
            "message": _first_text(item, "message", "text"),
            "location": _diagnostic_location(item),
        }
        records.append({**record, "identity": _identity(record)})
    return True, sorted(records, key=lambda item: str(item["identity"]))


def _diagnostic_location(item: Mapping[str, Any]) -> Any:
    for key in ("location", "span", "source", "range"):
        value = item.get(key)
        if value is not None:
            return _stable(value)
    fields = ("file", "path", "line", "column", "end_line", "end_column")
    location = {key: item.get(key) for key in fields if item.get(key) is not None}
    return location or None


def _severity_counts(records: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for record in records:
        severity = record.get("severity")
        counts[str(severity) if severity is not None else "unknown"] += 1
    return dict(sorted(counts.items()))


def _trace(before: Bundle, after: Bundle, collector: _Collector) -> dict[str, Any]:
    left_summary = _mapping(analyze_bundle(before).get("trace"))
    right_summary = _mapping(analyze_bundle(after).get("trace"))
    counters = {
        name: _counter_section(
            _int_mapping(left_summary.get(name)),
            _int_mapping(right_summary.get(name)),
            f"analysis.trace.{name}",
            collector,
        )
        for name in ("actions", "passes", "categories")
    }
    left = _trace_events(before)
    right = _trace_events(after)
    left_ids = [_identity(item) for item in left]
    right_ids = [_identity(item) for item in right]
    left_counts = Counter(left_ids)
    right_counts = Counter(right_ids)
    added_ids = sorted((right_counts - left_counts).elements())
    removed_ids = sorted((left_counts - right_counts).elements())
    added = [_event(right, identity) for identity in added_ids]
    removed = [_event(left, identity) for identity in removed_ids]
    order_changed = left_counts == right_counts and left_ids != right_ids
    collector.add(
        "analysis.trace",
        "event_count",
        "metric-changed",
        "provenance",
        "warning",
        len(left),
        len(right),
        delta=len(right) - len(left),
    )
    if order_changed:
        collector.add(
            "analysis.trace",
            "event_order",
            "reordered",
            "provenance",
            "warning",
            left_ids,
            right_ids,
        )
    for identity, event in zip(added_ids, added, strict=True):
        collector.add(
            "analysis.trace",
            identity,
            "event-added",
            "provenance",
            "warning",
            None,
            event,
        )
    for identity, event in zip(removed_ids, removed, strict=True):
        collector.add(
            "analysis.trace",
            identity,
            "event-removed",
            "provenance",
            "warning",
            event,
            None,
        )
    mismatches = [
        {"index": index, "before": left_id, "after": right_id}
        for index, (left_id, right_id) in enumerate(
            zip(left_ids, right_ids, strict=False)
        )
        if left_id != right_id
    ][:20]
    return {
        "changed": (
            any(item["changed"] for item in counters.values())
            or bool(added or removed or order_changed)
        ),
        "counters": counters,
        "events": {
            "before_count": len(left),
            "after_count": len(right),
            "added": added,
            "removed": removed,
            "order_changed": order_changed,
            "first_order_mismatches": mismatches,
        },
    }


def _trace_events(bundle: Bundle) -> list[dict[str, Any]]:
    document = bundle.artifact_json("trace")
    if not isinstance(document, Mapping):
        return []
    raw_events = document.get("events")
    events = raw_events if isinstance(raw_events, list) else []
    normalized: list[dict[str, Any]] = []
    for event in events:
        if isinstance(event, Mapping):
            ordered = sorted(
                event.items(),
                key=lambda pair: str(pair[0]),
            )
            normalized.append(
                {
                    str(key): _stable(value)
                    for key, value in ordered
                    if str(key) not in _VOLATILE_KEYS
                }
            )
    return normalized


def _event(
    events: Sequence[Mapping[str, Any]],
    identity: str,
) -> Mapping[str, Any] | None:
    return next((item for item in events if _identity(item) == identity), None)


def _counter_section(
    before: Mapping[str, int],
    after: Mapping[str, int],
    section: str,
    collector: _Collector,
) -> dict[str, Any]:
    items = _counter_diff(before, after)
    for name, values in items.items():
        collector.add(
            section,
            name,
            "counter-changed",
            "provenance",
            "warning",
            values["before"],
            values["after"],
            delta=values["delta"],
        )
    return {
        "changed": any(item["delta"] != 0 for item in items.values()),
        "items": items,
    }


def _evidence(
    before: Mapping[str, Any],
    after: Mapping[str, Any],
    collector: _Collector,
) -> dict[str, Any]:
    items: dict[str, dict[str, Any]] = {}
    for name in sorted(set(before) | set(after)):
        left = bool(before.get(name, False))
        right = bool(after.get(name, False))
        items[name] = {"before": left, "after": right, "changed": left != right}
        collector.add(
            "analysis.evidence",
            name,
            "availability-changed",
            "evidence",
            "error" if left and not right else "info",
            left,
            right,
        )
    return {
        "changed": any(item["changed"] for item in items.values()),
        "items": items,
    }


def _identity_section(
    before: Mapping[str, Mapping[str, Any]],
    after: Mapping[str, Mapping[str, Any]],
    section: str,
    collector: _Collector,
) -> dict[str, Any]:
    items: dict[str, dict[str, Any]] = {}
    for name in sorted(set(before) | set(after)):
        left = before.get(name)
        right = after.get(name)
        status = _identity_status(left, right)
        items[name] = {"status": status, "before": left, "after": right}
        if status != "unchanged":
            collector.add(
                section,
                name,
                status,
                "provenance" if section == "sources" else "evidence",
                "error" if status == "removed" else "warning",
                left,
                right,
            )
    return {
        "changed": any(item["status"] != "unchanged" for item in items.values()),
        "items": items,
    }


def _identity_status(
    before: Mapping[str, Any] | None,
    after: Mapping[str, Any] | None,
) -> str:
    if before is None:
        return "added"
    if after is None:
        return "removed"
    if before == after:
        return "unchanged"
    if before.get("sha256") != after.get("sha256"):
        return "hash-changed"
    return "metadata-changed"


def _source_identities(bundle: Bundle) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for position, entry in enumerate(bundle.sources):
        raw_index = entry.get("index")
        index = raw_index if isinstance(raw_index, int) else position
        result[f"{index:03d}"] = {
            "index": index,
            "path": entry.get("path"),
            "size": entry.get("size"),
            "sha256": entry.get("sha256"),
        }
    return result


def _entry_identities(value: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(value, Mapping):
        return {}
    result: dict[str, dict[str, Any]] = {}
    for name, entry in value.items():
        if isinstance(entry, str):
            result[str(name)] = {"path": entry, "size": None, "sha256": None}
        elif isinstance(entry, Mapping):
            result[str(name)] = {
                "path": entry.get("path"),
                "size": entry.get("size"),
                "sha256": entry.get("sha256"),
            }
    return dict(sorted(result.items()))


def _manifest(
    before: Bundle,
    after: Bundle,
    collector: _Collector,
) -> dict[str, Any]:
    left = {
        "bundle_format": before.manifest.get("format"),
        "compiler": _stable(before.manifest.get("compiler")),
        "build_manifest": _stable(before.artifact_json("build_manifest")),
    }
    right = {
        "bundle_format": after.manifest.get("format"),
        "compiler": _stable(after.manifest.get("compiler")),
        "build_manifest": _stable(after.artifact_json("build_manifest")),
    }
    differences = _deep_differences(left, right)
    for item in differences:
        path = str(item["path"])
        collector.add(
            "manifest",
            path,
            str(item["kind"]),
            "provenance",
            "error" if path in {"bundle_format", "compiler.exit_code"} else "warning",
            item.get("before"),
            item.get("after"),
            delta=_optional_delta(item),
        )
    return {
        "changed": bool(differences),
        "differences": differences,
        "before": left,
        "after": right,
    }


def _optimization_remarks(
    before: Bundle,
    after: Bundle,
    collector: _Collector,
) -> dict[str, Any]:
    left_available, left = _document_records(
        before.artifact_text("optimization_record")
    )
    right_available, right = _document_records(
        after.artifact_text("optimization_record")
    )
    collector.add(
        "optimization_remarks",
        "available",
        "changed",
        "evidence",
        "error" if not right_available else "info",
        left_available,
        right_available,
    )
    left_counts = Counter(str(item["sha256"]) for item in left)
    right_counts = Counter(str(item["sha256"]) for item in right)
    added_hashes = sorted((right_counts - left_counts).elements())
    removed_hashes = sorted((left_counts - right_counts).elements())
    added = [_record(left=right, digest=digest) for digest in added_hashes]
    removed = [_record(left=left, digest=digest) for digest in removed_hashes]
    for item in added:
        collector.add(
            "optimization_remarks",
            str(item["sha256"]),
            "added",
            "quality",
            "warning",
            None,
            item,
        )
    for item in removed:
        collector.add(
            "optimization_remarks",
            str(item["sha256"]),
            "removed",
            "quality",
            "warning",
            item,
            None,
        )
    return {
        "changed": left_available != right_available or bool(added or removed),
        "available": {"before": left_available, "after": right_available},
        "document_counts": {
            "before": len(left),
            "after": len(right),
            "delta": len(right) - len(left),
        },
        "added": added,
        "removed": removed,
    }


def _document_records(text: str | None) -> tuple[bool, list[dict[str, Any]]]:
    if text is None:
        return False, []
    documents: list[str] = []
    current: list[str] = []
    for line in text.replace("\r\n", "\n").splitlines():
        if line.strip() == "---" and current:
            documents.append("\n".join(current).rstrip() + "\n")
            current = []
        current.append(line.rstrip())
    if current:
        documents.append("\n".join(current).rstrip() + "\n")
    records = []
    for index, document in enumerate(documents):
        data = document.encode("utf-8")
        summary = next(
            (line.strip() for line in document.splitlines() if line.strip()),
            "",
        )
        records.append(
            {
                "index": index,
                "sha256": hashlib.sha256(data).hexdigest(),
                "bytes": len(data),
                "summary": summary[:160],
            }
        )
    return True, records


def _record(
    *,
    left: Sequence[Mapping[str, Any]],
    digest: str,
) -> Mapping[str, Any]:
    return next(item for item in left if item.get("sha256") == digest)


def _supplemental(
    name: str,
    before_context: Mapping[str, Any] | None,
    after_context: Mapping[str, Any] | None,
    classification: Literal["semantic", "quality"],
    collector: _Collector,
) -> dict[str, Any]:
    if before_context is None and after_context is None:
        return {
            "available": False,
            "changed": False,
            "reason": (
                "not stored in portable bundles; compiler-audit supplies runtime "
                "and contract results"
            ),
            "differences": [],
        }
    left_available = before_context is not None and name in before_context
    right_available = after_context is not None and name in after_context
    raw_left = before_context.get(name) if before_context is not None else None
    raw_right = after_context.get(name) if after_context is not None else None
    left = _stable_runtime(raw_left) if name == "runtime" else _stable(raw_left)
    right = _stable_runtime(raw_right) if name == "runtime" else _stable(raw_right)
    collector.add(
        f"supplemental.{name}",
        "available",
        "changed",
        "evidence",
        "error" if not right_available else "info",
        left_available,
        right_available,
    )
    differences = _deep_differences(left, right)
    for item in differences:
        collector.add(
            f"supplemental.{name}",
            str(item["path"]),
            str(item["kind"]),
            classification,
            "error" if classification == "semantic" else "warning",
            item.get("before"),
            item.get("after"),
            delta=_optional_delta(item),
        )
    return {
        "available": left_available or right_available,
        "changed": left_available != right_available or bool(differences),
        "before_available": left_available,
        "after_available": right_available,
        "differences": differences,
        "before": left,
        "after": right,
    }


def _deep_differences(
    before: Any,
    after: Any,
    path: str = "",
) -> list[dict[str, Any]]:
    if before == after:
        return []
    if isinstance(before, Mapping) and isinstance(after, Mapping):
        differences: list[dict[str, Any]] = []
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
        return [
            {
                "path": path or "$",
                "kind": "sequence-changed",
                "before": before,
                "after": after,
            }
        ]
    return [
        {
            "path": path or "$",
            "kind": "changed",
            "before": before,
            "after": after,
            "delta": _delta(before, after),
        }
    ]


def _stable(value: Any) -> Any:
    return _stable_with_keys(value, _VOLATILE_KEYS)


def _stable_runtime(value: Any) -> Any:
    return _stable_with_keys(value, _RUNTIME_VOLATILE_KEYS)


def _stable_with_keys(value: Any, volatile: frozenset[str]) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): _stable_with_keys(item, volatile)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
            if str(key) not in volatile
        }
    if isinstance(value, (list, tuple)):
        return [_stable_with_keys(item, volatile) for item in value]
    return value


def _summary(changes: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    classifications: Counter[str] = Counter()
    severities: Counter[str] = Counter()
    sections: set[str] = set()
    for change in changes:
        classifications[str(change["classification"])] += 1
        severities[str(change["severity"])] += 1
        sections.add(str(change["section"]))
    return {
        "changed": bool(changes),
        "total_changes": len(changes),
        "by_classification": dict(sorted(classifications.items())),
        "by_severity": dict(sorted(severities.items())),
        "changed_sections": sorted(sections),
        "has_errors": severities["error"] > 0,
        "has_warnings": severities["warning"] > 0,
    }


def _counter_diff(
    before: Mapping[str, int],
    after: Mapping[str, int],
) -> dict[str, dict[str, int]]:
    return {
        name: {
            "before": int(before.get(name, 0)),
            "after": int(after.get(name, 0)),
            "delta": int(after.get(name, 0)) - int(before.get(name, 0)),
        }
        for name in sorted(set(before) | set(after))
    }


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _int_mapping(value: Any) -> Mapping[str, int]:
    if not isinstance(value, Mapping):
        return {}
    return {
        str(key): item
        for key, item in value.items()
        if isinstance(item, int) and not isinstance(item, bool)
    }


def _string_set(value: Any) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {item for item in value if isinstance(item, str)}


def _first_text(item: Mapping[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = item.get(key)
        if isinstance(value, str):
            return value
    return None


def _delta(before: Any, after: Any) -> int | float | None:
    if (
        isinstance(before, (int, float))
        and not isinstance(before, bool)
        and isinstance(after, (int, float))
        and not isinstance(after, bool)
    ):
        return after - before
    return None


def _optional_delta(item: Mapping[str, Any]) -> int | float | None:
    value = item.get("delta")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value
    return None


def _identity(value: Any) -> str:
    canonical = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()
