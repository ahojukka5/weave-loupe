"""Public staged-review policy and summary-aware chunk planning."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence
from typing import Any

from weave_loupe import scalable_review_core as _core
from weave_loupe.llm import LlmConfig, chat_completion
from weave_loupe.scalable_review_core import (
    DEFAULT_ARTIFACT_REVIEW_TOKENS,
    DEFAULT_REQUEST_REVIEW_TOKENS,
    DEFAULT_TOTAL_REVIEW_TOKENS,
    REVIEW_PLAN_FORMAT,
    TOKEN_ESTIMATOR_FORMAT,
    CompletionFunction,
    CoverageRange,
    EvidenceArtifact,
    PlannedChunk,
    ReviewOutcome,
    ReviewPlanningError,
    estimate_tokens,
)

DEFAULT_CHUNK_OUTPUT_TOKENS = 1024


class ReviewPolicy(_core.ReviewPolicy):
    """Conservative review budgets with room for complete artifact findings."""

    def __init__(
        self,
        max_total_tokens: int = DEFAULT_TOTAL_REVIEW_TOKENS,
        max_request_tokens: int = DEFAULT_REQUEST_REVIEW_TOKENS,
        max_artifact_tokens: int = DEFAULT_ARTIFACT_REVIEW_TOKENS,
        chunk_output_tokens: int = DEFAULT_CHUNK_OUTPUT_TOKENS,
    ) -> None:
        super().__init__(
            max_total_tokens=max_total_tokens,
            max_request_tokens=max_request_tokens,
            max_artifact_tokens=max_artifact_tokens,
            chunk_output_tokens=chunk_output_tokens,
        )


def review_evidence(
    *,
    config: LlmConfig,
    full_prompt: str,
    artifacts: Sequence[EvidenceArtifact],
    deterministic_summary: Mapping[str, Any],
    policy: ReviewPolicy,
    complete: CompletionFunction = chat_completion,
) -> ReviewOutcome:
    """Review complete evidence using summary-aware staged chunk admission."""
    ordered = tuple(artifacts)
    _core._validate_artifacts(ordered, policy)
    single_estimate = estimate_tokens(full_prompt)
    single_cost = single_estimate + config.max_tokens
    if (
        single_cost <= policy.max_request_tokens
        and single_cost <= policy.max_total_tokens
    ):
        return _core._single_review(
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
            summary=deterministic_summary,
            max_request_tokens=policy.max_request_tokens,
            reserved_output_tokens=policy.chunk_output_tokens,
        )
    )
    prompts = tuple(
        _core._render_chunk_prompt(chunk=chunk, summary=deterministic_summary)
        for chunk in chunks
    )
    synthesis_reserve = _core._synthesis_worst_case(
        chunks=chunks,
        summary=deterministic_summary,
        chunk_output_tokens=policy.chunk_output_tokens,
    )
    planned_total = (
        sum(estimate_tokens(prompt) + policy.chunk_output_tokens for prompt in prompts)
        + synthesis_reserve
        + config.max_tokens
    )
    _core._check_staged_plan(
        planned_total=planned_total,
        synthesis_reserve=synthesis_reserve,
        final_output_tokens=config.max_tokens,
        policy=policy,
    )
    return _core._staged_review(
        config=config,
        chunks=chunks,
        prompts=prompts,
        summary=deterministic_summary,
        artifacts=ordered,
        policy=policy,
        complete=complete,
    )


def _chunk_artifact(
    artifact: EvidenceArtifact,
    *,
    summary: Mapping[str, Any],
    max_request_tokens: int,
    reserved_output_tokens: int,
) -> tuple[PlannedChunk, ...]:
    """Split one artifact using the exact summary present in each request."""
    empty_sha256 = hashlib.sha256(b"").hexdigest()
    probe = PlannedChunk(
        artifact=artifact,
        index=0,
        coverage=CoverageRange(
            artifact=artifact.name,
            start=0,
            end=0,
            sha256=empty_sha256,
        ),
        content="",
    )
    prompt_overhead = estimate_tokens(
        _core._render_chunk_prompt(chunk=probe, summary=summary)
    )
    content_limit = max_request_tokens - reserved_output_tokens - prompt_overhead - 512
    if content_limit <= 0:
        raise ReviewPlanningError(
            "max_request_tokens is too small for the staged review protocol "
            "and deterministic summary"
        )

    data = artifact.content.encode("utf-8")
    if not data:
        return (
            PlannedChunk(
                artifact=artifact,
                index=0,
                coverage=CoverageRange(
                    artifact=artifact.name,
                    start=0,
                    end=0,
                    sha256=empty_sha256,
                ),
                content="",
            ),
        )

    boundaries = _core._structural_boundaries(artifact, data)
    chunks: list[PlannedChunk] = []
    start = 0
    while start < len(data):
        limit = min(len(data), start + content_limit)
        candidates = [boundary for boundary in boundaries if start < boundary <= limit]
        if candidates:
            end = max(candidates)
        else:
            end = _core._safe_utf8_end(data, limit, start)
        if end <= start:
            raise ReviewPlanningError(
                f"unable to make progress while chunking artifact {artifact.name!r}"
            )
        payload = data[start:end]
        chunks.append(
            PlannedChunk(
                artifact=artifact,
                index=len(chunks),
                coverage=CoverageRange(
                    artifact=artifact.name,
                    start=start,
                    end=end,
                    sha256=hashlib.sha256(payload).hexdigest(),
                ),
                content=payload.decode("utf-8"),
            )
        )
        start = end
    _core._validate_coverage(artifact, chunks)
    return tuple(chunks)


__all__ = [
    "DEFAULT_ARTIFACT_REVIEW_TOKENS",
    "DEFAULT_CHUNK_OUTPUT_TOKENS",
    "DEFAULT_REQUEST_REVIEW_TOKENS",
    "DEFAULT_TOTAL_REVIEW_TOKENS",
    "REVIEW_PLAN_FORMAT",
    "TOKEN_ESTIMATOR_FORMAT",
    "CompletionFunction",
    "CoverageRange",
    "EvidenceArtifact",
    "PlannedChunk",
    "ReviewOutcome",
    "ReviewPlanningError",
    "ReviewPolicy",
    "estimate_tokens",
    "review_evidence",
]
