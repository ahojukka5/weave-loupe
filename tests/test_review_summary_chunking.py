"""Regression tests for summary-aware staged-review chunk planning."""

from __future__ import annotations

import hashlib

from weave_loupe.llm import LlmConfig, LlmResponse
from weave_loupe.scalable_review import (
    EvidenceArtifact,
    ReviewPolicy,
    review_evidence,
)


def test_staged_chunks_include_real_summary_in_request_budget() -> None:
    config = LlmConfig(
        endpoint="https://example.test/v1",
        api_key="secret",
        model="review-model",
        max_tokens=512,
    )
    policy = ReviewPolicy(
        max_total_tokens=100_000,
        max_request_tokens=12_000,
        max_artifact_tokens=20_000,
        chunk_output_tokens=128,
    )
    summary = {"complete_analysis": "S" * 4_000}
    artifact = EvidenceArtifact(
        name="analysis",
        label="Complete deterministic analysis",
        language="json",
        content="A" * 12_000,
    )
    prompts: list[tuple[LlmConfig, str]] = []

    def complete(request_config: LlmConfig, prompt: str) -> LlmResponse:
        prompts.append((request_config, prompt))
        content = (
            "OK\nAll staged evidence is covered."
            if prompt.startswith("You are the final adversarial")
            else "REVIEWED\nNo blocking finding in this exact range."
        )
        return _response(request_config, prompt, content, len(prompts))

    outcome = review_evidence(
        config=config,
        full_prompt="P" * 11_600,
        artifacts=[artifact],
        deterministic_summary=summary,
        policy=policy,
        complete=complete,
    )

    assert outcome.metadata["mode"] == "staged"
    artifact_requests = [
        request
        for request in outcome.metadata["requests"]
        if request["kind"] == "artifact"
    ]
    assert len(artifact_requests) >= 2
    for request in outcome.metadata["requests"]:
        assert (
            request["estimated_input_tokens"] + request["reserved_output_tokens"]
            <= policy.max_request_tokens
        )
    for request_config, prompt in prompts[:-1]:
        assert request_config.max_tokens == policy.chunk_output_tokens
        assert "S" * 4_000 in prompt


def _response(
    config: LlmConfig,
    prompt: str,
    content: str,
    request_index: int,
) -> LlmResponse:
    prompt_sha256 = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    request_sha256 = hashlib.sha256(f"{request_index}:{prompt}".encode()).hexdigest()
    return LlmResponse(
        content=content,
        requested_model=config.model,
        endpoint=config.endpoint_identity,
        max_tokens=config.max_tokens,
        temperature=config.temperature,
        prompt_sha256=prompt_sha256,
        request_sha256=request_sha256,
        provider_model=config.model,
        response_id=f"response-{request_index}",
        system_fingerprint=None,
        finish_reason="stop",
        created=None,
        prompt_tokens=None,
        completion_tokens=None,
        total_tokens=None,
    )
