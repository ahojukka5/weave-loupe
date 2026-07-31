"""Tests for host-aware process-count budgets."""

from __future__ import annotations

from unittest.mock import patch

from weave_loupe.bounded_process import ProcessLimits
from weave_loupe.process_budget import with_user_process_baseline


def _limits(process_count: int = 64) -> ProcessLimits:
    return ProcessLimits(
        timeout_seconds=5.0,
        output_bytes=1024,
        excerpt_bytes=256,
        cpu_seconds=6.0,
        address_space_bytes=512 * 1024 * 1024,
        file_size_bytes=64 * 1024 * 1024,
        process_count=process_count,
    )


def test_process_budget_adds_existing_uid_processes() -> None:
    with patch(
        "weave_loupe.process_budget.current_user_process_count",
        return_value=37,
    ):
        effective = with_user_process_baseline(_limits(64))

    assert effective.process_count == 101


def test_process_budget_preserves_limit_without_baseline() -> None:
    configured = _limits(64)
    with patch(
        "weave_loupe.process_budget.current_user_process_count",
        return_value=None,
    ):
        effective = with_user_process_baseline(configured)

    assert effective == configured
