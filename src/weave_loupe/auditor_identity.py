"""Content-addressed identity for the audit implementation itself."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

AUDITOR_IDENTITY_FORMAT = "weave-loupe-auditor-identity-v1"


@dataclass(frozen=True)
class AuditorFile:
    """One file contributing to the audit implementation fingerprint."""

    path: str
    sha256: str


@dataclass(frozen=True)
class AuditorIdentity:
    """Stable content identity independent of Git history and merge strategy."""

    format: str
    sha256: str
    files: tuple[AuditorFile, ...]

    def metadata(self) -> dict[str, Any]:
        """Return a JSON-ready representation for reports and workflow evidence."""
        return {
            "format": self.format,
            "sha256": self.sha256,
            "files": [
                {"path": item.path, "sha256": item.sha256} for item in self.files
            ],
        }


def identify_auditor(anchor: Path | None = None) -> AuditorIdentity:
    """Hash every file that can change audit decisions or report semantics."""
    resolved = (anchor or Path(__file__)).resolve()
    root = _source_root(resolved)
    if root is None:
        package = resolved.parent
        paths = sorted(package.rglob("*.py"))
        relative_to = package.parent
    else:
        package = root / "src" / "weave_loupe"
        paths = sorted(package.rglob("*.py"))
        paths.extend(
            path
            for path in (
                root / "scripts" / "audit_pr.py",
                root / "scripts" / "reaudit_stale.py",
                root / "pyproject.toml",
                root / "uv.lock",
            )
            if path.is_file()
        )
        paths = sorted(set(paths))
        relative_to = root

    digest = hashlib.sha256()
    files: list[AuditorFile] = []
    for path in paths:
        relative = path.relative_to(relative_to).as_posix()
        content = path.read_bytes()
        item_digest = hashlib.sha256(content).hexdigest()
        files.append(AuditorFile(path=relative, sha256=item_digest))
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(content)
        digest.update(b"\0")

    return AuditorIdentity(
        format=AUDITOR_IDENTITY_FORMAT,
        sha256=digest.hexdigest(),
        files=tuple(files),
    )


def sha256_file(path: Path) -> str:
    """Hash one file without loading arbitrarily large inputs into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _source_root(anchor: Path) -> Path | None:
    start = anchor if anchor.is_dir() else anchor.parent
    for candidate in (start, *start.parents):
        if (candidate / "pyproject.toml").is_file() and (
            candidate / "src" / "weave_loupe"
        ).is_dir():
            return candidate
    return None
