#!/usr/bin/env python3
"""Audit changed Weave files and produce one PR-comment Markdown summary."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

COMMENT_MARKER = "<!-- weave-loupe-pr-audit -->"
_RUNTIME_SIDECAR_SUFFIX = ".audit.json"
_REPORT_SUFFIX = ".md"
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
    candidate: Path
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
    parser.add_argument("--max-tokens", type=int, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--reports-list", type=Path, required=True)
    args = parser.parse_args()

    changed = _changed_paths(args.base, args.head)
    sources = _changed_weave_sources(changed)
    if not sources and _audit_engine_changed(changed):
        sources = sorted(Path("docs/audit").rglob("*.weave"))

    with tempfile.TemporaryDirectory(prefix="loupe-pr-audit-") as temp_dir:
        candidate_root = Path(temp_dir)
        audits = [
            _audit_file(
                source=source,
                candidate_root=candidate_root,
                weavec=args.weavec,
                model=args.model,
                max_tokens=args.max_tokens,
            )
            for source in sources
        ]
        passed = bool(audits) and all(audit.passed for audit in audits)
        if passed:
            for audit in audits:
                audit.report.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(audit.candidate, audit.report)

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
        ["git", "diff", "--name-only", "--diff-filter=ACMRD", base, head],
        capture_output=True,
        text=True,
        check=True,
    )
    return [Path(line) for line in completed.stdout.splitlines() if line.strip()]


def _changed_weave_sources(changed: list[Path]) -> list[Path]:
    sources = {path for path in changed if path.suffix == ".weave" and path.is_file()}
    for path in changed:
        name = str(path)
        source: Path | None = None
        if name.endswith(_RUNTIME_SIDECAR_SUFFIX):
            source = Path(name[: -len(_RUNTIME_SIDECAR_SUFFIX)] + ".weave")
        elif name.endswith(_REPORT_SUFFIX):
            source = path.with_suffix(".weave")
        if source is not None and source.is_file():
            sources.add(source)
    return sorted(sources)


def _audit_engine_changed(changed: list[Path]) -> bool:
    return any(
        str(path) == prefix or str(path).startswith(prefix)
        for path in changed
        for prefix in AUDIT_ENGINE_PATHS
    )


def _audit_file(
    *,
    source: Path,
    candidate_root: Path,
    weavec: Path,
    model: str,
    max_tokens: int,
) -> FileAudit:
    report = source.with_suffix(".md")
    candidate = candidate_root / report.name
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
        "--max-tokens",
        str(max_tokens),
        "--report-out",
        str(candidate),
        "--verbose",
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    return FileAudit(
        source=source,
        report=report,
        candidate=candidate,
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
