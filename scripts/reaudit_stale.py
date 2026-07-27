#!/usr/bin/env python3
"""Refresh stale audit reports and detect regressions in development compilers."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

from weave_loupe.compiler_version import CompilerVersion, identify_weavec

_TIMESTAMP_PREFIX = "- **Audit timestamp (UTC):** `"
_VERSION_PREFIX = "- **weavec version:** `"


@dataclass(frozen=True)
class ReportState:
    source: Path
    report: Path
    timestamp: datetime | None
    version: str | None
    reason: str | None


@dataclass(frozen=True)
class AuditRun:
    source: str
    report: str
    reason: str
    returncode: int
    stdout_log: str
    stderr_log: str

    @property
    def passed(self) -> bool:
        return self.returncode == 0

    @property
    def compiler_finding(self) -> bool:
        return self.returncode == 2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--weavec", type=Path, required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--source-root", type=Path, default=Path("docs/audit"))
    parser.add_argument("--max-age-days", type=int, default=30)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--reports-list", type=Path, required=True)
    parser.add_argument("--failures-json", type=Path, required=True)
    parser.add_argument("--logs-dir", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--now", help=argparse.SUPPRESS)
    args = parser.parse_args()

    now = _parse_time(args.now) if args.now else datetime.now(UTC)
    identity = identify_weavec(args.weavec)
    states = _report_states(
        source_root=args.source_root,
        identity=identity,
        now=now,
        max_age=timedelta(days=args.max_age_days),
        force=args.force,
    )
    due = [state for state in states if state.reason is not None]

    args.logs_dir.mkdir(parents=True, exist_ok=True)
    runs = [
        _audit(
            state=state,
            weavec=args.weavec,
            model=args.model,
            logs_dir=args.logs_dir,
        )
        for state in due
    ]

    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(
        _render_summary(identity=identity, states=states, runs=runs, now=now),
        encoding="utf-8",
    )
    args.reports_list.parent.mkdir(parents=True, exist_ok=True)
    args.reports_list.write_text(
        "".join(f"{run.report}\n" for run in runs if run.passed),
        encoding="utf-8",
    )
    failures = {
        "format": "weave-loupe-scheduled-failures-v1",
        "timestamp_utc": now.replace(microsecond=0).isoformat(),
        "compiler": asdict(identity),
        "compiler_findings": [asdict(run) for run in runs if run.compiler_finding],
        "infrastructure_failures": [
            asdict(run) for run in runs if not run.passed and not run.compiler_finding
        ],
    }
    args.failures_json.parent.mkdir(parents=True, exist_ok=True)
    args.failures_json.write_text(
        json.dumps(failures, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    if any(not run.passed and not run.compiler_finding for run in runs):
        return 1
    if any(run.compiler_finding for run in runs):
        return 2
    return 0


def _report_states(
    *,
    source_root: Path,
    identity: CompilerVersion,
    now: datetime,
    max_age: timedelta,
    force: bool,
) -> list[ReportState]:
    states: list[ReportState] = []
    for source in sorted(source_root.rglob("*.weave")):
        report = source.with_suffix(".md")
        timestamp, version = _read_report_identity(report)
        reason: str | None = None
        if force:
            reason = "manual force"
        elif timestamp is None:
            reason = "missing or unparseable report timestamp"
        elif now - timestamp >= max_age:
            reason = f"report age is at least {max_age.days} days"
        elif identity.development and version != identity.display:
            reason = (
                "development compiler changed from "
                f"{version or 'unknown'} to {identity.display}"
            )
        states.append(
            ReportState(
                source=source,
                report=report,
                timestamp=timestamp,
                version=version,
                reason=reason,
            )
        )
    return states


def _read_report_identity(report: Path) -> tuple[datetime | None, str | None]:
    try:
        lines = report.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None, None
    timestamp: datetime | None = None
    version: str | None = None
    for line in lines:
        if line.startswith(_TIMESTAMP_PREFIX) and line.endswith("`"):
            try:
                timestamp = _parse_time(line[len(_TIMESTAMP_PREFIX) : -1])
            except ValueError:
                timestamp = None
        elif line.startswith(_VERSION_PREFIX) and line.endswith("`"):
            version = line[len(_VERSION_PREFIX) : -1]
        if timestamp is not None and version is not None:
            break
    return timestamp, version


def _parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _audit(
    *, state: ReportState, weavec: Path, model: str, logs_dir: Path
) -> AuditRun:
    safe_name = "__".join(state.source.parts).replace(".weave", "")
    stdout_log = logs_dir / f"{safe_name}.stdout.md"
    stderr_log = logs_dir / f"{safe_name}.stderr.txt"
    with tempfile.TemporaryDirectory(prefix="loupe-reaudit-") as temp_dir:
        candidate = Path(temp_dir) / state.report.name
        command = [
            sys.executable,
            "-m",
            "weave_loupe.cli",
            "audit",
            str(state.source),
            "--weavec",
            str(weavec),
            "--model",
            model,
            "--report-out",
            str(candidate),
            "--verbose",
        ]
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
        stdout_log.write_text(completed.stdout, encoding="utf-8")
        stderr_log.write_text(completed.stderr, encoding="utf-8")
        if completed.returncode == 0:
            state.report.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(candidate, state.report)
    return AuditRun(
        source=str(state.source),
        report=str(state.report),
        reason=state.reason or "not due",
        returncode=completed.returncode,
        stdout_log=str(stdout_log),
        stderr_log=str(stderr_log),
    )


def _render_summary(
    *,
    identity: CompilerVersion,
    states: list[ReportState],
    runs: list[AuditRun],
    now: datetime,
) -> str:
    due_count = len(runs)
    passed = sum(run.passed for run in runs)
    findings = sum(run.compiler_finding for run in runs)
    infrastructure = due_count - passed - findings
    build_kind = "development" if identity.development else "release"
    lines = [
        "# Scheduled Weave audit refresh",
        "",
        f"- **Checked at:** `{now.replace(microsecond=0).isoformat()}`",
        f"- **Compiler:** `{identity.display}`",
        f"- **Compiler build kind:** `{build_kind}`",
        f"- **Reports discovered:** `{len(states)}`",
        f"- **Reports due:** `{due_count}`",
        f"- **Passed:** `{passed}`",
        f"- **Compiler findings:** `{findings}`",
        f"- **Infrastructure failures:** `{infrastructure}`",
        "",
    ]
    if not runs:
        lines.extend(["No reports required re-auditing.", ""])
        return "\n".join(lines)
    lines.extend(["## Results", ""])
    for run in runs:
        if run.passed:
            result = "PASSED"
        elif run.compiler_finding:
            result = "FAILED: compiler finding"
        else:
            result = "FAILED: infrastructure"
        lines.append(f"- `{run.source}` — **{result}** — {run.reason}")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
