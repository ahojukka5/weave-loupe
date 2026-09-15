"""Deterministic views over one evidence bundle."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from weave_loupe.bundle.model import Bundle

VIEW_NAMES: tuple[str, ...] = (
    "source_tests",
    "source_ir",
    "full",
    "deterministic",
    "model",
)

_VIEW_ARTIFACTS: dict[str, tuple[str, ...]] = {
    "source_tests": (
        "compiler_capabilities",
        "diagnostics",
        "build_manifest",
    ),
    "source_ir": (
        "compiler_capabilities",
        "wir",
        "llvm",
        "optimized_llvm",
        "diagnostics",
        "build_manifest",
    ),
    "full": (),
    "deterministic": (),
    "model": (
        "compiler_capabilities",
        "wir",
        "llvm",
        "optimized_llvm",
        "diagnostics",
        "trace",
        "build_manifest",
    ),
}


def evidence_view(bundle: Bundle, name: str) -> dict[str, Any]:
    """Project one information condition from a single retained bundle."""
    if name not in VIEW_NAMES:
        raise ValueError(f"unknown evidence view {name!r}")
    artifacts = bundle.manifest.get("artifacts")
    if not isinstance(artifacts, Mapping):
        artifacts = {}
    selected = _selected_names(name, artifacts)
    files = _file_entries(bundle, selected)
    budget = information_budget(files)
    return {
        "format": "weave-loupe-evidence-view-v1",
        "view": name,
        "objects": selected,
        "files": files,
        "budget": budget,
    }


def information_budget(files: Mapping[str, Mapping[str, Any]]) -> dict[str, int]:
    """Account for retained bytes without interpreting them as reasoning quality."""
    raw_bytes = 0
    text_bytes = 0
    for item in files.values():
        size = item.get("size")
        if isinstance(size, int):
            raw_bytes += size
        text = item.get("text_bytes")
        if isinstance(text, int):
            text_bytes += text
    return {
        "objects": len(files),
        "raw_bytes": raw_bytes,
        "normalized_text_bytes": text_bytes,
    }


def _selected_names(view: str, artifacts: Mapping[str, Any]) -> list[str]:
    if view in {"full", "deterministic"}:
        names = [name for name in artifacts if isinstance(name, str)]
        return sorted(names)
    wanted = set(_VIEW_ARTIFACTS[view])
    return sorted(name for name in artifacts if name in wanted)


def _file_entries(bundle: Bundle, names: list[str]) -> dict[str, dict[str, Any]]:
    artifacts = bundle.manifest.get("artifacts")
    if not isinstance(artifacts, Mapping):
        artifacts = {}
    logs = bundle.manifest.get("logs")
    files: dict[str, dict[str, Any]] = {}
    for index, source in enumerate(bundle.sources):
        files[f"source[{index}]"] = _entry_budget(source, text=True)
    if isinstance(logs, Mapping):
        for name, item in logs.items():
            if isinstance(item, Mapping):
                files[f"log.{name}"] = _entry_budget(item, text=True)
    for name in names:
        item = artifacts.get(name)
        if isinstance(item, Mapping):
            files[f"artifact.{name}"] = _entry_budget(
                item,
                text=name != "executable",
            )
    return files


def _entry_budget(item: Mapping[str, Any], *, text: bool) -> dict[str, Any]:
    size = item.get("size")
    digest = item.get("sha256")
    result: dict[str, Any] = {
        "sha256": digest if isinstance(digest, str) else None,
        "size": size if isinstance(size, int) else 0,
        "text_bytes": (size if isinstance(size, int) else 0) if text else 0,
    }
    path = item.get("path")
    if isinstance(path, str):
        result["path"] = path
    return result
