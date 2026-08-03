"""Scheduled refresh orchestration for positive and negative audit reports."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

from weave_loupe.audit_policy import DEFAULT_AUDIT_MAX_AGE_DAYS
from weave_loupe.auditor_identity import (
    AuditorIdentity,
    identify_auditor,
    sha256_file,
)
from weave_loupe.compiler_version import CompilerVersion, identify_weavec
from weave_loupe.expected_failure_audit import (
    EXPECTED_FAILURE_SUFFIX,
    ExpectedFailureError,
    expected_failure_report_reasons,
    load_expected_failure_contract,
)
from weave_loupe.llm import normalize_endpoint_identity
from weave_loupe.report_validity import (
    ReportIdentity,
    evaluate_identity,
    evaluate_report,
    parse_time,
    read_report_identity,
)

_read_report_identity = read_report_identity
_parse_time = parse_time


@dataclass(frozen=True)
class ReportState:
    """Freshness state for one workflow-owned audit report."""

    source: Path
    report: Path
    timestamp: datetime | None
    version: str | None
    version_source: str | None
    compiler_binary_sha256: str | None
    auditor_sha256: str | None
    model: str | None
    endpoint: str | None
    max_tokens: int | None
    source_sha256: str | None
    runtime_sha256: str | None
    reason: str | None
    sources: tuple[Path, ...] = ()
    expected_failure: Path | None = None

    def __post_init__(self) -> None:
        if not self.sources:
            object.__setattr__(self, "sources", (self.source,))

    @property
    def kind(self) -> str:
        return "expected failure" if self.expected_failure is not None else "positive"


@dataclass(frozen=True)
class AuditRun:
    """One scheduled compiler invocation and its classification."""

    source: str
    report: str
    reason: str
    returncode: int
    stdout_log: str
    stderr_log: str
    kind: str = "positive"
    duration_seconds: float = 0.0

    @property
    def passed(self) -> bool:
        return self.returncode == 0

    @property
    def compiler_finding(self) -> bool:
        return self.returncode == 2

    @property
    def failure_class(self) -> str:
        if self.passed:
            return "passed"
        if self.compiler_finding:
            return "compiler finding"
        return "infrastructure"


@dataclass(frozen=True)
class AuditOutcome:
    run: AuditRun
    candidate: Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--weavec", type=Path, required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--llm-endpoint", required=True)
    parser.add_argument("--max-tokens", type=int, required=True)
    parser.add_argument("--source-root", type=Path, default=Path("docs/audit"))
    parser.add_argument(
        "--negative-root",
        type=Path,
        default=Path("docs/negative-audit"),
    )
    parser.add_argument(
        "--max-age-days",
        type=int,
        default=DEFAULT_AUDIT_MAX_AGE_DAYS,
    )
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--reports-list", type=Path, required=True)
    parser.add_argument("--failures-json", type=Path, required=True)
    parser.add_argument("--logs-dir", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--now", help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.max_tokens <= 0:
        parser.error("--max-tokens must be positive")
    now = parse_time(args.now) if args.now else datetime.now(UTC)
    endpoint = normalize_endpoint_identity(args.llm_endpoint)
    identity = identify_weavec(args.weavec)
    compiler_binary_sha256 = sha256_file(args.weavec)
    auditor = identify_auditor()

    try:
        states = _scheduled_report_states(
            source_root=args.source_root,
            negative_root=args.negative_root,
            identity=identity,
            compiler_binary_sha256=compiler_binary_sha256,
            auditor=auditor,
            model=args.model,
            endpoint=endpoint,
            max_tokens=args.max_tokens,
            now=now,
            max_age=timedelta(days=args.max_age_days),
            force=args.force,
        )
    except (OSError, ValueError, ExpectedFailureError) as exc:
        _write_discovery_failure(
            summary=args.summary,
            reports_list=args.reports_list,
            failures_json=args.failures_json,
            identity=identity,
            compiler_binary_sha256=compiler_binary_sha256,
            auditor=auditor,
            model=args.model,
            endpoint=endpoint,
            max_tokens=args.max_tokens,
            now=now,
            message=str(exc),
        )
        print(f"loupe scheduled audit discovery failed: {exc}", file=sys.stderr)
        return 1

    due = [state for state in states if state.reason is not None]
    args.logs_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="loupe-reaudit-") as temp_dir:
        candidate_root = Path(temp_dir)
        outcomes = [
            _audit(
                state=state,
                candidate_root=candidate_root,
                weavec=args.weavec,
                model=args.model,
                max_tokens=args.max_tokens,
                logs_dir=args.logs_dir,
                endpoint=endpoint,
            )
            for state in due
        ]
        runs = [outcome.run for outcome in outcomes]
        all_passed = all(run.passed for run in runs)
        if all_passed:
            for outcome in outcomes:
                report = Path(outcome.run.report)
                report.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(outcome.candidate, report)

        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(
            _render_summary(
                identity=identity,
                compiler_binary_sha256=compiler_binary_sha256,
                auditor=auditor,
                model=args.model,
                endpoint=endpoint,
                max_tokens=args.max_tokens,
                states=states,
                runs=runs,
                now=now,
            ),
            encoding="utf-8",
        )
        args.reports_list.parent.mkdir(parents=True, exist_ok=True)
        published_runs = runs if all_passed else []
        args.reports_list.write_text(
            "".join(f"{run.report}\n" for run in published_runs),
            encoding="utf-8",
        )
        failures = {
            "format": "weave-loupe-scheduled-failures-v1",
            "timestamp_utc": now.replace(microsecond=0).isoformat(),
            "model": args.model,
            "endpoint": endpoint,
            "max_tokens": args.max_tokens,
            "compiler": {
                **asdict(identity),
                "binary_sha256": compiler_binary_sha256,
            },
            "auditor": auditor.metadata(),
            "compiler_findings": [
                _run_document(run) for run in runs if run.compiler_finding
            ],
            "infrastructure_failures": [
                _run_document(run)
                for run in runs
                if not run.passed and not run.compiler_finding
            ],
        }
        args.failures_json.parent.mkdir(parents=True, exist_ok=True)
        args.failures_json.write_text(
            json.dumps(failures, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    if any(not run.passed and not run.compiler_finding for run in runs):
        return 1
    if any(run.compiler_finding for run in runs):
        return 2
    return 0


def _scheduled_report_states(
    *,
    source_root: Path,
    negative_root: Path,
    identity: CompilerVersion,
    now: datetime,
    max_age: timedelta,
    force: bool,
    compiler_binary_sha256: str,
    auditor: AuditorIdentity,
    model: str,
    endpoint: str,
    max_tokens: int,
) -> list[ReportState]:
    positive = _report_states(
        source_root=source_root,
        identity=identity,
        compiler_binary_sha256=compiler_binary_sha256,
        auditor=auditor,
        model=model,
        endpoint=endpoint,
        max_tokens=max_tokens,
        now=now,
        max_age=max_age,
        force=force,
    )
    negative = _expected_failure_states(
        negative_root=negative_root,
        identity=identity,
        compiler_binary_sha256=compiler_binary_sha256,
        auditor=auditor,
        model=model,
        endpoint=endpoint,
        max_tokens=max_tokens,
        now=now,
        max_age=max_age,
        force=force,
    )
    return sorted([*positive, *negative], key=lambda state: str(state.report))


def _report_states(
    *,
    source_root: Path,
    identity: CompilerVersion,
    now: datetime,
    max_age: timedelta,
    force: bool,
    compiler_binary_sha256: str | None = None,
    auditor: AuditorIdentity | None = None,
    model: str | None = None,
    endpoint: str | None = None,
    max_tokens: int | None = None,
) -> list[ReportState]:
    """Discover positive reports while preserving legacy helper behavior."""

    source_files = tuple(sorted(source_root.rglob("*.weave")))
    states: list[ReportState] = []
    covered_sources: set[Path] = set()
    handled_reports: set[Path] = set()

    for report in sorted(source_root.rglob("*.md")):
        report_identity = read_report_identity(report)
        adjacent = report.with_suffix(".weave")
        if not report_identity.sources and not adjacent.is_file():
            continue
        state = _state_for_report(
            report=report,
            fallback_source=adjacent,
            source_files=source_files,
            report_identity=report_identity,
            identity=identity,
            compiler_binary_sha256=compiler_binary_sha256,
            auditor=auditor,
            model=model,
            endpoint=endpoint,
            max_tokens=max_tokens,
            now=now,
            max_age=max_age,
            force=force,
        )
        states.append(state)
        handled_reports.add(_path_key(report))
        covered_sources.update(_path_key(source) for source in state.sources)

    for source in source_files:
        if _path_key(source) in covered_sources:
            continue
        report = source.with_suffix(".md")
        if _path_key(report) in handled_reports:
            continue
        report_identity = read_report_identity(report)
        state = _state_for_report(
            report=report,
            fallback_source=source,
            source_files=source_files,
            report_identity=report_identity,
            identity=identity,
            compiler_binary_sha256=compiler_binary_sha256,
            auditor=auditor,
            model=model,
            endpoint=endpoint,
            max_tokens=max_tokens,
            now=now,
            max_age=max_age,
            force=force,
        )
        states.append(state)

    return sorted(states, key=lambda state: str(state.report))


def _expected_failure_states(
    *,
    negative_root: Path,
    identity: CompilerVersion,
    compiler_binary_sha256: str,
    auditor: AuditorIdentity,
    model: str,
    endpoint: str,
    max_tokens: int,
    now: datetime,
    max_age: timedelta,
    force: bool,
) -> list[ReportState]:
    states: list[ReportState] = []
    contracts = sorted(negative_root.rglob(f"*{EXPECTED_FAILURE_SUFFIX}"))
    for path in contracts:
        contract = load_expected_failure_contract(path)
        report = contract.report
        report_identity = read_report_identity(report)
        reason: str | None
        if force:
            reason = "manual force"
        elif not report.is_file():
            reason = "missing audit report"
        else:
            result = evaluate_report(
                report=report,
                source=None,
                sources=contract.sources,
                compiler_identity=identity,
                compiler_binary_sha256=compiler_binary_sha256,
                auditor=auditor,
                current_model=model,
                current_endpoint=endpoint,
                current_max_tokens=max_tokens,
                now=now,
                max_age=max_age,
                force=False,
            )
            reasons = [*result.reasons, *expected_failure_report_reasons(report)]
            reason = reasons[0] if reasons else None

        states.append(
            ReportState(
                source=contract.sources[0],
                sources=contract.sources,
                report=report,
                timestamp=report_identity.timestamp,
                version=report_identity.version,
                version_source=report_identity.version_source,
                compiler_binary_sha256=report_identity.compiler_binary_sha256,
                auditor_sha256=report_identity.auditor_sha256,
                model=report_identity.model,
                endpoint=report_identity.endpoint,
                max_tokens=report_identity.max_tokens,
                source_sha256=report_identity.source_sha256,
                runtime_sha256=report_identity.runtime_sha256,
                reason=reason,
                expected_failure=path,
            )
        )
    return states


def _state_for_report(
    *,
    report: Path,
    fallback_source: Path,
    source_files: tuple[Path, ...],
    report_identity: ReportIdentity,
    identity: CompilerVersion,
    compiler_binary_sha256: str | None,
    auditor: AuditorIdentity | None,
    model: str | None,
    endpoint: str | None,
    max_tokens: int | None,
    now: datetime,
    max_age: timedelta,
    force: bool,
) -> ReportState:
    if compiler_binary_sha256 is not None and auditor is not None:
        result = evaluate_report(
            report=report,
            source=None if report.is_file() else fallback_source,
            sources=None,
            compiler_identity=identity,
            compiler_binary_sha256=compiler_binary_sha256,
            auditor=auditor,
            current_model=model,
            current_endpoint=endpoint,
            current_max_tokens=max_tokens,
            now=now,
            max_age=max_age,
            force=force,
        )
        current_sources = result.sources
        reason = result.primary_reason
    else:
        current_sources = _compatibility_sources(
            report=report,
            fallback_source=fallback_source,
            source_files=source_files,
            report_identity=report_identity,
        )
        reason = _reaudit_reason(
            source=current_sources[0],
            report_identity=report_identity,
            identity=identity,
            current_model=model,
            current_endpoint=endpoint,
            current_max_tokens=max_tokens,
            now=now,
            max_age=max_age,
            force=force,
        )

    primary = current_sources[0]
    return ReportState(
        source=primary,
        sources=current_sources,
        report=report,
        timestamp=report_identity.timestamp,
        version=report_identity.version,
        version_source=report_identity.version_source,
        compiler_binary_sha256=report_identity.compiler_binary_sha256,
        auditor_sha256=report_identity.auditor_sha256,
        model=report_identity.model,
        endpoint=report_identity.endpoint,
        max_tokens=report_identity.max_tokens,
        source_sha256=report_identity.source_sha256,
        runtime_sha256=report_identity.runtime_sha256,
        reason=reason,
    )


def _compatibility_sources(
    *,
    report: Path,
    fallback_source: Path,
    source_files: tuple[Path, ...],
    report_identity: ReportIdentity,
) -> tuple[Path, ...]:
    if not report_identity.sources:
        return (fallback_source,)

    resolved: list[Path] = []
    for item in report_identity.sources:
        recorded = Path(item.path)
        candidates = [recorded]
        if not recorded.is_absolute():
            candidates.extend((report.parent / recorded, Path.cwd() / recorded))
        current = next(
            (candidate for candidate in candidates if candidate.is_file()),
            None,
        )
        if current is None:
            matches = [
                source
                for source in source_files
                if source.name == recorded.name and sha256_file(source) == item.sha256
            ]
            current = matches[0] if len(matches) == 1 else recorded
        resolved.append(current)
    return tuple(resolved)


def _path_key(path: Path) -> Path:
    try:
        return path.resolve()
    except OSError:
        return path.absolute()


def _safe_log_stem(path: Path) -> str:
    parts = [
        part.replace(":", "_")
        for part in path.parts
        if part not in {path.anchor, "/", "\\"}
    ]
    stem = "__".join(parts)
    for suffix in (EXPECTED_FAILURE_SUFFIX, ".weave", ".md"):
        stem = stem.replace(suffix, "")
    return stem or "audit"


def _reaudit_reason(
    *,
    source: Path,
    report_identity: ReportIdentity,
    identity: CompilerVersion,
    now: datetime,
    max_age: timedelta,
    force: bool,
    compiler_binary_sha256: str | None = None,
    auditor: AuditorIdentity | None = None,
    current_model: str | None = None,
    current_endpoint: str | None = None,
    current_max_tokens: int | None = None,
) -> str | None:
    """Compatibility wrapper for focused tests; production uses evaluate_report."""

    if compiler_binary_sha256 is not None and auditor is not None:
        result = evaluate_identity(
            report=source.with_suffix(".md"),
            source=source,
            identity=report_identity,
            compiler_identity=identity,
            compiler_binary_sha256=compiler_binary_sha256,
            auditor=auditor,
            current_model=current_model,
            current_endpoint=current_endpoint,
            current_max_tokens=current_max_tokens,
            now=now,
            max_age=max_age,
            force=force,
        )
        return result.primary_reason
    if force:
        return "manual force"
    if report_identity.timestamp is None:
        return "missing or unparseable report timestamp"
    if report_identity.source_sha256 is None:
        return "report does not record audited source hash"
    if sha256_file(source) != report_identity.source_sha256:
        return "source content changed since audit"
    runtime = source.with_suffix(".audit.json")
    if runtime.is_file():
        if report_identity.runtime_sha256 is None:
            return "runtime matrix was added or not recorded"
        if sha256_file(runtime) != report_identity.runtime_sha256:
            return "runtime matrix content changed since audit"
    elif report_identity.runtime_sha256 is not None:
        return "runtime matrix was removed since audit"
    if current_model is not None:
        if report_identity.model is None:
            return "report does not record LLM model"
        if report_identity.model != current_model:
            return f"LLM model changed from {report_identity.model} to {current_model}"
    if current_endpoint is not None:
        if report_identity.endpoint is None:
            return "report does not record LLM endpoint"
        if report_identity.endpoint != current_endpoint:
            return (
                f"LLM endpoint changed from {report_identity.endpoint} "
                f"to {current_endpoint}"
            )
    if current_max_tokens is not None:
        if report_identity.max_tokens is None:
            return "report does not record LLM max tokens"
        if report_identity.max_tokens != current_max_tokens:
            return (
                f"LLM max tokens changed from {report_identity.max_tokens} "
                f"to {current_max_tokens}"
            )
    if now - report_identity.timestamp >= max_age:
        return f"report age is at least {max_age.days} days"
    if identity.development and report_identity.version != identity.display:
        return (
            "development compiler changed from "
            f"{report_identity.version or 'unknown'} to {identity.display}"
        )
    if identity.source == "command" and report_identity.version_source != "command":
        return (
            "compiler identity source changed from "
            f"{report_identity.version_source or 'unknown'} to command"
        )
    return None


def _audit(
    *,
    state: ReportState,
    candidate_root: Path,
    weavec: Path,
    model: str,
    max_tokens: int,
    logs_dir: Path,
    endpoint: str | None = None,
) -> AuditOutcome:
    safe_name = _safe_log_stem(state.report)
    stdout_log = logs_dir / f"{safe_name}.stdout.md"
    stderr_log = logs_dir / f"{safe_name}.stderr.txt"
    candidate = candidate_root / f"{safe_name}.md"

    if state.expected_failure is not None:
        command = [
            sys.executable,
            "-m",
            "weave_loupe.expected_failure_audit",
            str(state.expected_failure),
            "--weavec",
            str(weavec),
            "--model",
            model,
            "--max-tokens",
            str(max_tokens),
            "--report-out",
            str(candidate),
        ]
        if endpoint is not None:
            command.extend(["--llm-endpoint", endpoint])
    else:
        command = [
            sys.executable,
            "-m",
            "weave_loupe.cli",
            "audit",
            *(str(source) for source in state.sources),
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

    started = time.monotonic()
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    duration = time.monotonic() - started
    stdout_log.write_text(completed.stdout, encoding="utf-8")
    stderr_log.write_text(completed.stderr, encoding="utf-8")
    run = AuditRun(
        source=str(state.source),
        report=str(state.report),
        reason=state.reason or "not due",
        returncode=completed.returncode,
        stdout_log=str(stdout_log),
        stderr_log=str(stderr_log),
        kind=state.kind,
        duration_seconds=round(duration, 3),
    )
    return AuditOutcome(run=run, candidate=candidate)


def _render_summary(
    *,
    identity: CompilerVersion,
    compiler_binary_sha256: str,
    auditor: AuditorIdentity,
    model: str,
    endpoint: str,
    max_tokens: int,
    states: list[ReportState],
    runs: list[AuditRun],
    now: datetime,
) -> str:
    due_count = len(runs)
    passed = sum(run.passed for run in runs)
    findings = sum(run.compiler_finding for run in runs)
    infrastructure = due_count - passed - findings
    positive_count = sum(state.expected_failure is None for state in states)
    negative_count = len(states) - positive_count
    build_kind = "development" if identity.development else "release"
    lines = [
        "# Scheduled Weave audit refresh",
        "",
        f"- **Checked at:** `{now.replace(microsecond=0).isoformat()}`",
        f"- **Compiler:** `{identity.display}`",
        f"- **Compiler binary SHA-256:** `{compiler_binary_sha256}`",
        f"- **Compiler build kind:** `{build_kind}`",
        f"- **Compiler identity source:** `{identity.source}`",
        f"- **Auditor content SHA-256:** `{auditor.sha256}`",
        f"- **LLM endpoint:** `{endpoint}`",
        f"- **LLM model:** `{model}`",
        f"- **LLM max tokens:** `{max_tokens}`",
        f"- **Positive reports discovered:** `{positive_count}`",
        f"- **Negative reports discovered:** `{negative_count}`",
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
        lines.append(
            f"- `{run.source}` — **{result}** — {run.kind} — "
            f"{run.duration_seconds:.3f} s — {run.reason}"
        )
    lines.append("")
    return "\n".join(lines)


def _run_document(run: AuditRun) -> dict[str, object]:
    return {
        "source": run.source,
        "report": run.report,
        "reason": run.reason,
        "returncode": run.returncode,
        "stdout_log": run.stdout_log,
        "stderr_log": run.stderr_log,
        "kind": run.kind,
        "duration_seconds": run.duration_seconds,
        "failure_class": run.failure_class,
    }


def _write_discovery_failure(
    *,
    summary: Path,
    reports_list: Path,
    failures_json: Path,
    identity: CompilerVersion,
    compiler_binary_sha256: str,
    auditor: AuditorIdentity,
    model: str,
    endpoint: str,
    max_tokens: int,
    now: datetime,
    message: str,
) -> None:
    summary.parent.mkdir(parents=True, exist_ok=True)
    summary.write_text(
        "# Scheduled Weave audit refresh\n\n"
        "- **Infrastructure failures:** `1`\n\n"
        f"Corpus discovery failed: {message}\n",
        encoding="utf-8",
    )
    reports_list.parent.mkdir(parents=True, exist_ok=True)
    reports_list.write_text("", encoding="utf-8")
    failure = {
        "format": "weave-loupe-scheduled-failures-v1",
        "timestamp_utc": now.replace(microsecond=0).isoformat(),
        "model": model,
        "endpoint": endpoint,
        "max_tokens": max_tokens,
        "compiler": {
            **asdict(identity),
            "binary_sha256": compiler_binary_sha256,
        },
        "auditor": auditor.metadata(),
        "compiler_findings": [],
        "infrastructure_failures": [
            {
                "source": "corpus discovery",
                "report": "",
                "reason": message,
                "returncode": 1,
                "stdout_log": "",
                "stderr_log": "",
                "kind": "discovery",
                "duration_seconds": 0.0,
                "failure_class": "infrastructure",
            }
        ],
    }
    failures_json.parent.mkdir(parents=True, exist_ok=True)
    failures_json.write_text(
        json.dumps(failure, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
