"""Verified loading for existing compiler-evidence bundles."""

from __future__ import annotations

from pathlib import Path

from weave_loupe.schemas import (
    SchemaCatalogError,
    SchemaValidationError,
    require_valid_document,
)

from .model import Bundle, BundleError
from .verification import BUNDLE_FORMAT, verify_bundle


def load_bundle(path: Path) -> Bundle:
    """Load a bundle only after complete fail-closed integrity verification."""
    verification = verify_bundle(path)
    if not verification.valid or verification.manifest is None:
        raise BundleError(verification.error_message())
    try:
        require_valid_document(verification.manifest, BUNDLE_FORMAT)
    except (SchemaCatalogError, SchemaValidationError) as exc:
        raise BundleError(str(exc)) from exc
    bundle = Bundle(root=verification.root, manifest=verification.manifest)
    if bundle.artifact_path("compiler_capabilities") is not None:
        bundle.compiler_capability_identity()
    return bundle
