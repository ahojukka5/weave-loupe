"""Deterministic self-contained HTML reports."""

from __future__ import annotations

import html
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, cast

from weave_loupe.analysis import analyze_bundle
from weave_loupe.bundle import Bundle


def render_bundle_report(bundle: Bundle) -> str:
    """Render a self-contained HTML report without scripts or remote assets."""
    analysis = analyze_bundle(bundle)
    llvm = cast(Mapping[str, Any], analysis["llvm"])
    sources = "".join(
        _details(
            f"Source {entry.get('index', '?')}: {entry.get('input', entry['path'])}",
            bundle.read_text(str(entry["path"])),
        )
        for entry in bundle.sources
    )
    artifacts = "".join(
        _details(label, bundle.artifact_text(name) or "(not produced)")
        for name, label in (
            ("wir", "WIR"),
            ("llvm", "LLVM IR with provenance"),
            ("diagnostics", "Diagnostics JSON"),
            ("trace", "Compilation trace JSON"),
            ("build_manifest", "Build manifest JSON"),
        )
    )
    metrics = "".join(
        f"<tr><th>{html.escape(name)}</th><td>{html.escape(str(value))}</td></tr>"
        for name, value in llvm.items()
    )
    analysis_json = html.escape(
        json.dumps(analysis, indent=2, sort_keys=True, ensure_ascii=False)
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Weave Loupe compiler report</title>
{_styles()}
</head>
<body>
<h1>Weave Loupe compiler report</h1>
<div class="summary">
<div class="card">
<h2>Compiler</h2>
<p>Exit code: <strong>{analysis["compiler_exit_code"]}</strong></p>
</div>
<div class="card">
<h2>Trace</h2>
<p>Events: <strong>
{cast(Mapping[str, Any], analysis["trace"])["events"]}
</strong></p>
</div>
<div class="card">
<h2>LLVM</h2>
<p>Instructions: <strong>{llvm.get("instructions", 0)}</strong></p>
</div>
</div>
<h2>LLVM structural metrics</h2>
<table><tbody>{metrics}</tbody></table>
<h2>Source inputs</h2>
{sources}
<h2>Compiler artifacts</h2>
{artifacts}
<details>
<summary>Normalized analysis JSON</summary>
<pre><code>{analysis_json}</code></pre>
</details>
</body>
</html>
"""


def render_diff_report(diff: Mapping[str, Any]) -> str:
    """Render a self-contained HTML bundle comparison."""
    if diff.get("format") == "weave-loupe-diff-v1":
        return _render_diff_v1(diff)
    return _render_diff_v2(diff)


def _render_diff_v2(diff: Mapping[str, Any]) -> str:
    summary = _mapping(diff.get("summary"))
    analysis = _mapping(diff.get("analysis"))
    changes = _sequence(diff.get("changes"))
    classifications = _mapping(summary.get("by_classification"))
    severities = _mapping(summary.get("by_severity"))
    raw_metrics = _mapping(_mapping(analysis.get("llvm")).get("metrics"))
    optimized_metrics = _mapping(
        _mapping(analysis.get("optimized_llvm")).get("metrics")
    )
    native = _mapping(analysis.get("native"))
    diagnostics = _mapping(analysis.get("diagnostics"))
    supplemental = _mapping(diff.get("supplemental"))
    raw = html.escape(json.dumps(diff, indent=2, sort_keys=True, ensure_ascii=False))
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Weave Loupe complete evidence comparison</title>
{_styles()}
</head><body>
<h1>Weave Loupe complete evidence comparison</h1>
<p><code>{html.escape(str(diff.get("format", "unknown")))}</code></p>
<div class="summary">
{_card("Changes", summary.get("total_changes", 0))}
{_card("Errors", severities.get("error", 0), "bad")}
{_card("Warnings", severities.get("warning", 0), "warn")}
{_card("Semantic", classifications.get("semantic", 0))}
{_card("Quality", classifications.get("quality", 0))}
{_card("Evidence", classifications.get("evidence", 0))}
</div>
<nav class="card">
<a href="#changes">Changes</a>
<a href="#llvm">LLVM</a>
<a href="#native">Native</a>
<a href="#diagnostics">Diagnostics</a>
<a href="#artifacts">Artifacts</a>
<a href="#runtime">Runtime and contracts</a>
<a href="#manifest">Manifest and remarks</a>
</nav>
<section id="changes">
<h2>Classified changes</h2>
{_changes_table(changes)}
</section>
<section id="llvm">
<h2>Raw LLVM metrics</h2>
{_metric_table(raw_metrics)}
<h2>Optimized LLVM metrics</h2>
{_metric_table(optimized_metrics)}
</section>
<section id="native">
<h2>Native code and reachability</h2>
{_native_summary(native)}
</section>
<section id="diagnostics">
<h2>Diagnostics</h2>
{_json_details("Normalized diagnostic changes", diagnostics)}
</section>
<section id="artifacts">
<h2>Sources, artifacts, and logs</h2>
{_identity_table("Sources", _mapping(diff.get("sources")))}
{_identity_table("Artifacts", _mapping(diff.get("artifacts")))}
{_identity_table("Logs", _mapping(diff.get("logs")))}
</section>
<section id="runtime">
<h2>Runtime and deterministic contracts</h2>
{_supplemental_table(supplemental)}
</section>
<section id="manifest">
<h2>Manifest and optimization remarks</h2>
{_json_details("Manifest comparison", diff.get("manifest"))}
{_json_details("Optimization remarks", diff.get("optimization_remarks"))}
</section>
<details><summary>Complete comparison JSON</summary><pre>{raw}</pre></details>
</body></html>
"""


def _render_diff_v1(diff: Mapping[str, Any]) -> str:
    metrics = cast(Mapping[str, Mapping[str, int]], diff.get("llvm_metrics", {}))
    rows = "".join(
        "<tr>"
        f"<th>{html.escape(name)}</th>"
        f"<td>{values['before']}</td><td>{values['after']}</td>"
        f"<td>{values['delta']:+d}</td>"
        "</tr>"
        for name, values in metrics.items()
    )
    raw = html.escape(json.dumps(diff, indent=2, sort_keys=True, ensure_ascii=False))
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Weave Loupe comparison</title>
{_styles()}
</head><body><h1>Weave Loupe comparison</h1>
<p>Legacy <code>weave-loupe-diff-v1</code> output.</p>
<table>
<thead>
<tr><th>LLVM metric</th><th>Before</th><th>After</th><th>Delta</th></tr>
</thead>
<tbody>{rows}</tbody>
</table>
<details><summary>Complete comparison JSON</summary><pre>{raw}</pre></details>
</body></html>
"""


def _changes_table(changes: Sequence[object]) -> str:
    if not changes:
        return '<p class="good">No stable evidence changes detected.</p>'
    rows = []
    for raw in changes:
        item = _mapping(raw)
        severity = html.escape(str(item.get("severity", "unknown")))
        rows.append(
            "<tr>"
            f'<td><span class="badge {severity}">{severity}</span></td>'
            f"<td>{html.escape(str(item.get('classification', '')))}</td>"
            f"<td><code>{html.escape(str(item.get('section', '')))}</code></td>"
            f"<td><code>{html.escape(str(item.get('path', '')))}</code></td>"
            f"<td>{html.escape(str(item.get('kind', '')))}</td>"
            f"<td>{_compact(item.get('before'))}</td>"
            f"<td>{_compact(item.get('after'))}</td>"
            "</tr>"
        )
    return (
        "<table><thead><tr>"
        "<th>Severity</th><th>Class</th><th>Section</th><th>Path</th>"
        "<th>Kind</th><th>Before</th><th>After</th>"
        "</tr></thead><tbody>" + "".join(rows) + "</tbody></table>"
    )


def _metric_table(metrics: Mapping[str, Any]) -> str:
    rows = []
    for name, raw in metrics.items():
        item = _mapping(raw)
        if item.get("changed") is not True:
            continue
        rows.append(
            "<tr>"
            f"<th>{html.escape(name)}</th>"
            f"<td>{_compact(item.get('before'))}</td>"
            f"<td>{_compact(item.get('after'))}</td>"
            f"<td>{_compact(item.get('delta'))}</td>"
            "</tr>"
        )
    if not rows:
        return '<p class="good">No metric changes.</p>'
    return (
        "<table><thead><tr>"
        "<th>Metric</th><th>Before</th><th>After</th><th>Delta</th>"
        "</tr></thead><tbody>" + "".join(rows) + "</tbody></table>"
    )


def _native_summary(native: Mapping[str, Any]) -> str:
    functions = _mapping(native.get("functions"))
    added = _sequence(functions.get("added"))
    removed = _sequence(functions.get("removed"))
    modified = _mapping(functions.get("modified"))
    return (
        f"<p>Added functions: {_inline_list(added)}</p>"
        f"<p>Removed functions: {_inline_list(removed)}</p>"
        f"<p>Modified functions: {_inline_list(list(modified))}</p>"
        + _json_details("Complete native comparison", native)
    )


def _identity_table(title: str, section: Mapping[str, Any]) -> str:
    items = _mapping(section.get("items"))
    rows = []
    for name, raw in items.items():
        item = _mapping(raw)
        if item.get("status") == "unchanged":
            continue
        rows.append(
            "<tr>"
            f"<th><code>{html.escape(name)}</code></th>"
            f"<td>{html.escape(str(item.get('status', 'unknown')))}</td>"
            f"<td>{_compact(item.get('before'))}</td>"
            f"<td>{_compact(item.get('after'))}</td>"
            "</tr>"
        )
    body = (
        "<p>No changes.</p>"
        if not rows
        else (
            "<table><thead><tr>"
            "<th>Name</th><th>Status</th><th>Before</th><th>After</th>"
            "</tr></thead><tbody>" + "".join(rows) + "</tbody></table>"
        )
    )
    return f"<h3>{html.escape(title)}</h3>{body}"


def _supplemental_table(supplemental: Mapping[str, Any]) -> str:
    rows = []
    for name, raw in supplemental.items():
        item = _mapping(raw)
        rows.append(
            "<tr>"
            f"<th>{html.escape(name)}</th>"
            f"<td>{html.escape(str(item.get('available', False)))}</td>"
            f"<td>{html.escape(str(item.get('changed', False)))}</td>"
            f"<td>{html.escape(str(item.get('reason', '')))}</td>"
            "</tr>"
        )
    return (
        "<table><thead><tr>"
        "<th>Section</th><th>Available</th><th>Changed</th><th>Notes</th>"
        "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table>"
        + _json_details("Complete runtime and contract comparison", supplemental)
    )


def _card(title: str, value: object, class_name: str = "") -> str:
    css = f" {class_name}" if class_name else ""
    return (
        f'<div class="card{css}"><h2>{html.escape(title)}</h2>'
        f"<p><strong>{html.escape(str(value))}</strong></p></div>"
    )


def _compact(value: object) -> str:
    text = json.dumps(value, sort_keys=True, ensure_ascii=False)
    if len(text) > 240:
        text = text[:237] + "..."
    return f"<code>{html.escape(text)}</code>"


def _inline_list(values: Sequence[object]) -> str:
    if not values:
        return "none"
    return ", ".join(f"<code>{html.escape(str(value))}</code>" for value in values)


def _json_details(title: str, value: object) -> str:
    serialized = json.dumps(
        value,
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
    )
    content = html.escape(serialized)
    return (
        f"<details><summary>{html.escape(title)}</summary>"
        f"<pre><code>{content}</code></pre></details>"
    )


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: object) -> Sequence[object]:
    return value if isinstance(value, list) else []


def write_report(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _details(title: str, content: str) -> str:
    return (
        f"<details><summary>{html.escape(title)}</summary>"
        f"<pre><code>{html.escape(content)}</code></pre></details>"
    )


def _styles() -> str:
    return """<style>
:root { color-scheme: light dark; font-family: system-ui, sans-serif; }
body { max-width: 1200px; margin: 0 auto; padding: 2rem; line-height: 1.5; }
h1, h2 { line-height: 1.15; }
.summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(10rem, 1fr));
  gap: 1rem;
}
.card, details {
  border: 1px solid #8886;
  border-radius: .6rem;
  padding: 1rem;
  margin: 1rem 0;
}
nav { display: flex; gap: 1rem; flex-wrap: wrap; }
table { border-collapse: collapse; width: 100%; }
th, td {
  border-bottom: 1px solid #8885;
  padding: .4rem .5rem;
  text-align: left;
  vertical-align: top;
}
pre { overflow-x: auto; white-space: pre; tab-size: 2; }
code { font-family: ui-monospace, SFMono-Regular, Consolas, monospace; }
.bad, .error { font-weight: 700; }
.warn, .warning { font-weight: 600; }
.good { font-weight: 600; }
.badge { border: 1px solid #8888; border-radius: .35rem; padding: .1rem .35rem; }
section { scroll-margin-top: 1rem; }
</style>"""
