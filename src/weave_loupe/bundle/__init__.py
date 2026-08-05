"""Public compiler-evidence bundle boundary."""

from weave_loupe.bundle_verification import (
    BUNDLE_FORMAT,
    BundleProblem,
    BundleVerification,
    verify_bundle,
)

from .capture import CaptureResult, capture_bundle
from .ingest import IngestResult, ingest_bundle
from .loading import load_bundle
from .model import Bundle, BundleError

__all__ = [
    "BUNDLE_FORMAT",
    "Bundle",
    "BundleError",
    "BundleProblem",
    "BundleVerification",
    "CaptureResult",
    "IngestResult",
    "capture_bundle",
    "ingest_bundle",
    "load_bundle",
    "verify_bundle",
]
