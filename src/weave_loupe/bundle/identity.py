"""Portable compiler identity recorded in an evidence bundle."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from weave_loupe.auditor_identity import sha256_file
from weave_loupe.compiler_version import identify_weavec


def compiler_content_identity(
    binary: Path,
    *,
    capability_registry_sha256: str | None = None,
    target: str | None = None,
) -> dict[str, Any]:
    """Return a host-path-free identity for the compiler that produced a bundle."""
    version = identify_weavec(binary)
    identity: dict[str, Any] = {
        "compiler_sha256": sha256_file(binary),
        "compiler_version": version.display,
        "git_sha": version.git_sha,
        "development": version.development,
        "version_source": version.source,
    }
    if capability_registry_sha256 is not None:
        identity["capability_registry_sha256"] = capability_registry_sha256
    if target:
        identity["target"] = target
    return identity


def identity_from_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Return declared compilation identity or an empty mapping."""
    compilation = manifest.get("compilation")
    if not isinstance(compilation, Mapping):
        return {}
    identity = compilation.get("identity")
    return dict(identity) if isinstance(identity, Mapping) else {}
