"""Independent verification of generated audit report validity."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

from weave_loupe.auditor_identity import AuditorIdentity, sha256_file
from weave_loupe.compiler_version import CompilerVersion
from weave_loupe.report_integrity import (
    REPORT_CONTENT_PREFIX,
    inspect_report_integrity,
)

_TIMESTAMP_PREFIX = "- **Audit timestamp (UTC):** `"
_VERSION_PREFIX = "- **weavec version:** `"
_VERSION_SOURCE_PREFIX = "- **weavec version source:** `"
_COMPILER_BINARY_PREFIX = "- **weavec binary SHA-256:** `"
_AUDITOR_PREFIX = "- **Auditor content SHA-256:** `"
_ENDPOINT_PREFIX = "- **LLM endpoint:** `"
_MODEL_PREFIX = "- **LLM model:** `"
_PROVIDER_MODEL_PREFIX = "- **Provider-reported model:** `"
_RESPONSE_ID_PREFIX = "- **Provider response ID:** `"
_SYSTEM_FINGERPRINT_PREFIX = "- **Provider system fingerprint:** `"
_SOURCE_INPUT = re.compile(
    r"^- (?:Source )?`(?P<path>[^`]+\.weave)` — SHA-256 "
    r"`(?P<sha256>[0-9a-f]{64})`$"
)
_RUNTIME_INPUT = re.compile(
    r"^- Runtime matrix `(?P<path>[^`]+\.audit\.json)` — SHA-256 "
    r"`(?P<sha256>[0-9a-f]{64})`$"
)


@dataclass(frozen=True)
class ReportIdentity:
    """Stable validity fields parsed from one generated Markdown report."""

    timestamp: datetime | None
    version: str | None
    version_source: str | None
    compiler_binary_sha256: str | None
    auditor_sha256: str | None
    model: str | None
    source_path: str | None
    source_sha256: str | None
    runtime_path: str | None
    runtime_sha256: str | None
    report_content_sha256: str | None = None
    endpoint: str | None = None
    provider_model: str | None = None
    response_id: str | None = None
    system_fingerprint: str | None = None


@dataclass(frozen=True)
class ValidityResult:
    """All reasons a report is stale under the current policy and toolchain."""

    report: Path
    source: Path
    identity: ReportIdentity
    reasons: tuple[str, ...]

    @property
    def valid(self) -> bool:
        return not self.reasons

    @property
    def primary_reason(self) -> str | None:
        return self.reasons[0] if self.reasons else None


def read_report_identity(report: Path) -> ReportIdentity:
    """Parse only the stable report envelope, never model-controlled prose."""
    try:
        lines = report.read_text(encoding="utf-8").splitlines()
    except OSError:
        return _empty_identity()

    timestamp: datetime | None = None
    version: str | None = None
    version_source: str | None = None
    compiler_binary_sha256: str | None = None
    auditor_sha256: str | None = None
    endpoint: str | None = None
    model: str | None = None
    provider_model: str | None = None
    response_id: str | None = None
    system_fingerprint: str | None = None
    source_path: str | None = None
    source_sha256: str | None = None
    runtime_path: str | None = None
    runtime_sha256: str | None = None
    report_content_sha256: str | None = None
    in_inputs = False

    for line in lines:
        if line == "## Audited inputs":
            in_inputs = True
            continue
        if in_inputs and line.startswith("## "):
            break
        if line.startswith(_TIMESTAMP_PREFIX) and line.endswith("`"):
            try:
                timestamp = parse_time(line[len(_TIMESTAMP_PREFIX) : -1])
            except ValueError:
                timestamp = None
        elif line.startswith(_VERSION_PREFIX) and line.endswith("`"):
            version = line[len(_VERSION_PREFIX) : -1]
        elif line.startswith(_VERSION_SOURCE_PREFIX) and line.endswith("`"):
            version_source = line[len(_VERSION_SOURCE_PREFIX) : -1]
        elif line.startswith(_COMPILER_BINARY_PREFIX) and line.endswith("`"):
            compiler_binary_sha256 = line[len(_COMPILER_BINARY_PREFIX) : -1]
        elif line.startswith(_AUDITOR_PREFIX) and line.endswith("`"):
            auditor_sha256 = line[len(_AUDITOR_PREFIX) : -1]
        elif line.startswith(_ENDPOINT_PREFIX) and line.endswith("`"):
            endpoint = line[len(_ENDPOINT_PREFIX) : -1]
        elif line.startswith(_MODEL_PREFIX) and line.endswith("`"):
            model = line[len(_MODEL_PREFIX) : -1]
        elif line.startswith(_PROVIDER_MODEL_PREFIX) and line.endswith("`"):
            provider_model = _available_value(
                line[len(_PROVIDER_MODEL_PREFIX) : -1]
            )
        elif line.startswith(_RESPONSE_ID_PREFIX) and line.endswith("`"):
            response_id = _available_value(line[len(_RESPONSE_ID_PREFIX) : -1])
        elif line.startswith(_SYSTEM_FINGERPRINT_PREFIX) and line.endswith("`"):
            system_fingerprint = _available_value(
                line[len(_SYSTEM_FINGERPRINT_PREFIX) : -1]
            )
        elif line.startswith(REPORT_CONTENT_PREFIX) and line.endswith("`"):
            report_content_sha256 = line[len(REPORT_CONTENT_PREFIX) : -1]
        elif in_inputs:
            source_match = _SOURCE_INPUT.fullmatch(line)
            if source_match is not None:
                source_path = source_match.group("path")
                source_sha256 = source_match.group("sha256")
                continue
            runtime_match = _RUNTIME_INPUT.fullmatch(line)
            if runtime_match is not None:
                runtime_path = runtime_match.group("path")
                runtime_sha256 = runtime_match.group("sha256")

    return ReportIdentity(
        timestamp=timestamp,
        version=version,
        version_source=version_source,
        compiler_binary_sha256=compiler_binary_sha256,
        auditor_sha256=auditor_sha256,
        model=model,
        source_path=source_path,
        source_sha256=source_sha256,
        runtime_path=runtime_path,
        runtime_sha256=runtime_sha256,
        report_content_sha256=report_content_sha256,
        endpoint=endpoint,
        provider_model=provider_model,
        response_id=response_id,
        system_fingerprint=system_fingerprint,
    )


def evaluate_report(
    *,
    report: Path,
    source: Path,
    compiler_identity: CompilerVersion,
    compiler_binary_sha256: str,
    auditor: AuditorIdentity,
    now: datetime,
    max_age: timedelta,
    force: bool = False,
    current_model: str | None = None,
    current_endpoint: str | None = None,
) -> ValidityResult:
    """Parse and evaluate one report against the current audit environment."""
    identity = read_report_identity(report)
    result = evaluate_identity(
        report=report,
        source=source,
        identity=identity,
        compiler_identity=compiler_identity,
        compiler_binary_sha256=compiler_binary_sha256,
        auditor=auditor,
        now=now,
        max_age=max_age,
        force=force,
        current_model=current_model,
        current_endpoint=current_endpoint,
    )
    if force:
        return result

    try:
        integrity = inspect_report_integrity(report.read_text(encoding="utf-8"))
    except OSError:
        return result

    reasons = list(result.reasons)
    if integrity.seal_count == 0:
        reasons.append("report does not record content hash")
    elif integrity.seal_count > 1:
        reasons.append("report records multiple content hashes")
    elif not integrity.valid:
        reasons.append("report content changed since audit")
    return ValidityResult(report, source, identity, tuple(reasons))


def evaluate_identity(
    *,
    report: Path,
    source: Path,
    identity: ReportIdentity,
    compiler_identity: CompilerVersion,
    compiler_binary_sha256: str,
    auditor: AuditorIdentity,
    now: datetime,
    max_age: timedelta,
    force: bool = False,
    current_model: str | None = None,
    current_endpoint: str | None = None,
) -> ValidityResult:
    """Evaluate an already parsed identity against current inputs and tools."""
    reasons: list[str] = []
    if force:
        reasons.append("manual force")
        return ValidityResult(report, source, identity, tuple(reasons))

    if identity.timestamp is None:
        reasons.append("missing or unparseable report timestamp")

    if identity.source_path is None:
        reasons.append("report does not record audited source path")
    elif not _same_path(identity.source_path, source):
        reasons.append("source path changed since audit")

    if identity.source_sha256 is None:
        reasons.append("report does not record audited source hash")
    elif not source.is_file():
        reasons.append("audited source file is missing")
    elif sha256_file(source) != identity.source_sha256:
        reasons.append("source content changed since audit")

    runtime = source.with_suffix(".audit.json")
    if runtime.is_file():
        if identity.runtime_path is None or identity.runtime_sha256 is None:
            reasons.append("runtime matrix was added or not recorded")
        else:
            if not _same_path(identity.runtime_path, runtime):
                reasons.append("runtime matrix path changed since audit")
            if sha256_file(runtime) != identity.runtime_sha256:
                reasons.append("runtime matrix content changed since audit")
    elif identity.runtime_path is not None or identity.runtime_sha256 is not None:
        reasons.append("runtime matrix was removed since audit")

    if identity.compiler_binary_sha256 is None:
        reasons.append("report does not record compiler binary hash")
    elif identity.compiler_binary_sha256 != compiler_binary_sha256:
        reasons.append("compiler binary changed since audit")

    if identity.auditor_sha256 is None:
        reasons.append("report does not record auditor fingerprint")
    elif identity.auditor_sha256 != auditor.sha256:
        reasons.append("audit implementation changed since audit")

    if current_model is not None:
        if identity.model is None:
            reasons.append("report does not record LLM model")
        elif identity.model != current_model:
            reasons.append(
                f"LLM model changed from {identity.model} to {current_model}"
            )

    if current_endpoint is not None:
        if identity.endpoint is None:
            reasons.append("report does not record LLM endpoint")
        elif identity.endpoint != current_endpoint:
            reasons.append(
                f"LLM endpoint changed from {identity.endpoint} to {current_endpoint}"
            )

    if identity.timestamp is not None and now - identity.timestamp >= max_age:
        reasons.append(f"report age is at least {max_age.days} days")
    if compiler_identity.development and identity.version != compiler_identity.display:
        reasons.append(
            "development compiler changed from "
            f"{identity.version or 'unknown'} to {compiler_identity.display}"
        )
    if compiler_identity.source == "command" and identity.version_source != "command":
        reasons.append(
            "compiler identity source changed from "
            f"{identity.version_source or 'unknown'} to command"
        )

    return ValidityResult(report, source, identity, tuple(reasons))


def parse_time(value: str) -> datetime:
    """Parse a report timestamp and normalize it to UTC."""
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _same_path(recorded: str, current: Path) -> bool:
    try:
        return Path(recorded).resolve() == current.resolve()
    except OSError:
        return False


def _available_value(value: str) -> str | None:
    return None if value == "unavailable" else value


def _empty_identity() -> ReportIdentity:
    return ReportIdentity(
        timestamp=None,
        version=None,
        version_source=None,
        compiler_binary_sha256=None,
        auditor_sha256=None,
        model=None,
        source_path=None,
        source_sha256=None,
        runtime_path=None,
        runtime_sha256=None,
    )
