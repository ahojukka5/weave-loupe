"""Independent verification of generated audit report validity."""

from __future__ import annotations

import re
from collections.abc import Sequence
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
_MAX_TOKENS_PREFIX = "- **LLM max tokens:** `"
_TEMPERATURE_PREFIX = "- **LLM temperature:** `"
_PROMPT_SHA256_PREFIX = "- **LLM prompt SHA-256:** `"
_REQUEST_SHA256_PREFIX = "- **LLM request SHA-256:** `"
_PROVIDER_MODEL_PREFIX = "- **Provider-reported model:** `"
_RESPONSE_ID_PREFIX = "- **Provider response ID:** `"
_SYSTEM_FINGERPRINT_PREFIX = "- **Provider system fingerprint:** `"
_FINISH_REASON_PREFIX = "- **Provider finish reason:** `"
_CREATED_PREFIX = "- **Provider created (Unix):** `"
_PROMPT_TOKENS_PREFIX = "- **Provider prompt tokens:** `"
_COMPLETION_TOKENS_PREFIX = "- **Provider completion tokens:** `"
_TOTAL_TOKENS_PREFIX = "- **Provider total tokens:** `"
_SOURCE_INPUT = re.compile(
    r"^- (?:Source )?`(?P<path>[^`]+\.weave)` — SHA-256 "
    r"`(?P<sha256>[0-9a-f]{64})`"
    r"(?: — (?P<size>[0-9]+) bytes)?$"
)
_RUNTIME_INPUT = re.compile(
    r"^- Runtime matrix `(?P<path>[^`]+\.audit\.json)` — SHA-256 "
    r"`(?P<sha256>[0-9a-f]{64})`$"
)


@dataclass(frozen=True)
class SourceIdentity:
    """One ordered source identity recorded in an audit report."""

    path: str
    sha256: str
    size: int | None = None


@dataclass(frozen=True)
class SourceMismatch:
    """Machine-readable difference between recorded and current source sets."""

    kind: str
    recorded_index: int | None
    current_index: int | None
    recorded_path: str | None
    current_path: str | None
    recorded_sha256: str | None
    current_sha256: str | None
    recorded_size: int | None
    current_size: int | None
    detail: str


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
    max_tokens: int | None = None
    temperature: float | None = None
    prompt_sha256: str | None = None
    request_sha256: str | None = None
    finish_reason: str | None = None
    created: int | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    sources: tuple[SourceIdentity, ...] = ()

    def __post_init__(self) -> None:
        """Keep legacy first-source fields synchronized with the ordered set."""
        if self.sources:
            first = self.sources[0]
            if self.source_path is None:
                object.__setattr__(self, "source_path", first.path)
            if self.source_sha256 is None:
                object.__setattr__(self, "source_sha256", first.sha256)
            return
        if self.source_path is not None and self.source_sha256 is not None:
            object.__setattr__(
                self,
                "sources",
                (SourceIdentity(self.source_path, self.source_sha256),),
            )


@dataclass(frozen=True)
class ValidityResult:
    """All reasons a report is stale under the current policy and toolchain."""

    report: Path
    source: Path
    identity: ReportIdentity
    reasons: tuple[str, ...]
    sources: tuple[Path, ...] = ()
    source_mismatches: tuple[SourceMismatch, ...] = ()

    def __post_init__(self) -> None:
        if not self.sources:
            object.__setattr__(self, "sources", (self.source,))

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
    max_tokens: int | None = None
    temperature: float | None = None
    prompt_sha256: str | None = None
    request_sha256: str | None = None
    provider_model: str | None = None
    response_id: str | None = None
    system_fingerprint: str | None = None
    finish_reason: str | None = None
    created: int | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    sources: list[SourceIdentity] = []
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
        elif line.startswith(_MAX_TOKENS_PREFIX) and line.endswith("`"):
            max_tokens = _optional_int(line[len(_MAX_TOKENS_PREFIX) : -1])
        elif line.startswith(_TEMPERATURE_PREFIX) and line.endswith("`"):
            temperature = _optional_float(line[len(_TEMPERATURE_PREFIX) : -1])
        elif line.startswith(_PROMPT_SHA256_PREFIX) and line.endswith("`"):
            prompt_sha256 = _optional_sha256(line[len(_PROMPT_SHA256_PREFIX) : -1])
        elif line.startswith(_REQUEST_SHA256_PREFIX) and line.endswith("`"):
            request_sha256 = _optional_sha256(line[len(_REQUEST_SHA256_PREFIX) : -1])
        elif line.startswith(_PROVIDER_MODEL_PREFIX) and line.endswith("`"):
            provider_model = _available_value(line[len(_PROVIDER_MODEL_PREFIX) : -1])
        elif line.startswith(_RESPONSE_ID_PREFIX) and line.endswith("`"):
            response_id = _available_value(line[len(_RESPONSE_ID_PREFIX) : -1])
        elif line.startswith(_SYSTEM_FINGERPRINT_PREFIX) and line.endswith("`"):
            system_fingerprint = _available_value(
                line[len(_SYSTEM_FINGERPRINT_PREFIX) : -1]
            )
        elif line.startswith(_FINISH_REASON_PREFIX) and line.endswith("`"):
            finish_reason = _available_value(line[len(_FINISH_REASON_PREFIX) : -1])
        elif line.startswith(_CREATED_PREFIX) and line.endswith("`"):
            created = _optional_int(line[len(_CREATED_PREFIX) : -1])
        elif line.startswith(_PROMPT_TOKENS_PREFIX) and line.endswith("`"):
            prompt_tokens = _optional_int(line[len(_PROMPT_TOKENS_PREFIX) : -1])
        elif line.startswith(_COMPLETION_TOKENS_PREFIX) and line.endswith("`"):
            completion_tokens = _optional_int(line[len(_COMPLETION_TOKENS_PREFIX) : -1])
        elif line.startswith(_TOTAL_TOKENS_PREFIX) and line.endswith("`"):
            total_tokens = _optional_int(line[len(_TOTAL_TOKENS_PREFIX) : -1])
        elif line.startswith(REPORT_CONTENT_PREFIX) and line.endswith("`"):
            report_content_sha256 = line[len(REPORT_CONTENT_PREFIX) : -1]
        elif in_inputs:
            source_match = _SOURCE_INPUT.fullmatch(line)
            if source_match is not None:
                size_text = source_match.group("size")
                sources.append(
                    SourceIdentity(
                        path=source_match.group("path"),
                        sha256=source_match.group("sha256"),
                        size=int(size_text) if size_text is not None else None,
                    )
                )
                continue
            runtime_match = _RUNTIME_INPUT.fullmatch(line)
            if runtime_match is not None:
                runtime_path = runtime_match.group("path")
                runtime_sha256 = runtime_match.group("sha256")

    first = sources[0] if sources else None
    return ReportIdentity(
        timestamp=timestamp,
        version=version,
        version_source=version_source,
        compiler_binary_sha256=compiler_binary_sha256,
        auditor_sha256=auditor_sha256,
        model=model,
        source_path=first.path if first is not None else None,
        source_sha256=first.sha256 if first is not None else None,
        runtime_path=runtime_path,
        runtime_sha256=runtime_sha256,
        report_content_sha256=report_content_sha256,
        endpoint=endpoint,
        provider_model=provider_model,
        response_id=response_id,
        system_fingerprint=system_fingerprint,
        max_tokens=max_tokens,
        temperature=temperature,
        prompt_sha256=prompt_sha256,
        request_sha256=request_sha256,
        finish_reason=finish_reason,
        created=created,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        sources=tuple(sources),
    )


def evaluate_report(
    *,
    report: Path,
    source: Path | None,
    compiler_identity: CompilerVersion,
    compiler_binary_sha256: str,
    auditor: AuditorIdentity,
    now: datetime,
    max_age: timedelta,
    force: bool = False,
    current_model: str | None = None,
    current_endpoint: str | None = None,
    current_max_tokens: int | None = None,
    sources: Sequence[Path] | None = None,
) -> ValidityResult:
    """Parse and evaluate one report against the current audit environment."""
    identity = read_report_identity(report)
    current_sources = _resolve_current_sources(
        report=report,
        identity=identity,
        source=source,
        sources=sources,
    )
    result = evaluate_identity(
        report=report,
        source=current_sources[0] if current_sources else report.with_suffix(".weave"),
        sources=current_sources,
        identity=identity,
        compiler_identity=compiler_identity,
        compiler_binary_sha256=compiler_binary_sha256,
        auditor=auditor,
        now=now,
        max_age=max_age,
        force=force,
        current_model=current_model,
        current_endpoint=current_endpoint,
        current_max_tokens=current_max_tokens,
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
    return ValidityResult(
        report=result.report,
        source=result.source,
        identity=result.identity,
        reasons=tuple(reasons),
        sources=result.sources,
        source_mismatches=result.source_mismatches,
    )


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
    current_max_tokens: int | None = None,
    sources: Sequence[Path] | None = None,
) -> ValidityResult:
    """Evaluate an already parsed identity against current inputs and tools."""
    current_sources = tuple(sources) if sources is not None else (source,)
    reasons: list[str] = []
    if force:
        reasons.append("manual force")
        return ValidityResult(
            report,
            source,
            identity,
            tuple(reasons),
            current_sources,
        )

    if identity.timestamp is None:
        reasons.append("missing or unparseable report timestamp")

    source_reasons, source_mismatches = _evaluate_sources(
        report=report,
        recorded=identity.sources,
        current=current_sources,
    )
    reasons.extend(source_reasons)

    _evaluate_runtime_input(
        report=report,
        identity=identity,
        sources=current_sources,
        reasons=reasons,
    )

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

    if current_max_tokens is not None:
        if identity.max_tokens is None:
            reasons.append("report does not record LLM max tokens")
        elif identity.max_tokens != current_max_tokens:
            reasons.append(
                f"LLM max tokens changed from {identity.max_tokens} "
                f"to {current_max_tokens}"
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

    return ValidityResult(
        report=report,
        source=source,
        identity=identity,
        reasons=tuple(reasons),
        sources=current_sources,
        source_mismatches=tuple(source_mismatches),
    )


def parse_time(value: str) -> datetime:
    """Parse a report timestamp and normalize it to UTC."""
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _evaluate_sources(
    *,
    report: Path,
    recorded: tuple[SourceIdentity, ...],
    current: tuple[Path, ...],
) -> tuple[list[str], list[SourceMismatch]]:
    reasons: list[str] = []
    mismatches: list[SourceMismatch] = []
    current_facts = tuple(_source_fact(path) for path in current)
    if not recorded:
        reasons.append("report does not record audited source path")
        reasons.append("report does not record audited source hash")
        for index, fact in enumerate(current_facts):
            mismatches.append(
                _mismatch(
                    kind="added",
                    recorded_index=None,
                    current_index=index,
                    recorded=None,
                    current=fact,
                    detail=f"unrecorded current source at index {index}",
                )
            )
        return reasons, mismatches

    mapping: dict[int, int] = {}
    unmatched_current = set(range(len(current_facts)))
    for recorded_index, item in enumerate(recorded):
        candidates = [
            current_index
            for current_index in sorted(unmatched_current)
            if _same_recorded_path(item.path, current_facts[current_index].path, report)
        ]
        if candidates:
            selected = recorded_index if recorded_index in candidates else candidates[0]
            mapping[recorded_index] = selected
            unmatched_current.remove(selected)

    for recorded_index, item in enumerate(recorded):
        if recorded_index in mapping:
            continue
        candidates = [
            current_index
            for current_index in sorted(unmatched_current)
            if current_facts[current_index].sha256 == item.sha256
        ]
        if candidates:
            selected = candidates[0]
            mapping[recorded_index] = selected
            unmatched_current.remove(selected)

    unmatched_recorded = [
        index for index in range(len(recorded)) if index not in mapping
    ]
    for recorded_index in list(unmatched_recorded):
        if (
            recorded_index >= len(current_facts)
            or recorded_index not in unmatched_current
        ):
            continue
        mapping[recorded_index] = recorded_index
        unmatched_current.remove(recorded_index)
        unmatched_recorded.remove(recorded_index)

    if (
        len(mapping) == len(recorded)
        and len(mapping) == len(current_facts)
        and [mapping[index] for index in range(len(recorded))]
        != list(range(len(recorded)))
    ):
        detail = "source order changed since audit"
        reasons.append(detail)
        mismatches.append(
            SourceMismatch(
                kind="reordered",
                recorded_index=None,
                current_index=None,
                recorded_path=None,
                current_path=None,
                recorded_sha256=None,
                current_sha256=None,
                recorded_size=None,
                current_size=None,
                detail=detail,
            )
        )

    single = len(recorded) == 1 and len(current_facts) == 1
    for recorded_index, item in enumerate(recorded):
        current_index = mapping.get(recorded_index)
        if current_index is None:
            detail = _removed_reason(item, recorded_index, single)
            reasons.append(detail)
            mismatches.append(
                _mismatch(
                    kind="removed",
                    recorded_index=recorded_index,
                    current_index=None,
                    recorded=item,
                    current=None,
                    detail=detail,
                )
            )
            continue

        fact = current_facts[current_index]
        path_matches = _same_recorded_path(item.path, fact.path, report)
        if not path_matches:
            detail = _path_reason(item, fact, recorded_index, current_index, single)
            reasons.append(detail)
            mismatches.append(
                _mismatch(
                    kind="renamed",
                    recorded_index=recorded_index,
                    current_index=current_index,
                    recorded=item,
                    current=fact,
                    detail=detail,
                )
            )
        if not fact.exists:
            detail = _missing_reason(item, recorded_index, single)
            reasons.append(detail)
            mismatches.append(
                _mismatch(
                    kind="missing",
                    recorded_index=recorded_index,
                    current_index=current_index,
                    recorded=item,
                    current=fact,
                    detail=detail,
                )
            )
            continue
        if fact.sha256 != item.sha256:
            detail = _content_reason(fact, recorded_index, single)
            reasons.append(detail)
            mismatches.append(
                _mismatch(
                    kind="modified",
                    recorded_index=recorded_index,
                    current_index=current_index,
                    recorded=item,
                    current=fact,
                    detail=detail,
                )
            )
        elif item.size is not None and fact.size != item.size:
            detail = _size_reason(fact, recorded_index, item.size, single)
            reasons.append(detail)
            mismatches.append(
                _mismatch(
                    kind="size-changed",
                    recorded_index=recorded_index,
                    current_index=current_index,
                    recorded=item,
                    current=fact,
                    detail=detail,
                )
            )

    for current_index in sorted(unmatched_current):
        fact = current_facts[current_index]
        detail = (
            "source was added since audit"
            if len(current_facts) == 1
            else f"source added since audit at index {current_index}: {fact.path}"
        )
        reasons.append(detail)
        mismatches.append(
            _mismatch(
                kind="added",
                recorded_index=None,
                current_index=current_index,
                recorded=None,
                current=fact,
                detail=detail,
            )
        )

    return reasons, mismatches


@dataclass(frozen=True)
class _SourceFact:
    path: Path
    exists: bool
    sha256: str | None
    size: int | None


def _source_fact(path: Path) -> _SourceFact:
    if not path.is_file():
        return _SourceFact(path=path, exists=False, sha256=None, size=None)
    try:
        return _SourceFact(
            path=path,
            exists=True,
            sha256=sha256_file(path),
            size=path.stat().st_size,
        )
    except OSError:
        return _SourceFact(path=path, exists=False, sha256=None, size=None)


def _mismatch(
    *,
    kind: str,
    recorded_index: int | None,
    current_index: int | None,
    recorded: SourceIdentity | None,
    current: _SourceFact | None,
    detail: str,
) -> SourceMismatch:
    return SourceMismatch(
        kind=kind,
        recorded_index=recorded_index,
        current_index=current_index,
        recorded_path=recorded.path if recorded is not None else None,
        current_path=str(current.path) if current is not None else None,
        recorded_sha256=recorded.sha256 if recorded is not None else None,
        current_sha256=current.sha256 if current is not None else None,
        recorded_size=recorded.size if recorded is not None else None,
        current_size=current.size if current is not None else None,
        detail=detail,
    )


def _removed_reason(item: SourceIdentity, index: int, single: bool) -> str:
    if single:
        return "audited source file is missing"
    return f"source removed since audit at index {index}: {item.path}"


def _missing_reason(item: SourceIdentity, index: int, single: bool) -> str:
    if single:
        return "audited source file is missing"
    return f"audited source file is missing at index {index}: {item.path}"


def _path_reason(
    item: SourceIdentity,
    fact: _SourceFact,
    recorded_index: int,
    current_index: int,
    single: bool,
) -> str:
    if single:
        return "source path changed since audit"
    return (
        f"source path changed at recorded index {recorded_index} "
        f"to current index {current_index}: {item.path} -> {fact.path}"
    )


def _content_reason(fact: _SourceFact, index: int, single: bool) -> str:
    if single:
        return "source content changed since audit"
    return f"source content changed at index {index}: {fact.path}"


def _size_reason(
    fact: _SourceFact,
    index: int,
    recorded_size: int,
    single: bool,
) -> str:
    if single:
        return "source size changed since audit"
    return (
        f"source size changed at index {index}: {fact.path} "
        f"({recorded_size} -> {fact.size})"
    )


def _evaluate_runtime_input(
    *,
    report: Path,
    identity: ReportIdentity,
    sources: tuple[Path, ...],
    reasons: list[str],
) -> None:
    runtime_candidates = tuple(
        candidate
        for candidate in (source.with_suffix(".audit.json") for source in sources)
        if candidate.is_file()
    )
    if len(runtime_candidates) > 1:
        reasons.append("multiple runtime matrices are present for current sources")
        return
    runtime = runtime_candidates[0] if runtime_candidates else None
    if runtime is not None:
        if identity.runtime_path is None or identity.runtime_sha256 is None:
            reasons.append("runtime matrix was added or not recorded")
            return
        if not _same_recorded_path(identity.runtime_path, runtime, report):
            reasons.append("runtime matrix path changed since audit")
        if sha256_file(runtime) != identity.runtime_sha256:
            reasons.append("runtime matrix content changed since audit")
    elif identity.runtime_path is not None or identity.runtime_sha256 is not None:
        reasons.append("runtime matrix was removed since audit")


def _resolve_current_sources(
    *,
    report: Path,
    identity: ReportIdentity,
    source: Path | None,
    sources: Sequence[Path] | None,
) -> tuple[Path, ...]:
    if sources is not None:
        return tuple(sources)
    if source is not None:
        return (source,)
    if identity.sources:
        return tuple(
            _resolve_recorded_source(report, item) for item in identity.sources
        )
    return (report.with_suffix(".weave"),)


def _resolve_recorded_source(report: Path, identity: SourceIdentity) -> Path:
    candidates = _recorded_path_candidates(identity.path, report)
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    root = _repository_root(report)
    if root is not None:
        matches: list[Path] = []
        try:
            possible = root.rglob(Path(identity.path).name)
            for candidate in possible:
                if candidate.is_file() and sha256_file(candidate) == identity.sha256:
                    matches.append(candidate)
        except OSError:
            matches = []
        if len(matches) == 1:
            return matches[0]
    return candidates[0] if candidates else Path(identity.path)


def _same_recorded_path(recorded: str, current: Path, report: Path) -> bool:
    current_resolved = _safe_resolve(current)
    for candidate in _recorded_path_candidates(recorded, report):
        if _safe_resolve(candidate) == current_resolved:
            return True

    root = _repository_root(report)
    if root is not None:
        try:
            relative = current_resolved.relative_to(root.resolve()).as_posix()
        except (OSError, ValueError):
            relative = None
        if relative is not None and _normalized_path(recorded).endswith(relative):
            return True
    return root is None and Path(recorded).name == current.name


def _recorded_path_candidates(recorded: str, report: Path) -> tuple[Path, ...]:
    path = Path(recorded)
    candidates: list[Path] = []
    if path.is_absolute():
        candidates.append(path)
    else:
        candidates.extend((report.parent / path, path, Path.cwd() / path))
        root = _repository_root(report)
        if root is not None:
            candidates.insert(0, root / path)

    root = _repository_root(report)
    if root is not None and path.is_absolute():
        parts = path.parts[1:]
        for index in range(len(parts)):
            candidates.append(root.joinpath(*parts[index:]))

    unique: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        key = str(_safe_resolve(candidate))
        if key not in seen:
            unique.append(candidate)
            seen.add(key)
    return tuple(unique)


def _repository_root(path: Path) -> Path | None:
    current = path.resolve().parent if path.suffix else path.resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return None


def _safe_resolve(path: Path) -> Path:
    try:
        return path.resolve()
    except OSError:
        return path.absolute()


def _normalized_path(value: str) -> str:
    return value.replace("\\", "/").lstrip("/")


def _available_value(value: str) -> str | None:
    return None if value == "unavailable" else value


def _optional_int(value: str) -> int | None:
    if value == "unavailable":
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _optional_float(value: str) -> float | None:
    if value == "unavailable":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _optional_sha256(value: str) -> str | None:
    if len(value) == 64 and all(character in "0123456789abcdef" for character in value):
        return value
    return None


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
