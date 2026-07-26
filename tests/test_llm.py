"""Tests for LLM configuration and chat completion."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import httpx
import pytest
from openai import APIStatusError

from weave_loupe.llm import LlmConfig, LlmError, chat_completion, load_config


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


def test_chat_completion_returns_message_content() -> None:
    config = LlmConfig(
        endpoint="https://example.test/v1",
        api_key="secret",
        model="z-ai/glm-5.2",
        max_tokens=16,
    )
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="OK"))]
    )
    client = MagicMock()
    client.chat.completions.create.return_value = response

    with patch("weave_loupe.llm.OpenAI", return_value=client) as openai_cls:
        content = chat_completion(config, "Say OK")

    assert content == "OK"
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
