"""Architecture checks for the public bundle package boundary."""

from __future__ import annotations

import ast
from pathlib import Path
from types import ModuleType

import weave_loupe.bundle as public_bundle
from weave_loupe.bundle import capture, loading, model


def test_public_bundle_api_reexports_lifecycle_roles() -> None:
    assert public_bundle.Bundle is model.Bundle
    assert public_bundle.BundleError is model.BundleError
    assert public_bundle.CaptureResult is capture.CaptureResult
    assert public_bundle.capture_bundle is capture.capture_bundle
    assert public_bundle.load_bundle is loading.load_bundle


def test_bundle_model_and_loading_do_not_import_compiler_execution() -> None:
    forbidden = {
        "weave_loupe.compiler.client",
        "weave_loupe.compiler_capabilities",
        "weave_loupe.weavec",
    }
    for module in (model, loading):
        assert _imports(module).isdisjoint(forbidden)


def _imports(module: ModuleType) -> set[str]:
    path = Path(module.__file__ or "")
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            names.add(node.module)
    return names
