"""OpenAI-compatible chat client for Weave LLM endpoints."""

from __future__ import annotations

import os
from dataclasses import dataclass

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


def load_config(*, model: str, max_tokens: int) -> LlmConfig:
    endpoint = os.environ.get("WEAVE_LLM_ENDPOINT", "").rstrip("/")
    api_key = os.environ.get("WEAVE_LLM_API_KEY", "")
    if not endpoint:
        raise LlmError("WEAVE_LLM_ENDPOINT is not set")
    if not api_key:
        raise LlmError("WEAVE_LLM_API_KEY is not set")
    if endpoint.startswith("http://"):
        # NVIDIA Integrate and similar hosts reject or hang on plain HTTP.
        endpoint = "https://" + endpoint.removeprefix("http://")
    return LlmConfig(
        endpoint=endpoint,
        api_key=api_key,
        model=model,
        max_tokens=max_tokens,
    )


def chat_completion(config: LlmConfig, prompt: str) -> str:
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
    return content
