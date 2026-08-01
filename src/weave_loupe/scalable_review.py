"""Token-aware single-request and staged LLM review orchestration."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, replace
from typing import Any, Literal

from weave_loupe.audit_result import (
    AuditProtocolError,
    AuditVerdict,
    parse_audit_response,
)
from weave_loupe.llm import LlmConfig, LlmError, LlmResponse, chat_completion

REVIEW_PLAN_FORMAT = "weave-loupe-review-plan-v1"
TOKEN_ESTIMATOR_FORMAT = "utf8-byte-upper-bound-v1"
DEFAULT_TOTAL_REVIEW_TOKENS = 524_288
DEFAULT_REQUEST_REVIEW_TOKENS = 98_304
DEFAULT_ARTIFACT_REVIEW_TOKENS = 262_144
DEFAULT_CHUNK_OUTPUT_TOKENS = 512

_FAILED = re.compile(r"^FAILED:\s*([a-z0-9]+(?:-[a-z0-9]+)*):\s*(\S(?:.*\S)?)\s*$")


class ReviewPlanningError(ValueError):
    """Raised when complete model-review coverage cannot satisfy policy."""


@dataclass(frozen=True)
class ReviewPolicy:
    """Conservative input and output budgets for one complete audit review."""

    max_total_tokens: int = DEFAULT_TOTAL_REVIEW_TOKENS
    max_request_tokens: int = DEFAULT_REQUEST_REVIEW_TOKENS
    max_artifact_tokens: int = DEFAULT_ARTIFACT_REVIEW_TOKENS
    chunk_output_tokens: int = DEFAULT_CHUNK_OUTPUT_TOKENS

    def __post_init__(self) -> None:
        values = {
            "max_total_tokens": self.max_total_tokens,
            "max_request_tokens": self.max_request_tokens,
            "max_artifact_tokens": self.max_artifact_tokens,
            "chunk_output_tokens": self.chunk_output_tokens,
        }
        for name, value in values.items():
            if value <= 0:
                raise ReviewPlanningError(f"{name} must be positive")
        if self.max_request_tokens > self.max_total_tokens:
            raise ReviewPlanningError(
                "max_request_tokens cannot exceed max_total_tokens"
            )
        if self.chunk_output_tokens >= self.max_request_tokens:
            raise ReviewPlanningError(
                "chunk_output_tokens must be smaller than max_request_tokens"
            )

    def metadata(self) -> dict[str, int]:
        return {
            "max_total_tokens": self.max_total_tokens,
            "max_request_tokens": self.max_request_tokens,
            "max_artifact_tokens": self.max_artifact_tokens,
            "chunk_output_tokens": self.chunk_output_tokens,
        }


@dataclass(frozen=True)
class EvidenceArtifact:
    """One complete textual evidence artifact supplied to model review."""

    name: str
    label: str
    language: str
    content: str


@dataclass(frozen=True)
class CoverageRange:
    """An exact UTF-8 byte range reviewed by one request."""

    artifact: str
    start: int
    end: int
    sha256: str

    def metadata(self) -> dict[str, str | int]:
        return {
            "artifact": self.artifact,
            "start": self.start,
            "end": self.end,
            "sha256": self.sha256,
        }


@dataclass(frozen=True)
class PlannedChunk:
    artifact: EvidenceArtifact
    index: int
    coverage: CoverageRange
    content: str


@dataclass(frozen=True)
class ReviewOutcome:
    """Final strict verdict plus complete request and coverage provenance."""

    verdict: AuditVerdict
    response: str
    final_completion: LlmResponse
    metadata: dict[str, Any]


CompletionFunction = Callable[[LlmConfig, str], LlmResponse]


def estimate_tokens(text: str) -> int:
    """Return a deterministic upper bound for byte-level BPE tokenizers."""
    return len(text.encode("utf-8")) + 16


def review_evidence(
    *,
    config: LlmConfig,
    full_prompt: str,
    artifacts: Sequence[EvidenceArtifact],
    deterministic_summary: Mapping[str, Any],
    policy: ReviewPolicy,
    complete: CompletionFunction = chat_completion,
) -> ReviewOutcome:
    """Review complete evidence in one request or a deterministic staged plan."""
    ordered = tuple(artifacts)
    _validate_artifacts(ordered, policy)
    single_estimate = estimate_tokens(full_prompt)
    single_cost = single_estimate + config.max_tokens
    if (
        single_cost <= policy.max_request_tokens
        and single_cost <= policy.max_total_tokens
    ):
        return _single_review(
            config=config,
            prompt=full_prompt,
            estimate=single_estimate,
            artifacts=ordered,
            policy=policy,
            complete=complete,
        )

    chunks = tuple(
        chunk
        for artifact in ordered
        for chunk in _chunk_artifact(
            artifact,
            max_request_tokens=policy.max_request_tokens,
            reserved_output_tokens=policy.chunk_output_tokens,
        )
    )
    chunk_prompts = tuple(
        _render_chunk_prompt(chunk=chunk, summary=deterministic_summary)
        for chunk in chunks
    )
    synthesis_reserve = _synthesis_worst_case(
        chunks=chunks,
        summary=deterministic_summary,
        chunk_output_tokens=policy.chunk_output_tokens,
    )
    planned_total = (
        sum(
            estimate_tokens(prompt) + policy.chunk_output_tokens
            for prompt in chunk_prompts
        )
        + synthesis_reserve
        + config.max_tokens
    )
    _check_staged_plan(
        planned_total=planned_total,
        synthesis_reserve=synthesis_reserve,
        final_output_tokens=config.max_tokens,
        policy=policy,
    )
    return _staged_review(
        config=config,
        chunks=chunks,
        prompts=chunk_prompts,
        summary=deterministic_summary,
        artifacts=ordered,
        policy=policy,
        complete=complete,
    )


def _single_review(
    *,
    config: LlmConfig,
    prompt: str,
    estimate: int,
    artifacts: Sequence[EvidenceArtifact],
    policy: ReviewPolicy,
    complete: CompletionFunction,
) -> ReviewOutcome:
    completion = _complete_checked(
        complete=complete,
        config=config,
        prompt=prompt,
        request_id="single-0001",
    )
    verdict = parse_audit_response(completion.content)
    chunks = tuple(
        PlannedChunk(
            artifact=artifact,
            index=0,
            coverage=_full_coverage(artifact),
            content=artifact.content,
        )
        for artifact in artifacts
    )
    request = _request_metadata(
        request_id="single-0001",
        kind="single",
        estimate=estimate,
        reserved_output=config.max_tokens,
        coverage=[chunk.coverage for chunk in chunks],
        completion=completion,
    )
    return ReviewOutcome(
        verdict=verdict,
        response=completion.content,
        final_completion=completion,
        metadata=_plan_metadata(
            mode="single",
            policy=policy,
            requests=[request],
            artifacts=artifacts,
            chunks=chunks,
            estimated_total=estimate + config.max_tokens,
        ),
    )


def _staged_review(
    *,
    config: LlmConfig,
    chunks: Sequence[PlannedChunk],
    prompts: Sequence[str],
    summary: Mapping[str, Any],
    artifacts: Sequence[EvidenceArtifact],
    policy: ReviewPolicy,
    complete: CompletionFunction,
) -> ReviewOutcome:
    requests: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    chunk_config = replace(
        config,
        max_tokens=min(config.max_tokens, policy.chunk_output_tokens),
    )
    paired = zip(chunks, prompts, strict=True)
    for position, (chunk, prompt) in enumerate(paired, start=1):
        request_id = f"artifact-{position:04d}"
        estimate = estimate_tokens(prompt)
        if estimate + chunk_config.max_tokens > policy.max_request_tokens:
            raise ReviewPlanningError(
                f"planned request {request_id} exceeds max_request_tokens"
            )
        try:
            completion = _complete_checked(
                complete=complete,
                config=chunk_config,
                prompt=prompt,
                request_id=request_id,
            )
        except LlmError as exc:
            message = f"staged review request {request_id} failed: {exc}"
            raise LlmError(message) from None
        finding = _parse_chunk_response(completion.content, request_id=request_id)
        findings.append(
            {
                "request_id": request_id,
                "artifact": chunk.artifact.name,
                "coverage": chunk.coverage.metadata(),
                **finding,
            }
        )
        requests.append(
            _request_metadata(
                request_id=request_id,
                kind="artifact",
                estimate=estimate,
                reserved_output=chunk_config.max_tokens,
                coverage=[chunk.coverage],
                completion=completion,
            )
        )

    synthesis_prompt = _render_synthesis_prompt(
        summary=summary,
        findings=findings,
        chunks=chunks,
    )
    synthesis_estimate = estimate_tokens(synthesis_prompt)
    _check_actual_total(
        requests=requests,
        synthesis_estimate=synthesis_estimate,
        final_output_tokens=config.max_tokens,
        policy=policy,
    )
    final = _complete_checked(
        complete=complete,
        config=config,
        prompt=synthesis_prompt,
        request_id="synthesis-0001",
    )
    verdict = parse_audit_response(final.content)
    requests.append(
        _request_metadata(
            request_id="synthesis-0001",
            kind="synthesis",
            estimate=synthesis_estimate,
            reserved_output=config.max_tokens,
            coverage=[],
            completion=final,
            depends_on=[str(request["request_id"]) for request in requests],
        )
    )
    estimated_total = sum(
        int(request["estimated_input_tokens"]) + int(request["reserved_output_tokens"])
        for request in requests
    )
    return ReviewOutcome(
        verdict=verdict,
        response=final.content,
        final_completion=final,
        metadata=_plan_metadata(
            mode="staged",
            policy=policy,
            requests=requests,
            artifacts=artifacts,
            chunks=chunks,
            estimated_total=estimated_total,
        ),
    )


def _check_staged_plan(
    *,
    planned_total: int,
    synthesis_reserve: int,
    final_output_tokens: int,
    policy: ReviewPolicy,
) -> None:
    if planned_total > policy.max_total_tokens:
        raise ReviewPlanningError(
            "complete staged review requires an estimated "
            f"{planned_total} tokens, exceeding max_total_tokens="
            f"{policy.max_total_tokens}"
        )
    if synthesis_reserve + final_output_tokens > policy.max_request_tokens:
        raise ReviewPlanningError(
            "final synthesis cannot fit max_request_tokens after reserving "
            "complete chunk findings"
        )


def _check_actual_total(
    *,
    requests: Sequence[Mapping[str, Any]],
    synthesis_estimate: int,
    final_output_tokens: int,
    policy: ReviewPolicy,
) -> None:
    if synthesis_estimate + final_output_tokens > policy.max_request_tokens:
        raise ReviewPlanningError(
            "actual final synthesis exceeds max_request_tokens; reduce artifact "
            "size or increase the configured request budget"
        )
    actual_total = (
        sum(
            int(request["estimated_input_tokens"])
            + int(request["reserved_output_tokens"])
            for request in requests
        )
        + synthesis_estimate
        + final_output_tokens
    )
    if actual_total > policy.max_total_tokens:
        raise ReviewPlanningError(
            "actual staged review exceeds max_total_tokens after artifact reviews"
        )


def _validate_artifacts(
    artifacts: Sequence[EvidenceArtifact],
    policy: ReviewPolicy,
) -> None:
    names: set[str] = set()
    for artifact in artifacts:
        if not artifact.name or artifact.name in names:
            raise ReviewPlanningError(
                "review artifact names must be unique non-empty strings"
            )
        names.add(artifact.name)
        estimate = estimate_tokens(artifact.content)
        if estimate > policy.max_artifact_tokens:
            raise ReviewPlanningError(
                f"artifact {artifact.name!r} requires an estimated {estimate} "
                "tokens, exceeding max_artifact_tokens="
                f"{policy.max_artifact_tokens}"
            )


def _complete_checked(
    *,
    complete: CompletionFunction,
    config: LlmConfig,
    prompt: str,
    request_id: str,
) -> LlmResponse:
    completion = complete(config, prompt)
    if completion.finish_reason not in {None, "stop"}:
        raise LlmError(
            f"review request {request_id} ended with finish reason "
            f"{completion.finish_reason!r}"
        )
    return completion


def _parse_chunk_response(content: str, *, request_id: str) -> dict[str, Any]:
    normalized = content.replace("\r\n", "\n").lstrip("\ufeff")
    lines = normalized.splitlines()
    if not lines:
        raise AuditProtocolError(f"review request {request_id} returned no content")
    first = lines[0].strip()
    body = "\n".join(lines[1:]).strip()
    if first == "REVIEWED":
        return {
            "status": "REVIEWED",
            "code": None,
            "reason": None,
            "body": body,
        }
    failed = _FAILED.fullmatch(first)
    if failed is not None:
        return {
            "status": "FAILED",
            "code": failed.group(1),
            "reason": failed.group(2),
            "body": body,
        }
    raise AuditProtocolError(
        f"review request {request_id} first line must be REVIEWED or "
        "FAILED: <lowercase-kebab-code>: <reason>"
    )


def _chunk_artifact(
    artifact: EvidenceArtifact,
    *,
    max_request_tokens: int,
    reserved_output_tokens: int,
) -> tuple[PlannedChunk, ...]:
    prompt_overhead = estimate_tokens(
        _render_chunk_prompt(
            chunk=PlannedChunk(
                artifact=artifact,
                index=0,
                coverage=CoverageRange(
                    artifact=artifact.name,
                    start=0,
                    end=0,
                    sha256=hashlib.sha256(b"").hexdigest(),
                ),
                content="",
            ),
            summary={},
        )
    )
    content_limit = max_request_tokens - reserved_output_tokens - prompt_overhead - 512
    if content_limit <= 0:
        raise ReviewPlanningError(
            "max_request_tokens is too small for the staged review protocol"
        )
    data = artifact.content.encode("utf-8")
    if not data:
        coverage = CoverageRange(
            artifact=artifact.name,
            start=0,
            end=0,
            sha256=hashlib.sha256(data).hexdigest(),
        )
        return (
            PlannedChunk(
                artifact=artifact,
                index=0,
                coverage=coverage,
                content="",
            ),
        )

    boundaries = _structural_boundaries(artifact, data)
    chunks: list[PlannedChunk] = []
    start = 0
    while start < len(data):
        limit = min(len(data), start + content_limit)
        candidates = [boundary for boundary in boundaries if start < boundary <= limit]
        end = max(candidates) if candidates else _safe_utf8_end(data, limit, start)
        if end <= start:
            raise ReviewPlanningError(
                f"unable to make progress while chunking artifact {artifact.name!r}"
            )
        payload = data[start:end]
        coverage = CoverageRange(
            artifact=artifact.name,
            start=start,
            end=end,
            sha256=hashlib.sha256(payload).hexdigest(),
        )
        chunks.append(
            PlannedChunk(
                artifact=artifact,
                index=len(chunks),
                coverage=coverage,
                content=payload.decode("utf-8"),
            )
        )
        start = end
    _validate_coverage(artifact, chunks)
    return tuple(chunks)


def _structural_boundaries(
    artifact: EvidenceArtifact,
    data: bytes,
) -> tuple[int, ...]:
    text = data.decode("utf-8")
    offsets = [0]
    position = 0
    patterns = _boundary_patterns(artifact.name)
    for line in text.splitlines(keepends=True):
        if any(pattern.search(line) for pattern in patterns):
            offsets.append(position)
        position += len(line.encode("utf-8"))
        offsets.append(position)
    offsets.append(len(data))
    return tuple(sorted(set(offsets)))


def _boundary_patterns(name: str) -> tuple[re.Pattern[str], ...]:
    lowered = name.lower()
    if "llvm" in lowered:
        return (
            re.compile(r"^define\b"),
            re.compile(r"^declare\b"),
            re.compile(r"^attributes\b"),
        )
    if "disassembly" in lowered:
        return (
            re.compile(r"^[0-9a-fA-F]+\s+<[^>]+>:\s*$"),
            re.compile(r"^[A-Za-z_.$][\w.$@-]*:\s*$"),
        )
    if "assembly" in lowered:
        return (re.compile(r"^[A-Za-z_.$][\w.$@-]*:\s*(?:[#;].*)?$"),)
    if "optimization" in lowered:
        return (re.compile(r"^---(?:\s|$)"),)
    if name in {"source", "wir"}:
        return (
            re.compile(r"^---\s+.*\s+---\s*$"),
            re.compile(r"^\s*\((?:program|fn|entry)\b"),
        )
    return (re.compile(r"^\s*[}\]]?[,]?\s*$"),)


def _safe_utf8_end(data: bytes, limit: int, start: int) -> int:
    end = limit
    while end > start:
        try:
            data[start:end].decode("utf-8")
            return end
        except UnicodeDecodeError:
            end -= 1
    return start


def _validate_coverage(
    artifact: EvidenceArtifact,
    chunks: Sequence[PlannedChunk],
) -> None:
    expected = 0
    for chunk in chunks:
        if chunk.coverage.start != expected:
            raise ReviewPlanningError(
                f"artifact {artifact.name!r} coverage contains a gap or overlap"
            )
        expected = chunk.coverage.end
    if expected != len(artifact.content.encode("utf-8")):
        raise ReviewPlanningError(f"artifact {artifact.name!r} coverage is incomplete")


def _full_coverage(artifact: EvidenceArtifact) -> CoverageRange:
    data = artifact.content.encode("utf-8")
    return CoverageRange(
        artifact=artifact.name,
        start=0,
        end=len(data),
        sha256=hashlib.sha256(data).hexdigest(),
    )


def _render_chunk_prompt(
    *,
    chunk: PlannedChunk,
    summary: Mapping[str, Any],
) -> str:
    coverage = chunk.coverage
    summary_json = json.dumps(
        summary,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return (
        "You are reviewing one exact byte range from a complete Weave compiler "
        "audit. Inspect only supported findings and do not infer missing context.\n\n"
        "The first line must be exactly one of:\n\n"
        "REVIEWED\n"
        "FAILED: <lowercase-kebab-code>: <one-line reason>\n\n"
        "After the first line, provide a concise evidence summary for final "
        "synthesis. Include functions, blocks, instructions, locations, and "
        "cross-stage concerns visible in this range. A FAILED result records a "
        "candidate blocking finding; final synthesis decides the overall gate.\n\n"
        "=== Deterministic audit summary ===\n"
        f"{summary_json}\n"
        "=== End deterministic summary ===\n\n"
        f"Artifact: {chunk.artifact.name}\n"
        f"Label: {chunk.artifact.label}\n"
        f"Language: {chunk.artifact.language}\n"
        f"Chunk: {chunk.index}\n"
        f"UTF-8 bytes: [{coverage.start}, {coverage.end})\n"
        f"Chunk SHA-256: {coverage.sha256}\n\n"
        "=== Evidence range ===\n"
        f"{chunk.content}"
        "\n=== End evidence range ===\n"
    )


def _render_synthesis_prompt(
    *,
    summary: Mapping[str, Any],
    findings: Sequence[Mapping[str, Any]],
    chunks: Sequence[PlannedChunk],
) -> str:
    coverage = [chunk.coverage.metadata() for chunk in chunks]
    return (
        "You are the final adversarial release-gate reviewer for the Weave compiler. "
        "Every required textual artifact was reviewed through exact, hash-addressed "
        "UTF-8 byte ranges. Synthesize the deterministic evidence and all artifact "
        "reviews without weakening any supported finding.\n\n"
        "Your first output line MUST be exactly one of:\n\n"
        "OK\n"
        "FAILED: <lowercase-kebab-code>: <one-line reason>\n\n"
        "After it, provide the complete Markdown audit review with a verification "
        "matrix, blocking findings, non-blocking opportunities, and suggested "
        "verification. Any FAILED artifact review must be resolved explicitly. "
        "Fail with insufficient-evidence when the supplied summaries cannot "
        "support an essential correctness, safety, ABI, target, runtime, or "
        "final-code claim.\n\n"
        "=== Deterministic audit summary ===\n"
        + json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False)
        + "\n=== End deterministic summary ===\n\n"
        "=== Complete coverage map ===\n"
        + json.dumps(coverage, indent=2, sort_keys=True, ensure_ascii=False)
        + "\n=== End coverage map ===\n\n"
        "=== Artifact review findings ===\n"
        + json.dumps(list(findings), indent=2, sort_keys=True, ensure_ascii=False)
        + "\n=== End artifact findings ===\n"
    )


def _synthesis_worst_case(
    *,
    chunks: Sequence[PlannedChunk],
    summary: Mapping[str, Any],
    chunk_output_tokens: int,
) -> int:
    placeholder_findings = [
        {
            "request_id": f"artifact-{index:04d}",
            "artifact": chunk.artifact.name,
            "coverage": chunk.coverage.metadata(),
            "status": "REVIEWED",
            "code": None,
            "reason": None,
            "body": "x" * (chunk_output_tokens * 4),
        }
        for index, chunk in enumerate(chunks, start=1)
    ]
    return estimate_tokens(
        _render_synthesis_prompt(
            summary=summary,
            findings=placeholder_findings,
            chunks=chunks,
        )
    )


def _request_metadata(
    *,
    request_id: str,
    kind: Literal["single", "artifact", "synthesis"],
    estimate: int,
    reserved_output: int,
    coverage: Sequence[CoverageRange],
    completion: LlmResponse,
    depends_on: Sequence[str] = (),
) -> dict[str, Any]:
    return {
        "request_id": request_id,
        "kind": kind,
        "estimated_input_tokens": estimate,
        "reserved_output_tokens": reserved_output,
        "coverage": [item.metadata() for item in coverage],
        "depends_on": list(depends_on),
        "completion": completion.metadata(),
    }


def _plan_metadata(
    *,
    mode: Literal["single", "staged"],
    policy: ReviewPolicy,
    requests: Sequence[Mapping[str, Any]],
    artifacts: Sequence[EvidenceArtifact],
    chunks: Sequence[PlannedChunk],
    estimated_total: int,
) -> dict[str, Any]:
    coverage_by_artifact: dict[str, list[dict[str, str | int]]] = {
        artifact.name: [] for artifact in artifacts
    }
    for chunk in chunks:
        coverage_by_artifact[chunk.artifact.name].append(chunk.coverage.metadata())
    artifact_metadata = []
    for artifact in artifacts:
        data = artifact.content.encode("utf-8")
        ranges = coverage_by_artifact[artifact.name]
        artifact_metadata.append(
            {
                "name": artifact.name,
                "label": artifact.label,
                "language": artifact.language,
                "size": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
                "estimated_tokens": estimate_tokens(artifact.content),
                "coverage": ranges,
                "complete": _ranges_complete(ranges, len(data)),
            }
        )
    return {
        "format": REVIEW_PLAN_FORMAT,
        "mode": mode,
        "token_estimator": TOKEN_ESTIMATOR_FORMAT,
        "policy": policy.metadata(),
        "estimated_total_tokens": estimated_total,
        "request_count": len(requests),
        "requests": [dict(request) for request in requests],
        "artifacts": artifact_metadata,
    }


def _ranges_complete(
    ranges: Sequence[Mapping[str, Any]],
    size: int,
) -> bool:
    expected = 0
    for item in ranges:
        start = item.get("start")
        end = item.get("end")
        if not isinstance(start, int) or not isinstance(end, int) or start != expected:
            return False
        expected = end
    return expected == size
