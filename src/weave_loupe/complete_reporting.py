"""WIR-aware extensions for deterministic self-contained HTML reports."""

from __future__ import annotations

import html
import json
from collections.abc import Mapping
from typing import Any

from weave_loupe.analysis import analyze_bundle
from weave_loupe.bundle import Bundle
from weave_loupe.reporting import render_bundle_report as _render_bundle_report
from weave_loupe.reporting import render_diff_report as _render_diff_report


def render_bundle_report(bundle: Bundle) -> str:
    """Render the established bundle report with focused WIR analysis."""
    base = _render_bundle_report(bundle)
    wir = _mapping(analyze_bundle(bundle).get("wir"))
    metrics = _mapping(wir.get("metrics"))
    card = (
        '<div class="card">\n<h2>WIR</h2>\n'
        f"<p>Valid: <strong>{html.escape(str(wir.get('valid', False)))}</strong></p>\n"
        "<p>Functions: <strong>"
        f"{html.escape(str(metrics.get('functions', 0)))}"
        "</strong></p>\n"
        "</div>\n"
    )
    section = (
        "<h2>WIR structural analysis</h2>\n"
        + _metric_table(metrics)
        + _details("WIR functions and control flow", wir.get("functions"))
        + _details("WIR provenance", wir.get("provenance"))
        + _details("WIR-to-LLVM correspondence", wir.get("cross_stage"))
    )
    llvm_card = '<div class="card">\n<h2>LLVM</h2>'
    base = base.replace(llvm_card, card + llvm_card, 1)
    llvm_metrics = "<h2>LLVM structural metrics</h2>"
    return base.replace(llvm_metrics, section + llvm_metrics, 1)


def render_diff_report(diff: Mapping[str, Any]) -> str:
    """Render the established diff report with focused WIR comparison."""
    base = _render_diff_report(diff)
    if diff.get("format") == "weave-loupe-diff-v1":
        return base
    analysis = _mapping(diff.get("analysis"))
    wir = _mapping(analysis.get("wir"))
    section = (
        '<section id="wir">\n<h2>WIR structure and lowering correspondence</h2>\n'
        + _metric_delta_table(_mapping(wir.get("metrics")))
        + _function_summary(_mapping(wir.get("functions")))
        + _details("Complete WIR comparison", wir)
        + "\n</section>\n"
    )
    base = base.replace(
        '<a href="#llvm">LLVM</a>',
        '<a href="#wir">WIR</a>\n<a href="#llvm">LLVM</a>',
        1,
    )
    return base.replace('<section id="llvm">', section + '<section id="llvm">', 1)


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


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]
