"""Tests for LLM configuration and chat completion."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import httpx
import pytest
from openai import APIStatusError

from weave_loupe.llm import (
    LlmConfig,
    LlmError,
    chat_completion,
    load_config,
    normalize_endpoint_identity,
)


def test_load_config_requires_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("WEAVE_LLM_ENDPOINT", raising=False)
    monkeypatch.setenv("WEAVE_LLM_API_KEY", "secret")
    with pytest.raises(LlmError, match="WEAVE_LLM_ENDPOINT"):
        load_config(model="z-ai/glm-5.2", max_tokens=16)


def test_load_config_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WEAVE_LLM_ENDPOINT", "https://example.test/v1")
    monkeypatch.delenv("WEAVE_LLM_API_KEY", raising=False)
    with pytest.raises(LlmError, match="WEAVE_LLM_API_KEY"):
        load_config(model="z-ai/glm-5.2", max_tokens=16)


def test_load_config_rejects_nonpositive_max_tokens(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("WEAVE_LLM_ENDPOINT", "https://example.test/v1")
    monkeypatch.setenv("WEAVE_LLM_API_KEY", "secret")
    with pytest.raises(LlmError, match="max_tokens must be positive"):
        load_config(model="z-ai/glm-5.2", max_tokens=0)


def test_load_config_upgrades_http_to_https(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("WEAVE_LLM_ENDPOINT", "http://example.test/v1/")
    monkeypatch.setenv("WEAVE_LLM_API_KEY", "secret")
    config = load_config(model="z-ai/glm-5.2", max_tokens=32)
    assert config.endpoint == "https://example.test/v1"
    assert config.api_key == "secret"
    assert config.model == "z-ai/glm-5.2"
    assert config.max_tokens == 32


def test_endpoint_identity_removes_private_url_components() -> None:
    endpoint = normalize_endpoint_identity(
        "https://user:secret@Example.TEST:8443/v1/?token=hidden#fragment"
    )

    assert endpoint == "https://example.test:8443/v1"


def test_endpoint_identity_rejects_non_http_transport() -> None:
    with pytest.raises(ValueError, match="HTTPS"):
        normalize_endpoint_identity("ftp://example.test/v1")


def test_chat_completion_returns_request_and_provider_metadata() -> None:
    config = LlmConfig(
        endpoint="https://example.test/v1",
        api_key="secret",
        model="z-ai/glm-5.2",
        max_tokens=16,
    )
    response = SimpleNamespace(
        id="chatcmpl-test",
        model="z-ai/glm-5.2-20260701",
        system_fingerprint="fp_test",
        created=1785236400,
        usage=SimpleNamespace(
            prompt_tokens=12,
            completion_tokens=3,
            total_tokens=15,
        ),
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content="OK"),
                finish_reason="stop",
            )
        ],
    )
    client = MagicMock()
    client.chat.completions.create.return_value = response

    with patch("weave_loupe.llm.OpenAI", return_value=client) as openai_cls:
        completion = chat_completion(config, "Say OK")

    assert completion.content == "OK"
    assert completion.requested_model == "z-ai/glm-5.2"
    assert completion.endpoint == "https://example.test/v1"
    assert completion.max_tokens == 16
    assert completion.temperature == 0.0
    assert len(completion.prompt_sha256) == 64
    assert len(completion.request_sha256) == 64
    assert completion.prompt_sha256 != completion.request_sha256
    assert completion.provider_model == "z-ai/glm-5.2-20260701"
    assert completion.response_id == "chatcmpl-test"
    assert completion.system_fingerprint == "fp_test"
    assert completion.finish_reason == "stop"
    assert completion.created == 1785236400
    assert completion.prompt_tokens == 12
    assert completion.completion_tokens == 3
    assert completion.total_tokens == 15
    assert completion.metadata() == {
        "requested_model": "z-ai/glm-5.2",
        "endpoint": "https://example.test/v1",
        "max_tokens": 16,
        "temperature": 0.0,
        "prompt_sha256": completion.prompt_sha256,
        "request_sha256": completion.request_sha256,
        "provider_model": "z-ai/glm-5.2-20260701",
        "response_id": "chatcmpl-test",
        "system_fingerprint": "fp_test",
        "finish_reason": "stop",
        "created": 1785236400,
        "prompt_tokens": 12,
        "completion_tokens": 3,
        "total_tokens": 15,
    }
    openai_cls.assert_called_once_with(
        api_key="secret",
        base_url="https://example.test/v1",
        timeout=300.0,
    )
    client.chat.completions.create.assert_called_once_with(
        model="z-ai/glm-5.2",
        messages=[{"role": "user", "content": "Say OK"}],
        max_tokens=16,
        temperature=0.0,
    )


def test_request_hash_changes_with_prompt_or_settings() -> None:
    response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content="OK"),
                finish_reason="stop",
            )
        ]
    )
    client = MagicMock()
    client.chat.completions.create.return_value = response
    first = LlmConfig(
        endpoint="https://example.test/v1",
        api_key="secret",
        model="model",
        max_tokens=16,
    )
    second = LlmConfig(
        endpoint="https://example.test/v1",
        api_key="secret",
        model="model",
        max_tokens=32,
    )

    with patch("weave_loupe.llm.OpenAI", return_value=client):
        one = chat_completion(first, "prompt")
        other_prompt = chat_completion(first, "different")
        other_limit = chat_completion(second, "prompt")

    assert one.prompt_sha256 != other_prompt.prompt_sha256
    assert one.request_sha256 != other_prompt.request_sha256
    assert one.prompt_sha256 == other_limit.prompt_sha256
    assert one.request_sha256 != other_limit.request_sha256


def test_chat_completion_accepts_missing_optional_attestation() -> None:
    config = LlmConfig(
        endpoint="https://example.test/v1",
        api_key="secret",
        model="z-ai/glm-5.2",
    )
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="OK"))]
    )
    client = MagicMock()
    client.chat.completions.create.return_value = response

    with patch("weave_loupe.llm.OpenAI", return_value=client):
        completion = chat_completion(config, "prompt")

    assert completion.provider_model is None
    assert completion.response_id is None
    assert completion.system_fingerprint is None
    assert completion.finish_reason is None
    assert completion.created is None
    assert completion.prompt_tokens is None
    assert completion.completion_tokens is None
    assert completion.total_tokens is None


def test_chat_completion_wraps_api_error() -> None:
    config = LlmConfig(
        endpoint="https://example.test/v1",
        api_key="secret",
        model="z-ai/glm-5.2",
    )
    request = httpx.Request("POST", "https://example.test/v1/chat/completions")
    response = httpx.Response(500, request=request)
    api_error = APIStatusError(
        message="boom",
        response=response,
        body=None,
    )
    client = MagicMock()
    client.chat.completions.create.side_effect = api_error

    with (
        patch("weave_loupe.llm.OpenAI", return_value=client),
        pytest.raises(LlmError, match="HTTP 500"),
    ):
        chat_completion(config, "prompt")


def test_chat_completion_rejects_empty_content() -> None:
    config = LlmConfig(
        endpoint="https://example.test/v1",
        api_key="secret",
        model="z-ai/glm-5.2",
    )
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=""))]
    )
    client = MagicMock()
    client.chat.completions.create.return_value = response

    with (
        patch("weave_loupe.llm.OpenAI", return_value=client),
        pytest.raises(LlmError, match="empty content"),
    ):
        chat_completion(config, "prompt")
