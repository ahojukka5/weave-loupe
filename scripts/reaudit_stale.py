#!/usr/bin/env python3
"""Refresh stale positive and expected-failure audit reports."""

from __future__ import annotations

from typing import Any

from weave_loupe import scheduled_audit as _scheduled_audit


def __getattr__(name: str) -> Any:
    """Preserve compatibility for focused tests importing script internals."""
    return getattr(_scheduled_audit, name)


if __name__ == "__main__":
    raise SystemExit(_scheduled_audit.main())
