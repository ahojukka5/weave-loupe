"""OpenAI-compatible chat client for Weave LLM endpoints."""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass
from urllib.parse import urlsplit, urlunsplit

from openai import (
    APIConnectionError,
    APIError,
    APIStatusError,
    APITimeoutError,
    OpenAI,
    OpenAIError,
)

_DEFAULT_MAX_ATTEMPTS = 5
_RETRYABLE_STATUS_CODES = frozenset({404, 408, 409, 425, 429, 500, 502, 503, 504})


class LlmError(RuntimeError):
    """Raised when the LLM endpoint is misconfigured or fails."""


@dataclass(frozen=True)
class LlmConfig:
    endpoint: str
    api_key: str
    model: str
    max_tokens: int = 4096
    temperature: float = 0.0
    max_attempts: int = _DEFAULT_MAX_ATTEMPTS


@dataclass(frozen=True)
class LlmResponse:
    """Completion content plus request and provider provenance fields."""

    content: str
    requested_model: str
    endpoint: str
    max_tokens: int
    temperature: float
    prompt_sha256: str
    request_sha256: str
    provider_model: str | None
    response_id: str | None
    system_fingerprint: str | None
    finish_reason: str | None
    created: int | None
    prompt_tokens: int | None
    completion_tokens: int | None
    total_tokens: int | None

    def metadata(self) -> dict[str, str | int | float | None]:
        """Return stable report metadata for this request and completion."""
        return {
            "requested_model": self.requested_model,
            "endpoint": self.endpoint,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "prompt_sha256": self.prompt_sha256,
            "request_sha256": self.request_sha256,
            "provider_model": self.provider_model,
            "response_id": self.response_id,
            "system_fingerprint": self.system_fingerprint,
            "finish_reason": self.finish_reason,
            "created": self.created,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
        }


def normalize_endpoint_identity(endpoint: str) -> str:
    """Return a public, stable endpoint identity without credentials or queries."""
    value = endpoint.strip().rstrip("/")
    if not value:
        raise ValueError("LLM endpoint is empty")
    parsed = urlsplit(value)
    scheme = parsed.scheme.lower()
    if scheme == "http":
        scheme = "https"
    if scheme != "https":
        raise ValueError("LLM endpoint must use HTTPS")
    hostname = parsed.hostname
    if not hostname:
        raise ValueError("LLM endpoint does not contain a hostname")
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError("LLM endpoint contains an invalid port") from exc
    host = hostname.lower()
    if ":" in host:
        host = f"[{host}]"
    netloc = host if port is None else f"{host}:{port}"
    path = parsed.path.rstrip("/")
    return urlunsplit((scheme, netloc, path, "", ""))


def load_config(*, model: str, max_tokens: int) -> LlmConfig:
    endpoint = os.environ.get("WEAVE_LLM_ENDPOINT", "")
    api_key = os.environ.get("WEAVE_LLM_API_KEY", "")
    if not endpoint:
        raise LlmError("WEAVE_LLM_ENDPOINT is not set")
    if not api_key:
        raise LlmError("WEAVE_LLM_API_KEY is not set")
    if max_tokens <= 0:
        raise LlmError("max_tokens must be positive")
    max_attempts = _positive_environment_integer(
        "WEAVE_LLM_MAX_ATTEMPTS",
        default=_DEFAULT_MAX_ATTEMPTS,
    )
    try:
        endpoint = normalize_endpoint_identity(endpoint)
    except ValueError as exc:
        raise LlmError(str(exc)) from exc
    return LlmConfig(
        endpoint=endpoint,
        api_key=api_key,
        model=model,
        max_tokens=max_tokens,
        max_attempts=max_attempts,
    )


def chat_completion(config: LlmConfig, prompt: str) -> LlmResponse:
    if config.max_attempts <= 0:
        raise LlmError("max_attempts must be positive")
    request = _request_metadata(config, prompt)
    client = OpenAI(
        api_key=config.api_key,
        base_url=config.endpoint,
        timeout=300.0,
    )
    response = _create_completion(client, config, prompt)

    if not response.choices:
        raise LlmError(f"LLM response had no choices: {response}")

    choice = response.choices[0]
    content = choice.message.content
    if not content:
        raise LlmError(f"LLM response had empty content: {response}")
    usage = getattr(response, "usage", None)
    return LlmResponse(
        content=content,
        requested_model=config.model,
        endpoint=config.endpoint,
        max_tokens=config.max_tokens,
        temperature=config.temperature,
        prompt_sha256=request["prompt_sha256"],
        request_sha256=request["request_sha256"],
        provider_model=_optional_string(getattr(response, "model", None)),
        response_id=_optional_string(getattr(response, "id", None)),
        system_fingerprint=_optional_string(
            getattr(response, "system_fingerprint", None)
        ),
        finish_reason=_optional_string(getattr(choice, "finish_reason", None)),
        created=_optional_int(getattr(response, "created", None)),
        prompt_tokens=_optional_int(getattr(usage, "prompt_tokens", None)),
        completion_tokens=_optional_int(getattr(usage, "completion_tokens", None)),
        total_tokens=_optional_int(getattr(usage, "total_tokens", None)),
    )


def _create_completion(client: OpenAI, config: LlmConfig, prompt: str):
    for attempt in range(1, config.max_attempts + 1):
        try:
            return client.chat.completions.create(
                model=config.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=config.max_tokens,
                temperature=config.temperature,
            )
        except APIStatusError as exc:
            if (
                exc.status_code not in _RETRYABLE_STATUS_CODES
                or attempt == config.max_attempts
            ):
                raise LlmError(
                    f"LLM request failed with HTTP {exc.status_code}: {exc.message}"
                ) from exc
            time.sleep(_retry_delay_seconds(attempt))
        except (APIConnectionError, APITimeoutError) as exc:
            if attempt == config.max_attempts:
                raise LlmError(f"LLM request failed: {exc}") from exc
            time.sleep(_retry_delay_seconds(attempt))
        except (APIError, OpenAIError) as exc:
            raise LlmError(f"LLM request failed: {exc}") from exc
    raise AssertionError("unreachable LLM retry loop")


def _retry_delay_seconds(attempt: int) -> float:
    return float(min(2 ** (attempt - 1), 8))


def _positive_environment_integer(name: str, *, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise LlmError(f"{name} must be a positive integer") from exc
    if value <= 0:
        raise LlmError(f"{name} must be a positive integer")
    return value


def _request_metadata(config: LlmConfig, prompt: str) -> dict[str, str]:
    prompt_sha256 = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    envelope = {
        "endpoint": config.endpoint,
        "max_tokens": config.max_tokens,
        "messages": [{"content": prompt, "role": "user"}],
        "model": config.model,
        "temperature": config.temperature,
    }
    canonical = json.dumps(
        envelope,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    return {
        "prompt_sha256": prompt_sha256,
        "request_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
    }


def _optional_string(value: object) -> str | None:
    return value if isinstance(value, str) and value else None


def _optional_int(value: object) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None
