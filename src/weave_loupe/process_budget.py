"""Host-aware process-count budgets for POSIX resource limits."""

from __future__ import annotations

import os
from dataclasses import replace
from pathlib import Path

from weave_loupe.bounded_process import ProcessLimits


def with_user_process_baseline(limits: ProcessLimits) -> ProcessLimits:
    """Convert an additional process budget to an effective UID-wide ceiling."""
    baseline = current_user_process_count()
    if baseline is None:
        return limits
    return replace(limits, process_count=baseline + limits.process_count)


def current_user_process_count() -> int | None:
    """Count Linux tasks whose real UID matches the current process."""
    proc = Path("/proc")
    if os.name != "posix" or not proc.is_dir() or not hasattr(os, "getuid"):
        return None
    uid = os.getuid()
    count = 0
    try:
        entries = tuple(proc.iterdir())
    except OSError:
        return None
    for entry in entries:
        if not entry.name.isdigit():
            continue
        try:
            status = (entry / "status").read_text(
                encoding="utf-8",
                errors="replace",
            )
        except OSError:
            continue
        if not _status_matches_uid(status, uid):
            continue
        try:
            count += sum(
                1 for task in (entry / "task").iterdir() if task.name.isdigit()
            )
        except OSError:
            continue
    return count


def _status_matches_uid(status: str, uid: int) -> bool:
    for line in status.splitlines():
        if not line.startswith("Uid:"):
            continue
        fields = line.split()
        return len(fields) >= 2 and fields[1].isdigit() and int(fields[1]) == uid
    return False
