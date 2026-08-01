"""Tests for LLM configuration and chat completion."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, call, patch

import httpx
import pytest
from openai import APIStatusError

from weave_loupe.llm import (
    LlmConfig,
    LlmError,
    chat_completion,
    load_config,
    normalize_endpoint_identity,
    resolve_endpoint,
)


def _status_error(status_code: int, message: str = "boom") -> APIStatusError:
    request = httpx.Request("POST", "https://example.test/v1/chat/completions")
    response = httpx.Response(status_code, request=request)
    return APIStatusError(message=message, response=response, body=None)


def _ok_response() -> SimpleNamespace:
    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content="OK"),
                finish_reason="stop",
            )
        ]
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


def test_load_config_rejects_invalid_max_attempts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("WEAVE_LLM_ENDPOINT", "https://example.test/v1")
    monkeypatch.setenv("WEAVE_LLM_API_KEY", "secret")
    monkeypatch.setenv("WEAVE_LLM_MAX_ATTEMPTS", "zero")

    with pytest.raises(LlmError, match="must be a positive integer"):
        load_config(model="z-ai/glm-5.2", max_tokens=16)


def test_load_config_preserves_loopback_transport_and_reads_retry_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transport = "http://user:secret@LOCALHOST:8000/v1/?token=hidden#fragment"
    monkeypatch.setenv("WEAVE_LLM_ENDPOINT", transport)
    monkeypatch.setenv("WEAVE_LLM_API_KEY", "secret")
    monkeypatch.setenv("WEAVE_LLM_MAX_ATTEMPTS", "7")

    config = load_config(model="z-ai/glm-5.2", max_tokens=32)

    assert config.endpoint == transport
    assert config.endpoint_identity == "http://localhost:8000/v1"
    assert config.api_key == "secret"
    assert config.model == "z-ai/glm-5.2"
    assert config.max_tokens == 32
    assert config.max_attempts == 7


def test_load_config_rejects_nonloopback_http_by_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("WEAVE_LLM_ENDPOINT", "http://example.test/v1")
    monkeypatch.setenv("WEAVE_LLM_API_KEY", "secret")

    with pytest.raises(LlmError, match="restricted to loopback"):
        load_config(model="model", max_tokens=16)


def test_load_config_accepts_explicit_nonloopback_http_override(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("WEAVE_LLM_ENDPOINT", "http://example.test:8080/v1/")
    monkeypatch.setenv("WEAVE_LLM_API_KEY", "secret")

    config = load_config(
        model="model",
        max_tokens=16,
        allow_unsafe_http=True,
    )

    assert config.endpoint == "http://example.test:8080/v1/"
    assert config.endpoint_identity == "http://example.test:8080/v1"
    assert config.allow_unsafe_http is True


def test_load_config_accepts_environment_nonloopback_http_override(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("WEAVE_LLM_ENDPOINT", "http://example.test/v1")
    monkeypatch.setenv("WEAVE_LLM_API_KEY", "secret")
    monkeypatch.setenv("WEAVE_LLM_ALLOW_UNSAFE_HTTP", "yes")

    config = load_config(model="model", max_tokens=16)

    assert config.endpoint_identity == "http://example.test/v1"
    assert config.allow_unsafe_http is True


def test_load_config_rejects_invalid_unsafe_http_environment_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("WEAVE_LLM_ENDPOINT", "https://example.test/v1")
    monkeypatch.setenv("WEAVE_LLM_API_KEY", "secret")
    monkeypatch.setenv("WEAVE_LLM_ALLOW_UNSAFE_HTTP", "sometimes")

    with pytest.raises(LlmError, match="must be one of"):
        load_config(model="model", max_tokens=16)


@pytest.mark.parametrize(
    ("transport", "identity"),
    [
        ("http://LOCALHOST:80/v1/", "http://localhost/v1"),
        ("http://localhost.:8000/v1/", "http://localhost:8000/v1"),
        ("http://127.42.0.8:8000/v1/", "http://127.42.0.8:8000/v1"),
        ("http://[0:0:0:0:0:0:0:1]:80/v1/", "http://[::1]/v1"),
        ("https://Example.TEST:443/v1/", "https://example.test/v1"),
        ("https://Example.TEST:8443/v1/", "https://example.test:8443/v1"),
    ],
)
def test_endpoint_identity_normalizes_supported_urls(
    transport: str,
    identity: str,
) -> None:
    assert normalize_endpoint_identity(transport) == identity


def test_endpoint_identity_removes_private_url_components() -> None:
    endpoint = normalize_endpoint_identity(
        "https://user:secret@Example.TEST:8443/v1/?token=hidden#fragment"
    )

    assert endpoint == "https://example.test:8443/v1"


def test_endpoint_resolution_records_transport_security() -> None:
    loopback = resolve_endpoint("http://127.0.0.2:8000/v1")
    secure = resolve_endpoint("https://example.test/v1")

    assert loopback.loopback is True
    assert loopback.secure is False
    assert secure.loopback is False
    assert secure.secure is True


def test_endpoint_identity_requires_override_for_nonloopback_http() -> None:
    with pytest.raises(ValueError, match="restricted to loopback"):
        normalize_endpoint_identity("http://example.test/v1")

    assert (
        normalize_endpoint_identity(
            "http://example.test/v1",
            allow_unsafe_http=True,
        )
        == "http://example.test/v1"
    )


@pytest.mark.parametrize(
    "endpoint",
    [
        "ftp://example.test/v1",
        "https:///v1",
        "https://example.test:invalid/v1",
        "https://example.test/v 1",
        "http://[fe80::1%25eth0]/v1",
    ],
)
def test_endpoint_identity_rejects_invalid_urls(endpoint: str) -> None:
    with pytest.raises(ValueError):
        normalize_endpoint_identity(endpoint)


def test_config_repr_hides_transport_credentials_and_api_key() -> None:
    config = LlmConfig(
        endpoint="https://user:transport-secret@example.test/v1?token=hidden",
        api_key="api-secret",
        model="model",
    )

    rendered = repr(config)

    assert "transport-secret" not in rendered
    assert "api-secret" not in rendered
    assert "token=hidden" not in rendered
    assert "https://example.test/v1" in rendered


def test_chat_completion_returns_request_and_provider_metadata() -> None:
    transport = "https://user:secret@Example.TEST:443/v1/?token=hidden#fragment"
    config = LlmConfig(
        endpoint=transport,
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
        base_url=transport,
        timeout=300.0,
    )
    client.chat.completions.create.assert_called_once_with(
        model="z-ai/glm-5.2",
        messages=[{"role": "user", "content": "Say OK"}],
        max_tokens=16,
        temperature=0.0,
    )


def test_request_hash_uses_public_identity_not_transport_secrets() -> None:
    client = MagicMock()
    client.chat.completions.create.return_value = _ok_response()
    first = LlmConfig(
        endpoint="https://user:one@example.test/v1?token=first#one",
        api_key="secret",
        model="model",
        max_tokens=16,
    )
    second = LlmConfig(
        endpoint="https://other:two@EXAMPLE.TEST:443/v1/?token=second#two",
        api_key="secret",
        model="model",
        max_tokens=16,
    )

    with patch("weave_loupe.llm.OpenAI", return_value=client):
        one = chat_completion(first, "prompt")
        two = chat_completion(second, "prompt")

    assert first.endpoint != second.endpoint
    assert first.endpoint_identity == second.endpoint_identity
    assert one.request_sha256 == two.request_sha256


def test_request_hash_changes_with_prompt_or_settings() -> None:
    client = MagicMock()
    client.chat.completions.create.return_value = _ok_response()
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


def test_chat_completion_retries_transient_routing_failure() -> None:
    config = LlmConfig(
        endpoint="https://example.test/v1",
        api_key="secret",
        model="model",
        max_attempts=2,
    )
    client = MagicMock()
    client.chat.completions.create.side_effect = [_status_error(404), _ok_response()]

    with (
        patch("weave_loupe.llm.OpenAI", return_value=client),
        patch("weave_loupe.llm.time.sleep") as sleep,
    ):
        completion = chat_completion(config, "prompt")

    assert completion.content == "OK"
    assert client.chat.completions.create.call_count == 2
    sleep.assert_called_once_with(1.0)


def test_chat_completion_stops_after_retry_limit() -> None:
    config = LlmConfig(
        endpoint="https://example.test/v1",
        api_key="secret",
        model="model",
        max_attempts=3,
    )
    client = MagicMock()
    client.chat.completions.create.side_effect = _status_error(404)

    with (
        patch("weave_loupe.llm.OpenAI", return_value=client),
        patch("weave_loupe.llm.time.sleep") as sleep,
        pytest.raises(LlmError, match="HTTP 404"),
    ):
        chat_completion(config, "prompt")

    assert client.chat.completions.create.call_count == 3
    assert sleep.call_args_list == [call(1.0), call(2.0)]


def test_chat_completion_does_not_retry_permanent_client_error() -> None:
    config = LlmConfig(
        endpoint="https://example.test/v1",
        api_key="secret",
        model="model",
        max_attempts=5,
    )
    client = MagicMock()
    client.chat.completions.create.side_effect = _status_error(400)

    with (
        patch("weave_loupe.llm.OpenAI", return_value=client),
        patch("weave_loupe.llm.time.sleep") as sleep,
        pytest.raises(LlmError, match="HTTP 400"),
    ):
        chat_completion(config, "prompt")

    client.chat.completions.create.assert_called_once()
    sleep.assert_not_called()


def test_chat_completion_errors_do_not_expose_transport_secrets() -> None:
    config = LlmConfig(
        endpoint=(
            "https://private-user:private-password@example.test/v1"
            "?token=private-token#private-fragment"
        ),
        api_key="private-api-key",
        model="model",
        max_attempts=1,
    )
    client = MagicMock()
    client.chat.completions.create.side_effect = _status_error(
        500,
        message="private-token private-password",
    )

    with (
        patch("weave_loupe.llm.OpenAI", return_value=client),
        pytest.raises(LlmError) as captured,
    ):
        chat_completion(config, "prompt")

    message = str(captured.value)
    assert message == "LLM request failed with HTTP 500"
    assert "private" not in message


def test_chat_completion_accepts_missing_optional_attestation() -> None:
    config = LlmConfig(
        endpoint="https://example.test/v1",
        api_key="secret",
        model="z-ai/glm-5.2",
    )
    client = MagicMock()
    client.chat.completions.create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="OK"))]
    )

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
        max_attempts=1,
    )
    client = MagicMock()
    client.chat.completions.create.side_effect = _status_error(500)

    with (
        patch("weave_loupe.llm.OpenAI", return_value=client),
        pytest.raises(LlmError, match="HTTP 500"),
    ):
        chat_completion(config, "prompt")


def test_chat_completion_rejects_nonpositive_attempts() -> None:
    config = LlmConfig(
        endpoint="https://example.test/v1",
        api_key="secret",
        model="z-ai/glm-5.2",
        max_attempts=0,
    )

    with pytest.raises(LlmError, match="max_attempts must be positive"):
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
