"""Focused extensions for deterministic self-contained HTML reports."""

from __future__ import annotations

import html
import json
from collections import defaultdict
from collections.abc import Mapping, Sequence
from typing import Any

from weave_loupe.analysis import analyze_bundle
from weave_loupe.bundle import Bundle
from weave_loupe.reporting import render_bundle_report as _render_bundle_report
from weave_loupe.reporting import render_diff_report as _render_diff_report


def render_bundle_report(bundle: Bundle) -> str:
    """Render the established report with WIR and optimization remarks."""
    base = _render_bundle_report(bundle)
    analysis = analyze_bundle(bundle)
    wir = _mapping(analysis.get("wir"))
    metrics = _mapping(wir.get("metrics"))
    remarks = _mapping(analysis.get("optimization_remarks"))
    remark_summary = _mapping(remarks.get("summary"))
    cards = (
        '<div class="card">\n<h2>WIR</h2>\n'
        f"<p>Valid: <strong>{html.escape(str(wir.get('valid', False)))}</strong></p>\n"
        "<p>Functions: <strong>"
        f"{html.escape(str(metrics.get('functions', 0)))}"
        "</strong></p>\n"
        "</div>\n"
        '<div class="card">\n<h2>Optimization remarks</h2>\n'
        "<p>Valid: <strong>"
        f"{html.escape(str(remarks.get('valid', False)))}"
        "</strong></p>\n"
        "<p>Records: <strong>"
        f"{html.escape(str(remark_summary.get('total', 0)))}"
        "</strong></p>\n"
        "</div>\n"
    )
    sections = (
        "<h2>WIR structural analysis</h2>\n"
        + _metric_table(metrics)
        + _details("WIR functions and control flow", wir.get("functions"))
        + _details("WIR provenance", wir.get("provenance"))
        + _details("WIR-to-LLVM correspondence", wir.get("cross_stage"))
        + "<h2>LLVM optimization remarks</h2>\n"
        + _remark_summary(remarks)
    )
    llvm_card = '<div class="card">\n<h2>LLVM</h2>'
    base = base.replace(llvm_card, cards + llvm_card, 1)
    llvm_metrics = "<h2>LLVM structural metrics</h2>"
    return base.replace(llvm_metrics, sections + llvm_metrics, 1)


def render_diff_report(diff: Mapping[str, Any]) -> str:
    """Render the established diff report with WIR and remark comparisons."""
    base = _render_diff_report(diff)
    if diff.get("format") == "weave-loupe-diff-v1":
        return base
    analysis = _mapping(diff.get("analysis"))
    wir = _mapping(analysis.get("wir"))
    wir_section = (
        '<section id="wir">\n<h2>WIR structure and lowering correspondence</h2>\n'
        + _metric_delta_table(_mapping(wir.get("metrics")))
        + _function_summary(_mapping(wir.get("functions")))
        + _details("Complete WIR comparison", wir)
        + "\n</section>\n"
    )
    remarks = _mapping(diff.get("optimization_remarks"))
    remark_section = (
        '<section id="optimization-remarks">\n'
        "<h2>LLVM optimization remark changes</h2>\n"
        + _remark_counter_deltas(_mapping(remarks.get("counters")))
        + _changed_remark_table("Added remarks", remarks.get("added"))
        + _changed_remark_table("Removed remarks", remarks.get("removed"))
        + _details("Complete optimization remark comparison", remarks)
        + "\n</section>\n"
    )
    base = base.replace(
        '<a href="#llvm">LLVM</a>',
        '<a href="#wir">WIR</a>\n<a href="#llvm">LLVM</a>',
        1,
    )
    base = base.replace(
        '<a href="#manifest">Manifest and remarks</a>',
        '<a href="#optimization-remarks">Optimization remarks</a>\n'
        '<a href="#manifest">Manifest</a>',
        1,
    )
    base = base.replace('<section id="llvm">', wir_section + '<section id="llvm">', 1)
    return base.replace(
        '<section id="manifest">',
        remark_section + '<section id="manifest">',
        1,
    )


def _remark_summary(remarks: Mapping[str, Any]) -> str:
    summary = _mapping(remarks.get("summary"))
    status_class = "good" if remarks.get("valid") is True else "bad"
    status = (
        f'<p class="{status_class}">Valid: '
        f"<strong>{html.escape(str(remarks.get('valid', False)))}</strong></p>"
    )
    return (
        status
        + _named_counts("Remark categories", _mapping(summary.get("by_category")))
        + _named_counts("Optimization passes", _mapping(summary.get("by_pass")))
        + _missed_groups(summary.get("highest_value_missed"))
        + _details("Complete normalized optimization remarks", remarks)
    )


def _named_counts(title: str, values: Mapping[str, Any]) -> str:
    rows = "".join(
        f"<tr><th>{html.escape(str(name))}</th><td>{html.escape(str(value))}</td></tr>"
        for name, value in sorted(values.items())
    )
    if not rows:
        return f"<h3>{html.escape(title)}</h3><p>None.</p>"
    return f"<h3>{html.escape(title)}</h3><table><tbody>{rows}</tbody></table>"


def _missed_groups(value: object) -> str:
    groups: dict[tuple[str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for item in _mapping_sequence(value):
        function = str(item.get("function") or "unknown")
        pass_name = str(item.get("pass") or "unknown")
        groups[(function, pass_name)].append(item)
    if not groups:
        return "<h3>Highest-value missed optimizations</h3><p>None.</p>"
    sections = ["<h3>Highest-value missed optimizations</h3>"]
    for (function, pass_name), records in sorted(groups.items()):
        rows = "".join(_remark_row(item) for item in records)
        sections.append(
            f"<h4><code>{html.escape(function)}</code> / "
            f"<code>{html.escape(pass_name)}</code></h4>"
            "<table><thead><tr><th>Name</th><th>Hotness</th>"
            f"<th>Location</th><th>Message</th></tr></thead><tbody>{rows}</tbody></table>"
        )
    return "".join(sections)


def _remark_row(item: Mapping[str, Any]) -> str:
    location = _mapping(item.get("location"))
    location_text = ""
    if location:
        location_text = "{}:{}:{}".format(
            location.get("file") or "?",
            location.get("line") or "?",
            location.get("column") or "?",
        )
    return (
        "<tr>"
        f"<td>{html.escape(str(item.get('name') or 'unknown'))}</td>"
        f"<td>{html.escape(str(item.get('hotness') or ''))}</td>"
        f"<td>{html.escape(location_text)}</td>"
        f"<td>{html.escape(str(item.get('message') or ''))}</td>"
        "</tr>"
    )


def _remark_counter_deltas(counters: Mapping[str, Any]) -> str:
    categories = _mapping(counters.get("by_category"))
    rows: list[str] = []
    for name, raw in sorted(categories.items()):
        item = _mapping(raw)
        if item.get("changed") is not True:
            continue
        rows.append(
            "<tr>"
            f"<th>{html.escape(str(name))}</th>"
            f"<td>{_compact(item.get('before'))}</td>"
            f"<td>{_compact(item.get('after'))}</td>"
            f"<td>{_compact(item.get('delta'))}</td>"
            "</tr>"
        )
    if not rows:
        return '<p class="good">No optimization remark category changes.</p>'
    return (
        "<table><thead><tr><th>Category</th><th>Before</th>"
        "<th>After</th><th>Delta</th></tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table>"
    )


def _changed_remark_table(title: str, value: object) -> str:
    records = _mapping_sequence(value)
    if not records:
        return f"<h3>{html.escape(title)}</h3><p>None.</p>"
    rows = "".join(
        "<tr>"
        f"<td>{html.escape(str(item.get('category') or 'unknown'))}</td>"
        f"<td>{html.escape(str(item.get('function') or 'unknown'))}</td>"
        f"<td>{html.escape(str(item.get('pass') or 'unknown'))}</td>"
        f"<td>{html.escape(str(item.get('name') or 'unknown'))}</td>"
        f"<td>{html.escape(str(item.get('hotness') or ''))}</td>"
        f"<td>{html.escape(str(item.get('message') or ''))}</td>"
        "</tr>"
        for item in records
    )
    return (
        f"<h3>{html.escape(title)}</h3>"
        "<table><thead><tr><th>Category</th><th>Function</th>"
        "<th>Pass</th><th>Name</th><th>Hotness</th><th>Message</th>"
        "</tr></thead><tbody>" + rows + "</tbody></table>"
    )


def _metric_table(metrics: Mapping[str, Any]) -> str:
    rows = "".join(
        f"<tr><th>{html.escape(str(name))}</th><td>{html.escape(str(value))}</td></tr>"
        for name, value in sorted(metrics.items())
    )
    return f"<table><tbody>{rows}</tbody></table>" if rows else "<p>No WIR metrics.</p>"


def _metric_delta_table(metrics: Mapping[str, Any]) -> str:
    rows: list[str] = []
    for name, raw in sorted(metrics.items()):
        value = _mapping(raw)
        if value.get("changed") is not True:
            continue
        rows.append(
            "<tr>"
            f"<th>{html.escape(str(name))}</th>"
            f"<td>{_compact(value.get('before'))}</td>"
            f"<td>{_compact(value.get('after'))}</td>"
            f"<td>{_compact(value.get('delta'))}</td>"
            "</tr>"
        )
    if not rows:
        return '<p class="good">No WIR metric changes.</p>'
    return (
        "<table><thead><tr>"
        "<th>WIR metric</th><th>Before</th><th>After</th><th>Delta</th>"
        "</tr></thead><tbody>" + "".join(rows) + "</tbody></table>"
    )


def _function_summary(functions: Mapping[str, Any]) -> str:
    added = _string_list(functions.get("added"))
    removed = _string_list(functions.get("removed"))
    modified = _string_list(functions.get("modified"))
    return (
        f"<p>Added functions: {_inline(added)}</p>"
        f"<p>Removed functions: {_inline(removed)}</p>"
        f"<p>Modified functions: {_inline(modified)}</p>"
    )


def _details(title: str, value: object) -> str:
    content = html.escape(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False)
    )
    return (
        f"<details><summary>{html.escape(title)}</summary>"
        f"<pre><code>{content}</code></pre></details>"
    )


def _compact(value: object) -> str:
    content = json.dumps(value, sort_keys=True, ensure_ascii=False)
    return f"<code>{html.escape(content)}</code>"


def _inline(values: list[str]) -> str:
    if not values:
        return "none"
    return ", ".join(f"<code>{html.escape(value)}</code>" for value in values)


def _mapping(value: object) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}


def _mapping_sequence(value: object) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]
