"""OpenAI-compatible chat client for Weave LLM endpoints."""

from __future__ import annotations

import hashlib
import ipaddress
import json
import math
import os
import time
from dataclasses import dataclass, field
from urllib.parse import urlsplit, urlunsplit

from openai import (
    APIConnectionError,
    APIError,
    APIStatusError,
    APITimeoutError,
    OpenAI,
    OpenAIError,
)
from openai.types.chat import ChatCompletion

DEFAULT_RETRY_ATTEMPTS = 7
DEFAULT_RETRY_MAX_SECONDS = 60.0
_RETRYABLE_STATUS_CODES = frozenset({404, 408, 409, 425, 429, 500, 502, 503, 504})
_TRUE_ENVIRONMENT_VALUES = frozenset({"1", "true", "yes", "on"})
_FALSE_ENVIRONMENT_VALUES = frozenset({"0", "false", "no", "off"})


class LlmError(RuntimeError):
    """Raised when the LLM endpoint is misconfigured or fails."""


@dataclass(frozen=True)
class Endpoint:
    """Private connection URL plus its sanitized public attestation identity."""

    transport: str = field(repr=False)
    identity: str
    secure: bool
    loopback: bool


@dataclass(frozen=True)
class LlmConfig:
    endpoint: str = field(repr=False)
    api_key: str = field(repr=False)
    model: str
    max_tokens: int = 4096
    temperature: float = 0.0
    max_attempts: int = DEFAULT_RETRY_ATTEMPTS
    allow_unsafe_http: bool = False
    endpoint_identity: str = field(init=False)

    def __post_init__(self) -> None:
        """Validate the transport and derive the public endpoint identity."""
        resolved = resolve_endpoint(
            self.endpoint,
            allow_unsafe_http=self.allow_unsafe_http,
        )
        object.__setattr__(self, "endpoint", resolved.transport)
        object.__setattr__(self, "endpoint_identity", resolved.identity)


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


def resolve_endpoint(
    endpoint: str,
    *,
    allow_unsafe_http: bool = False,
) -> Endpoint:
    """Validate a connection URL and derive its secret-free public identity."""
    value = endpoint.strip()
    if not value:
        raise ValueError("LLM endpoint is empty")
    if any(character.isspace() or ord(character) < 32 for character in value):
        raise ValueError("LLM endpoint contains whitespace or control characters")
    try:
        parsed = urlsplit(value)
    except ValueError:
        raise ValueError("LLM endpoint is invalid") from None

    scheme = parsed.scheme.lower()
    if scheme not in {"http", "https"}:
        raise ValueError("LLM endpoint must use HTTP or HTTPS")
    hostname = parsed.hostname
    if not hostname:
        raise ValueError("LLM endpoint does not contain a hostname")
    try:
        port = parsed.port
    except ValueError:
        raise ValueError("LLM endpoint contains an invalid port") from None

    host = _normalize_hostname(hostname)
    loopback = _is_loopback_hostname(host)
    if scheme == "http" and not loopback and not allow_unsafe_http:
        raise ValueError(
            "plain HTTP LLM endpoints are restricted to loopback hosts; "
            "pass --allow-unsafe-http or set WEAVE_LLM_ALLOW_UNSAFE_HTTP=1 "
            "to override"
        )

    default_port = 80 if scheme == "http" else 443
    public_port = None if port in {None, default_port} else port
    public_host = f"[{host}]" if ":" in host else host
    netloc = public_host if public_port is None else f"{public_host}:{public_port}"
    path = parsed.path.rstrip("/")
    identity = urlunsplit((scheme, netloc, path, "", ""))
    return Endpoint(
        transport=value,
        identity=identity,
        secure=scheme == "https",
        loopback=loopback,
    )


def normalize_endpoint_identity(
    endpoint: str,
    *,
    allow_unsafe_http: bool = False,
) -> str:
    """Return a stable endpoint identity without credentials, queries, or fragments."""
    return resolve_endpoint(
        endpoint,
        allow_unsafe_http=allow_unsafe_http,
    ).identity


def resolve_unsafe_http_policy(override: bool | None) -> bool:
    """Resolve an explicit override before consulting the shared environment flag."""
    if override is not None:
        return override
    return _boolean_environment("WEAVE_LLM_ALLOW_UNSAFE_HTTP", default=False)


def load_config(
    *,
    model: str,
    max_tokens: int,
    allow_unsafe_http: bool | None = None,
) -> LlmConfig:
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
        default=DEFAULT_RETRY_ATTEMPTS,
    )
    unsafe_http = resolve_unsafe_http_policy(allow_unsafe_http)
    try:
        return LlmConfig(
            endpoint=endpoint,
            api_key=api_key,
            model=model,
            max_tokens=max_tokens,
            max_attempts=max_attempts,
            allow_unsafe_http=unsafe_http,
        )
    except ValueError as exc:
        raise LlmError(str(exc)) from None


def chat_completion(config: LlmConfig, prompt: str) -> LlmResponse:
    if config.max_attempts <= 0:
        raise LlmError("max_attempts must be positive")
    request = _request_metadata(config, prompt)
    try:
        client = OpenAI(
            api_key=config.api_key,
            base_url=config.endpoint,
            timeout=300.0,
        )
    except (OpenAIError, TypeError, ValueError):
        raise LlmError(
            f"LLM client configuration failed for {config.endpoint_identity}"
        ) from None
    response = _create_completion(client, config, prompt)

    if not response.choices:
        raise LlmError("LLM response had no choices")

    choice = response.choices[0]
    content = choice.message.content
    if not content:
        raise LlmError("LLM response had empty content")
    usage = getattr(response, "usage", None)
    return LlmResponse(
        content=content,
        requested_model=config.model,
        endpoint=config.endpoint_identity,
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


def _create_completion(
    client: OpenAI,
    config: LlmConfig,
    prompt: str,
) -> ChatCompletion:
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
                    f"LLM request failed with HTTP {exc.status_code}"
                ) from None
            fallback = _retry_delay_seconds(attempt)
            time.sleep(_retry_delay(exc, fallback, DEFAULT_RETRY_MAX_SECONDS))
        except (APIConnectionError, APITimeoutError):
            if attempt == config.max_attempts:
                raise LlmError(
                    f"LLM request could not reach {config.endpoint_identity}"
                ) from None
            time.sleep(min(_retry_delay_seconds(attempt), DEFAULT_RETRY_MAX_SECONDS))
        except (APIError, OpenAIError) as exc:
            raise LlmError(f"LLM request failed ({type(exc).__name__})") from None
    raise AssertionError("unreachable LLM retry loop")


def _normalize_hostname(hostname: str) -> str:
    host = hostname.rstrip(".").lower()
    if not host:
        raise ValueError("LLM endpoint does not contain a hostname")
    if "%" in host:
        raise ValueError("LLM endpoint contains an unsupported IPv6 zone identifier")
    try:
        return ipaddress.ip_address(host).compressed
    except ValueError:
        try:
            return host.encode("idna").decode("ascii")
        except UnicodeError:
            raise ValueError("LLM endpoint contains an invalid hostname") from None


def _is_loopback_hostname(hostname: str) -> bool:
    if hostname == "localhost":
        return True
    try:
        return ipaddress.ip_address(hostname).is_loopback
    except ValueError:
        return False


def _retry_delay(error: object, fallback_seconds: float, max_seconds: float) -> float:
    fallback = min(max(float(fallback_seconds), 0.0), max_seconds)
    response = getattr(error, "response", None)
    headers = getattr(response, "headers", None)
    if headers is None:
        return fallback
    try:
        raw_value = headers.get("retry-after")
    except AttributeError:
        return fallback
    try:
        retry_after = float(raw_value)
    except (TypeError, ValueError):
        return fallback
    if retry_after < 0.0 or not math.isfinite(retry_after):
        return fallback
    return min(retry_after, max_seconds)


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


def _boolean_environment(name: str, *, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    value = raw.strip().lower()
    if value in _TRUE_ENVIRONMENT_VALUES:
        return True
    if value in _FALSE_ENVIRONMENT_VALUES:
        return False
    raise LlmError(f"{name} must be one of: 1, 0, true, false, yes, no, on, off")


def _request_metadata(config: LlmConfig, prompt: str) -> dict[str, str]:
    prompt_sha256 = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    envelope = {
        "endpoint": config.endpoint_identity,
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
