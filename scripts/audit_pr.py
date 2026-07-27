#!/usr/bin/env python3
"""Audit changed Weave files and produce one PR-comment Markdown summary."""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

COMMENT_MARKER = "<!-- weave-loupe-pr-audit -->"
AUDIT_ENGINE_PATHS = (
    "src/weave_loupe/",
    "scripts/audit_pr.py",
    "scripts/reaudit_stale.py",
    ".github/workflows/weave-audit.yml",
    ".github/workflows/scheduled-reaudit.yml",
    "pyproject.toml",
    "uv.lock",
)


@dataclass(frozen=True)
class FileAudit:
    source: Path
    report: Path
    returncode: int
    stdout: str
    stderr: str

    @property
    def passed(self) -> bool:
        return self.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--weavec", type=Path, required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--reports-list", type=Path, required=True)
    args = parser.parse_args()

    changed = _changed_paths(args.base, args.head)
    sources = _changed_weave_sources(changed)
    if not sources and _audit_engine_changed(changed):
        sources = sorted(Path("docs/audit").rglob("*.weave"))

    audits = [
        _audit_file(source=source, weavec=args.weavec, model=args.model)
        for source in sources
    ]
    passed = bool(audits) and all(audit.passed for audit in audits)
    summary = _render_summary(
        base=args.base,
        head=args.head,
        changed=changed,
        audits=audits,
        passed=passed,
    )
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(summary, encoding="utf-8")
    args.reports_list.parent.mkdir(parents=True, exist_ok=True)
    reports = "".join(f"{audit.report}\n" for audit in audits if audit.passed)
    args.reports_list.write_text(reports, encoding="utf-8")
    return 0 if passed else 1


def _changed_paths(base: str, head: str) -> list[Path]:
    completed = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=ACMR", base, head],
        capture_output=True,
        text=True,
        check=True,
    )
    return [Path(line) for line in completed.stdout.splitlines() if line.strip()]


def _changed_weave_sources(changed: list[Path]) -> list[Path]:
    return sorted(
        path for path in changed if path.suffix == ".weave" and path.is_file()
    )


def _audit_engine_changed(changed: list[Path]) -> bool:
    return any(
        str(path) == prefix or str(path).startswith(prefix)
        for path in changed
        for prefix in AUDIT_ENGINE_PATHS
    )


def _audit_file(*, source: Path, weavec: Path, model: str) -> FileAudit:
    report = source.with_suffix(".md")
    command = [
        sys.executable,
        "-m",
        "weave_loupe.cli",
        "audit",
        str(source),
        "--weavec",
        str(weavec),
        "--model",
        model,
        "--report-out",
        str(report),
        "--verbose",
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    return FileAudit(
        source=source,
        report=report,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def _render_summary(
    *,
    base: str,
    head: str,
    changed: list[Path],
    audits: list[FileAudit],
    passed: bool,
) -> str:
    icon = "✅" if passed else "❌"
    lines = [
        COMMENT_MARKER,
        "## Weave Loupe audit",
        "",
        f"**Overall:** {icon} {'PASSED' if passed else 'FAILED'}",
        f"**Audited commit:** `{head}`",
        f"**Base commit:** `{base}`",
        "",
    ]
    if not audits:
        lines.extend(
            [
                "No auditable `.weave` files were found. The gate is failed "
                "rather than silently passing without evidence.",
                "",
                "Changed paths:",
                "",
                *[f"- `{path}`" for path in changed],
                "",
            ]
        )
        return "\n".join(lines)

    for audit in audits:
        result = "PASSED" if audit.passed else f"FAILED (exit {audit.returncode})"
        lines.extend(
            [
                f"<details {'open' if not audit.passed else ''}>",
                f"<summary><code>{audit.source}</code> — {result}</summary>",
                "",
                audit.stdout.strip() or "_No audit report was produced._",
            ]
        )
        if audit.stderr.strip():
            lines.extend(
                [
                    "",
                    "### Tool diagnostics",
                    "",
                    "```text",
                    audit.stderr.strip(),
                    "```",
                ]
            )
        lines.extend(["", "</details>", ""])
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
