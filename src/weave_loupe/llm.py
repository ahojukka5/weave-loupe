"""OpenAI-compatible chat client for Weave LLM endpoints."""

from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import urlsplit, urlunsplit

from openai import APIError, APIStatusError, OpenAI, OpenAIError


class LlmError(RuntimeError):
    """Raised when the LLM endpoint is misconfigured or fails."""


@dataclass(frozen=True)
class LlmConfig:
    endpoint: str
    api_key: str
    model: str
    max_tokens: int = 4096
    temperature: float = 0.0


@dataclass(frozen=True)
class LlmResponse:
    """Completion content plus provider-returned provenance fields."""

    content: str
    requested_model: str
    endpoint: str
    provider_model: str | None
    response_id: str | None
    system_fingerprint: str | None

    def metadata(self) -> dict[str, str | None]:
        """Return the stable report metadata for this completion."""
        return {
            "requested_model": self.requested_model,
            "endpoint": self.endpoint,
            "provider_model": self.provider_model,
            "response_id": self.response_id,
            "system_fingerprint": self.system_fingerprint,
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
    try:
        endpoint = normalize_endpoint_identity(endpoint)
    except ValueError as exc:
        raise LlmError(str(exc)) from exc
    return LlmConfig(
        endpoint=endpoint,
        api_key=api_key,
        model=model,
        max_tokens=max_tokens,
    )


def chat_completion(config: LlmConfig, prompt: str) -> LlmResponse:
    client = OpenAI(
        api_key=config.api_key,
        base_url=config.endpoint,
        timeout=300.0,
    )
    try:
        response = client.chat.completions.create(
            model=config.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=config.max_tokens,
            temperature=config.temperature,
        )
    except APIStatusError as exc:
        raise LlmError(
            f"LLM request failed with HTTP {exc.status_code}: {exc.message}"
        ) from exc
    except (APIError, OpenAIError) as exc:
        raise LlmError(f"LLM request failed: {exc}") from exc

    if not response.choices:
        raise LlmError(f"LLM response had no choices: {response}")

    content = response.choices[0].message.content
    if not content:
        raise LlmError(f"LLM response had empty content: {response}")
    return LlmResponse(
        content=content,
        requested_model=config.model,
        endpoint=config.endpoint,
        provider_model=_optional_string(getattr(response, "model", None)),
        response_id=_optional_string(getattr(response, "id", None)),
        system_fingerprint=_optional_string(
            getattr(response, "system_fingerprint", None)
        ),
    )


def _optional_string(value: object) -> str | None:
    return value if isinstance(value, str) and value else None
