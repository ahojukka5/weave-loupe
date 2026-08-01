"""Tests for token-aware complete-evidence model review."""

from __future__ import annotations

import hashlib
from collections.abc import Callable

import pytest

from weave_loupe.audit_result import AuditProtocolError
from weave_loupe.llm import LlmConfig, LlmError, LlmResponse
from weave_loupe.scalable_review import (
    EvidenceArtifact,
    ReviewPlanningError,
    ReviewPolicy,
    estimate_tokens,
    review_evidence,
)


def _config(*, max_tokens: int = 128) -> LlmConfig:
    return LlmConfig(
        endpoint="https://example.test/v1",
        api_key="secret",
        model="review-model",
        max_tokens=max_tokens,
    )


def _response(
    prompt: str,
    content: str,
    *,
    finish_reason: str | None = "stop",
    request_index: int = 1,
) -> LlmResponse:
    digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    return LlmResponse(
        content=content,
        requested_model="review-model",
        endpoint="https://example.test/v1",
        max_tokens=128,
        temperature=0.0,
        prompt_sha256=digest,
        request_sha256=digest,
        provider_model="review-model-20260801",
        response_id=f"chatcmpl-{request_index}",
        system_fingerprint="fp-test",
        finish_reason=finish_reason,
        created=1785600000 + request_index,
        prompt_tokens=len(prompt.encode("utf-8")),
        completion_tokens=len(content.encode("utf-8")),
        total_tokens=len(prompt.encode("utf-8")) + len(content.encode("utf-8")),
    )


def _successful_client(prompts: list[str]) -> Callable[[LlmConfig, str], LlmResponse]:
    def complete(config: LlmConfig, prompt: str) -> LlmResponse:
        del config
        prompts.append(prompt)
        if "=== Artifact review findings ===" in prompt:
            content = "OK\n## Summary\nComplete staged evidence is consistent."
        elif "=== Evidence range ===" in prompt:
            content = "REVIEWED\nNo blocking defect in this exact range."
        else:
            content = "OK\n## Summary\nComplete evidence is consistent."
        return _response(prompt, content, request_index=len(prompts))

    return complete


def _artifact(name: str, content: str) -> EvidenceArtifact:
    return EvidenceArtifact(
        name=name,
        label=name.replace("_", " "),
        language="text",
        content=content,
    )


def _assert_complete_coverage(
    artifact: EvidenceArtifact,
    metadata: dict[str, object],
) -> None:
    artifacts = metadata["artifacts"]
    assert isinstance(artifacts, list)
    item = next(raw for raw in artifacts if raw["name"] == artifact.name)
    assert item["complete"] is True
    assert item["size"] == len(artifact.content.encode("utf-8"))
    ranges = item["coverage"]
    expected = 0
    data = artifact.content.encode("utf-8")
    for covered in ranges:
        assert covered["start"] == expected
        payload = data[covered["start"] : covered["end"]]
        assert covered["sha256"] == hashlib.sha256(payload).hexdigest()
        payload.decode("utf-8")
        expected = covered["end"]
    assert expected == len(data)


def test_exact_request_budget_retains_single_request() -> None:
    prompt = "abc"
    artifact = _artifact("source", "x")
    max_tokens = 64
    exact = estimate_tokens(prompt) + max_tokens
    prompts: list[str] = []

    outcome = review_evidence(
        config=_config(max_tokens=max_tokens),
        full_prompt=prompt,
        artifacts=[artifact],
        deterministic_summary={},
        policy=ReviewPolicy(
            max_total_tokens=exact,
            max_request_tokens=exact,
            max_artifact_tokens=100,
            chunk_output_tokens=16,
        ),
        complete=_successful_client(prompts),
    )

    assert outcome.verdict.passed is True
    assert outcome.metadata["mode"] == "single"
    assert outcome.metadata["request_count"] == 1
    assert prompts == [prompt]
    _assert_complete_coverage(artifact, outcome.metadata)


def test_large_llvm_and_disassembly_use_complete_staged_coverage() -> None:
    llvm = "".join(
        f"define i32 @f{index}() {{\nentry:\n  ret i32 {index}\n}}\n"
        for index in range(650)
    )
    disassembly = "".join(
        f"{index:08x} <f{index}>:\n  {index:08x}: c3 retq\n" for index in range(650)
    )
    artifacts = (
        _artifact("raw_llvm", llvm),
        _artifact("disassembly", disassembly),
    )
    prompts: list[str] = []

    outcome = review_evidence(
        config=_config(),
        full_prompt="x" * 50_000,
        artifacts=artifacts,
        deterministic_summary={"compiler_exit_code": 0},
        policy=ReviewPolicy(
            max_total_tokens=200_000,
            max_request_tokens=20_000,
            max_artifact_tokens=80_000,
            chunk_output_tokens=128,
        ),
        complete=_successful_client(prompts),
    )

    assert outcome.verdict.passed is True
    assert outcome.metadata["mode"] == "staged"
    assert outcome.metadata["request_count"] == len(prompts)
    requests = outcome.metadata["requests"]
    assert requests[-1]["kind"] == "synthesis"
    assert len(requests[-1]["depends_on"]) == len(requests) - 1
    assert len(requests) > 3
    for artifact in artifacts:
        _assert_complete_coverage(artifact, outcome.metadata)


def test_identical_inputs_produce_identical_plans_and_request_hashes() -> None:
    artifact = _artifact(
        "raw_llvm",
        "".join(
            f"define i32 @f{index}() {{\n  ret i32 {index}\n}}\n"
            for index in range(500)
        ),
    )

    def run_once() -> dict[str, object]:
        prompts: list[str] = []
        outcome = review_evidence(
            config=_config(),
            full_prompt="y" * 40_000,
            artifacts=[artifact],
            deterministic_summary={"format": "summary-v1", "passed": True},
            policy=ReviewPolicy(
                max_total_tokens=150_000,
                max_request_tokens=18_000,
                max_artifact_tokens=60_000,
                chunk_output_tokens=128,
            ),
            complete=_successful_client(prompts),
        )
        return outcome.metadata

    first = run_once()
    second = run_once()

    assert first["artifacts"] == second["artifacts"]
    first_requests = first["requests"]
    second_requests = second["requests"]
    assert [item["coverage"] for item in first_requests] == [
        item["coverage"] for item in second_requests
    ]
    assert [item["completion"]["request_sha256"] for item in first_requests] == [
        item["completion"]["request_sha256"] for item in second_requests
    ]


def test_unicode_and_oversized_single_function_split_on_safe_bytes() -> None:
    content = "define i32 @huge() { " + ("ää漢字🙂 add i32 1, 2 " * 1800) + "}\n"
    artifact = _artifact("raw_llvm", content)
    prompts: list[str] = []

    outcome = review_evidence(
        config=_config(),
        full_prompt="z" * 30_000,
        artifacts=[artifact],
        deterministic_summary={},
        policy=ReviewPolicy(
            max_total_tokens=180_000,
            max_request_tokens=12_000,
            max_artifact_tokens=100_000,
            chunk_output_tokens=128,
        ),
        complete=_successful_client(prompts),
    )

    assert outcome.metadata["mode"] == "staged"
    artifact_metadata = outcome.metadata["artifacts"][0]
    assert len(artifact_metadata["coverage"]) > 1
    _assert_complete_coverage(artifact, outcome.metadata)


def test_provider_truncation_fails_single_request() -> None:
    def complete(config: LlmConfig, prompt: str) -> LlmResponse:
        del config
        return _response(prompt, "OK\nIncomplete", finish_reason="length")

    with pytest.raises(LlmError, match="finish reason 'length'"):
        review_evidence(
            config=_config(),
            full_prompt="small",
            artifacts=[_artifact("source", "content")],
            deterministic_summary={},
            policy=ReviewPolicy(
                max_total_tokens=10_000,
                max_request_tokens=10_000,
                max_artifact_tokens=10_000,
                chunk_output_tokens=128,
            ),
            complete=complete,
        )


def test_partial_staged_request_failure_names_request_and_stops() -> None:
    calls: list[str] = []

    def complete(config: LlmConfig, prompt: str) -> LlmResponse:
        del config
        calls.append(prompt)
        if len(calls) == 2:
            raise LlmError("endpoint reset")
        return _response(prompt, "REVIEWED\nFirst range checked.")

    artifact_content = "define i32 @f() {\n" + ("  %x = add i32 1, 2\n" * 800) + "}\n"
    artifact = _artifact("raw_llvm", artifact_content)
    with pytest.raises(
        LlmError,
        match="staged review request artifact-0002 failed: endpoint reset",
    ):
        review_evidence(
            config=_config(),
            full_prompt="q" * 30_000,
            artifacts=[artifact],
            deterministic_summary={},
            policy=ReviewPolicy(
                max_total_tokens=100_000,
                max_request_tokens=10_000,
                max_artifact_tokens=50_000,
                chunk_output_tokens=128,
            ),
            complete=complete,
        )
    assert len(calls) == 2
    assert all("Artifact review findings" not in prompt for prompt in calls)


def test_artifact_budget_fails_before_any_request() -> None:
    calls = 0

    def complete(config: LlmConfig, prompt: str) -> LlmResponse:
        nonlocal calls
        del config
        calls += 1
        return _response(prompt, "OK")

    with pytest.raises(ReviewPlanningError, match="max_artifact_tokens"):
        review_evidence(
            config=_config(),
            full_prompt="small",
            artifacts=[_artifact("raw_llvm", "x" * 5000)],
            deterministic_summary={},
            policy=ReviewPolicy(
                max_total_tokens=20_000,
                max_request_tokens=10_000,
                max_artifact_tokens=1000,
                chunk_output_tokens=128,
            ),
            complete=complete,
        )
    assert calls == 0


def test_total_budget_fails_before_any_request() -> None:
    calls = 0

    def complete(config: LlmConfig, prompt: str) -> LlmResponse:
        nonlocal calls
        del config
        calls += 1
        return _response(prompt, "REVIEWED\nChecked.")

    with pytest.raises(ReviewPlanningError, match="max_total_tokens"):
        review_evidence(
            config=_config(),
            full_prompt="x" * 6000,
            artifacts=[_artifact("raw_llvm", "y" * 6000)],
            deterministic_summary={},
            policy=ReviewPolicy(
                max_total_tokens=5000,
                max_request_tokens=4000,
                max_artifact_tokens=10_000,
                chunk_output_tokens=128,
            ),
            complete=complete,
        )
    assert calls == 0


def test_malformed_artifact_response_fails_closed() -> None:
    def complete(config: LlmConfig, prompt: str) -> LlmResponse:
        del config
        return _response(prompt, "Looks fine.")

    with pytest.raises(AuditProtocolError, match="first line must be REVIEWED"):
        review_evidence(
            config=_config(),
            full_prompt="x" * 30_000,
            artifacts=[_artifact("raw_llvm", "y" * 8000)],
            deterministic_summary={},
            policy=ReviewPolicy(
                max_total_tokens=100_000,
                max_request_tokens=10_000,
                max_artifact_tokens=20_000,
                chunk_output_tokens=128,
            ),
            complete=complete,
        )
