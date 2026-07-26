"""Deterministic self-contained HTML reports."""

from __future__ import annotations

import html
import json
from pathlib import Path
from collections.abc import Mapping
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
<style>
:root {{ color-scheme: light dark; font-family: system-ui, sans-serif; }}
body {{ max-width: 1100px; margin: 0 auto; padding: 2rem; line-height: 1.5; }}
h1, h2 {{ line-height: 1.15; }}
.summary {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(14rem, 1fr));
  gap: 1rem;
}}
.card, details {{
  border: 1px solid #8886;
  border-radius: .6rem;
  padding: 1rem;
  margin: 1rem 0;
}}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border-bottom: 1px solid #8885; padding: .35rem .5rem; text-align: left; }}
pre {{ overflow-x: auto; white-space: pre; tab-size: 2; }}
code {{ font-family: ui-monospace, SFMono-Regular, Consolas, monospace; }}
.bad {{ font-weight: 700; }}
</style>
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
<style>
body {{
  max-width: 900px;
  margin: auto;
  padding: 2rem;
  font-family: system-ui, sans-serif;
}}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{
  padding: .4rem;
  border-bottom: 1px solid #9996;
  text-align: left;
}}
pre {{ overflow: auto; }}
</style>
</head><body><h1>Weave Loupe comparison</h1>
<table>
<thead>
<tr><th>LLVM metric</th><th>Before</th><th>After</th><th>Delta</th></tr>
</thead>
<tbody>{rows}</tbody>
</table>
<details><summary>Complete comparison JSON</summary><pre>{raw}</pre></details>
</body></html>
"""


def write_report(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _details(title: str, content: str) -> str:
    return (
        f"<details><summary>{html.escape(title)}</summary>"
        f"<pre><code>{html.escape(content)}</code></pre></details>"
    )
