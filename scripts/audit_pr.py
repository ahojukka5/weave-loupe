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

from weave_loupe.expected_failure_audit import (
    EXPECTED_FAILURE_SUFFIX,
    ExpectedFailureError,
    load_expected_failure_contract,
)

COMMENT_MARKER = "<!-- weave-loupe-pr-audit -->"
_RUNTIME_SIDECAR_SUFFIX = ".audit.json"
_SOURCE_SET_SUFFIX = ".audit.sources"
_REPORT_SUFFIX = ".md"
AUDIT_ENGINE_PATHS = (
    "src/weave_loupe/",
    "scripts/audit_pr.py",
    "scripts/reaudit_stale.py",
    "scripts/check_workflow_security.py",
    ".github/workflows/weave-audit.yml",
    ".github/workflows/publish-audit.yml",
    ".github/workflows/scheduled-reaudit.yml",
    "pyproject.toml",
    "uv.lock",
)


@dataclass(frozen=True)
class AuditTarget:
    sources: tuple[Path, ...]
    report: Path
    expected_failure: Path | None = None

    @property
    def primary(self) -> Path:
        return self.sources[0]


@dataclass(frozen=True)
class FileAudit:
    sources: tuple[Path, ...]
    report: Path
    candidate: Path
    returncode: int
    stdout: str
    stderr: str

    @property
    def source(self) -> Path:
        return self.sources[0]

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
    try:
        targets = _changed_audit_targets(changed)
        if not targets and _audit_engine_changed(changed):
            targets = sorted(
                [
                    *_all_audit_targets(Path("docs/audit")),
                    *_all_audit_targets(Path("docs/negative-audit")),
                ],
                key=lambda item: str(item.report),
            )
    except (OSError, ValueError, ExpectedFailureError) as exc:
        print(f"loupe PR audit source selection failed: {exc}", file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory(prefix="loupe-pr-audit-") as temp_dir:
        candidate_root = Path(temp_dir)
        audits = [
            _audit_file(
                target=target,
                candidate_root=candidate_root,
                weavec=args.weavec,
                model=args.model,
                max_tokens=args.max_tokens,
            )
            for target in targets
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


def _changed_audit_targets(changed: list[Path]) -> list[AuditTarget]:
    declared = _declared_audit_targets(Path("."))
    by_source: dict[Path, AuditTarget] = {}
    by_manifest: dict[Path, AuditTarget] = {}
    by_report: dict[Path, AuditTarget] = {}
    for manifest, target in declared:
        for source in target.sources:
            key = _path_key(source)
            existing = by_source.get(key)
            if existing is not None and existing != target:
                raise ValueError(f"source belongs to multiple audit sets: {source}")
            by_source[key] = target
        by_manifest[_path_key(manifest)] = target
        by_report[_path_key(target.report)] = target

    selected: dict[Path, AuditTarget] = {}
    for path in changed:
        key = _path_key(path)
        target = by_source.get(key) or by_manifest.get(key) or by_report.get(key)
        name = str(path)
        if target is None and path.suffix == ".weave" and path.is_file():
            target = _single_source_target(path)
        elif target is None and name.endswith(_SOURCE_SET_SUFFIX):
            primary = _primary_for_source_set(path)
            if primary.is_file():
                target = _single_source_target(primary)
        elif target is None and name.endswith(_RUNTIME_SIDECAR_SUFFIX):
            primary = Path(name[: -len(_RUNTIME_SIDECAR_SUFFIX)] + ".weave")
            target = by_source.get(_path_key(primary))
            if target is None and primary.is_file():
                target = _single_source_target(primary)
        elif target is None and name.endswith(_REPORT_SUFFIX):
            primary = path.with_suffix(".weave")
            if primary.is_file():
                target = _single_source_target(primary)
        if target is not None:
            selected[_path_key(target.report)] = target
    return sorted(selected.values(), key=lambda item: str(item.report))


def _changed_weave_sources(changed: list[Path]) -> list[Path]:
    """Compatibility wrapper returning each selected target's primary source."""
    return [target.primary for target in _changed_audit_targets(changed)]


def _all_audit_targets(root: Path) -> list[AuditTarget]:
    declared = _declared_audit_targets(root)
    grouped = {_path_key(source) for _, target in declared for source in target.sources}
    targets = [target for _, target in declared]
    targets.extend(
        _single_source_target(source)
        for source in sorted(root.rglob("*.weave"))
        if _path_key(source) not in grouped
    )
    return sorted(targets, key=lambda item: str(item.report))


def _declared_audit_targets(root: Path) -> list[tuple[Path, AuditTarget]]:
    declared = [
        (manifest, _read_source_set(manifest))
        for manifest in sorted(root.rglob(f"*{_SOURCE_SET_SUFFIX}"))
    ]
    declared.extend(
        (contract_path, _read_expected_failure_target(contract_path))
        for contract_path in sorted(root.rglob(f"*{EXPECTED_FAILURE_SUFFIX}"))
    )
    return sorted(declared, key=lambda item: str(item[0]))


def _read_expected_failure_target(path: Path) -> AuditTarget:
    contract = load_expected_failure_contract(path)
    return AuditTarget(
        sources=contract.sources,
        report=contract.report,
        expected_failure=path,
    )


def _read_source_set(manifest: Path) -> AuditTarget:
    primary = _primary_for_source_set(manifest)
    entries = [
        line.strip()
        for line in manifest.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not entries:
        raise ValueError(f"source-set manifest is empty: {manifest}")

    root = manifest.parent.resolve()
    sources: list[Path] = []
    seen: set[Path] = set()
    for entry in entries:
        raw = Path(entry)
        if raw.is_absolute():
            raise ValueError(f"source-set path must be relative: {entry}")
        candidate = manifest.parent / raw
        resolved = candidate.resolve()
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"source-set path escapes its directory: {entry}") from exc
        if resolved in seen:
            raise ValueError(f"source-set path is duplicated: {entry}")
        if candidate.suffix != ".weave":
            raise ValueError(f"source-set path must name a .weave file: {entry}")
        if not candidate.is_file():
            raise ValueError(f"source-set source does not exist: {candidate}")
        seen.add(resolved)
        sources.append(candidate)

    if _path_key(sources[0]) != _path_key(primary):
        raise ValueError(
            f"source-set primary must be first: expected {primary}, got {sources[0]}"
        )
    return AuditTarget(sources=tuple(sources), report=primary.with_suffix(".md"))


def _primary_for_source_set(manifest: Path) -> Path:
    name = str(manifest)
    if not name.endswith(_SOURCE_SET_SUFFIX):
        raise ValueError(f"not an audit source-set manifest: {manifest}")
    return Path(name[: -len(_SOURCE_SET_SUFFIX)] + ".weave")


def _single_source_target(source: Path) -> AuditTarget:
    return AuditTarget(sources=(source,), report=source.with_suffix(".md"))


def _path_key(path: Path) -> Path:
    try:
        return path.resolve()
    except OSError:
        return path.absolute()


def _audit_engine_changed(changed: list[Path]) -> bool:
    return any(
        str(path) == prefix or str(path).startswith(prefix)
        for path in changed
        for prefix in AUDIT_ENGINE_PATHS
    )


def _audit_file(
    *,
    target: AuditTarget,
    candidate_root: Path,
    weavec: Path,
    model: str,
    max_tokens: int,
) -> FileAudit:
    report = target.report
    candidate = candidate_root / report
    candidate.parent.mkdir(parents=True, exist_ok=True)
    if target.expected_failure is not None:
        command = [
            sys.executable,
            "-m",
            "weave_loupe.expected_failure_audit",
            str(target.expected_failure),
            "--weavec",
            str(weavec),
            "--model",
            model,
            "--max-tokens",
            str(max_tokens),
            "--report-out",
            str(candidate),
        ]
    else:
        command = [
            sys.executable,
            "-m",
            "weave_loupe.cli",
            "audit",
            *(str(source) for source in target.sources),
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
        sources=target.sources,
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
                "No auditable Weave inputs were found. The gate is failed rather "
                "than silently passing without evidence.",
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
        source_label = ", ".join(str(source) for source in audit.sources)
        lines.extend(
            [
                f"<details {'open' if not audit.passed else ''}>",
                f"<summary><code>{source_label}</code> — {result}</summary>",
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
