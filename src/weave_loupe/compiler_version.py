"""Resolve a reproducible weavec release or development build identity."""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

_VERSION_LINE = re.compile(r"^(?:weavec\s+)?(v?\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?)$")


@dataclass(frozen=True)
class CompilerVersion:
    """Normalized compiler identity recorded in an audit report."""

    display: str
    base: str
    git_sha: str | None
    development: bool
    source: str


def identify_weavec(binary: Path) -> CompilerVersion:
    """Return the strongest available identity for a compiler executable."""
    command = _command_version(binary)
    if command is not None:
        normalized = _normalize(command)
        return CompilerVersion(
            display=f"weavec {normalized}",
            base=normalized.split("+", 1)[0],
            git_sha=_git_sha_from_version(normalized),
            development="+git." in normalized or normalized.endswith(".dirty"),
            source="command",
        )

    root = _git_root(binary.parent)
    version_file = _find_version_file(binary, root)
    base = _read_base_version(version_file) or "v0.0.0"
    if not base.startswith("v"):
        base = "v" + base

    sha = _git(root, "rev-parse", "--short=12", "HEAD") if root else None
    exact = _git(root, "describe", "--tags", "--exact-match", "HEAD") if root else None
    dirty = bool(root and _git(root, "status", "--porcelain", "--untracked-files=no"))
    if exact == base and not dirty:
        version = base
        development = False
    elif sha:
        version = f"{base}+git.{sha}" + (".dirty" if dirty else "")
        development = True
    else:
        version = base
        development = False

    return CompilerVersion(
        display=f"weavec {version}",
        base=base,
        git_sha=sha,
        development=development,
        source="repository" if root else "version-file",
    )


def _command_version(binary: Path) -> str | None:
    try:
        completed = subprocess.run(
            [str(binary), "--version"],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    output = (completed.stdout or completed.stderr).strip().splitlines()
    if completed.returncode != 0 or not output:
        return None
    line = output[0].strip()
    return line if _VERSION_LINE.fullmatch(line) else None


def _normalize(value: str) -> str:
    version = value.removeprefix("weavec ").strip()
    return version if version.startswith("v") else "v" + version


def _git_sha_from_version(version: str) -> str | None:
    marker = "+git."
    if marker not in version:
        return None
    return version.split(marker, 1)[1].split(".", 1)[0]


def _git_root(directory: Path) -> Path | None:
    root = _git(directory, "rev-parse", "--show-toplevel")
    return Path(root) if root else None


def _git(directory: Path | None, *args: str) -> str | None:
    if directory is None:
        return None
    try:
        completed = subprocess.run(
            ["git", "-C", str(directory), *args],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return completed.stdout.strip() if completed.returncode == 0 else None


def _find_version_file(binary: Path, root: Path | None) -> Path | None:
    candidates: list[Path] = []
    if root is not None:
        candidates.append(root / "VERSION")
    current = binary.resolve().parent
    for _ in range(5):
        candidates.append(current / "VERSION")
        if current.parent == current:
            break
        current = current.parent
    return next((candidate for candidate in candidates if candidate.is_file()), None)


def _read_base_version(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        value = path.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    return value or None
