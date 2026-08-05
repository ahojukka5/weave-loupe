"""Validated compiler-evidence bundle model."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from weave_loupe.compiler.capabilities import (
    CompilerCapabilityError,
    capability_identity_from_document,
)


class BundleError(RuntimeError):
    """Raised when a bundle is invalid or cannot be produced."""


@dataclass(frozen=True)
class Bundle:
    """Validated bundle directory and manifest."""

    root: Path
    manifest: Mapping[str, Any]

    @property
    def sources(self) -> tuple[Mapping[str, Any], ...]:
        raw = self.manifest.get("sources", [])
        if not isinstance(raw, list):
            raise BundleError("bundle sources must be a list")
        return tuple(cast(Mapping[str, Any], item) for item in raw)

    def read_text(self, relative_path: str) -> str:
        return _bundle_path(self.root, relative_path).read_text(encoding="utf-8")

    def artifact_path(self, name: str) -> Path | None:
        artifacts = self.manifest.get("artifacts", {})
        if not isinstance(artifacts, dict):
            raise BundleError("bundle artifacts must be an object")
        item = artifacts.get(name)
        if item is None:
            return None
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            raise BundleError(f"invalid artifact entry: {name}")
        return _bundle_path(self.root, cast(str, item["path"]))

    def artifact_text(self, name: str) -> str | None:
        path = self.artifact_path(name)
        return path.read_text(encoding="utf-8") if path is not None else None

    def artifact_json(self, name: str) -> Any | None:
        text = self.artifact_text(name)
        return json.loads(text) if text is not None else None

    def compiler_capability_identity(self) -> dict[str, Any] | None:
        """Return validated retained capability identity for new bundles."""

        artifacts = self.manifest.get("artifacts")
        if not isinstance(artifacts, Mapping):
            raise BundleError("bundle artifacts must be an object")
        item = artifacts.get("compiler_capabilities")
        if item is None:
            return None
        if not isinstance(item, Mapping):
            raise BundleError("compiler capability artifact entry must be an object")
        digest = item.get("sha256")
        size = item.get("size")
        if not isinstance(digest, str) or not isinstance(size, int):
            raise BundleError("compiler capability artifact identity is invalid")
        document = self.artifact_json("compiler_capabilities")
        if document is None:
            raise BundleError("compiler capability artifact is missing")
        try:
            return capability_identity_from_document(
                document,
                registry_sha256=digest,
                registry_bytes=size,
            )
        except CompilerCapabilityError as exc:
            raise BundleError(str(exc)) from exc

    def log_path(self, name: str) -> Path | None:
        """Return a verified log path, accepting legacy string entries."""
        logs = self.manifest.get("logs", {})
        if not isinstance(logs, dict):
            raise BundleError("bundle logs must be an object")
        item = logs.get(name)
        if item is None:
            return None
        relative_path = item if isinstance(item, str) else item.get("path")
        if not isinstance(relative_path, str):
            raise BundleError(f"invalid log entry: {name}")
        return _bundle_path(self.root, relative_path)

    def log_text(self, name: str) -> str | None:
        """Read a captured compiler log by logical name."""
        path = self.log_path(name)
        return path.read_text(encoding="utf-8") if path is not None else None


def _bundle_path(root: Path, relative_path: str) -> Path:
    candidate = (root / relative_path).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise BundleError(f"bundle path escapes root: {relative_path}") from exc
    return candidate
