"""Atomic publication primitives for verified evidence bundles."""

from __future__ import annotations

import hashlib
import os
import shutil
from collections.abc import Mapping
from pathlib import Path
from typing import Any


def file_entry(
    root: Path,
    path: Path,
    *,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Describe one retained file relative to a bundle root."""
    data = path.read_bytes()
    entry: dict[str, Any] = {
        "path": path.relative_to(root).as_posix(),
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }
    if extra:
        entry.update(extra)
    return entry


def publish_directory(source: Path, destination: Path) -> None:
    """Atomically replace a published bundle directory when possible."""
    backup: Path | None = None
    if destination.exists():
        backup = destination.with_name(destination.name + ".previous")
        if backup.exists():
            shutil.rmtree(backup)
        os.replace(destination, backup)
    try:
        os.replace(source, destination)
    except OSError:
        if backup is not None and backup.exists() and not destination.exists():
            os.replace(backup, destination)
        raise
    if backup is not None:
        shutil.rmtree(backup, ignore_errors=True)
