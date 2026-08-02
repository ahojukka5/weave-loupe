"""Tests for bounded provider rate-limit retry delays."""

from types import SimpleNamespace

from weave_loupe import llm


def test_default_retry_window_covers_minute_scale_limits() -> None:
    assert llm.DEFAULT_RETRY_ATTEMPTS == 7
    assert llm.DEFAULT_RETRY_MAX_SECONDS == 60.0


def test_retry_delay_honors_numeric_retry_after() -> None:
    error = SimpleNamespace(
        status_code=429,
        response=SimpleNamespace(headers={"retry-after": "45"}),
    )

    assert llm._retry_delay(error, 2.0, 60.0) == 45.0


def test_retry_delay_caps_provider_value() -> None:
    error = SimpleNamespace(
        status_code=429,
        response=SimpleNamespace(headers={"retry-after": "120"}),
    )

    assert llm._retry_delay(error, 2.0, 60.0) == 60.0


def test_retry_delay_uses_fallback_for_malformed_header() -> None:
    error = SimpleNamespace(
        status_code=429,
        response=SimpleNamespace(headers={"retry-after": "later"}),
    )

    assert llm._retry_delay(error, 8.0, 60.0) == 8.0
