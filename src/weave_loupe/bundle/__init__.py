"""Public compiler-evidence bundle boundary."""

from weave_loupe.bundle_verification import (
    BUNDLE_FORMAT,
    BundleProblem,
    BundleVerification,
    verify_bundle,
)

from .capture import CaptureResult, capture_bundle
from .ingest import IngestResult, ingest_bundle
from .ingest_contract import (
    INGEST_REQUEST_FORMAT,
    ingest_request_schema,
    ingest_request_schema_json,
    validate_ingest_request_document,
)
from .loading import load_bundle
from .model import Bundle, BundleError

__all__ = [
    "BUNDLE_FORMAT",
    "INGEST_REQUEST_FORMAT",
    "Bundle",
    "BundleError",
    "BundleProblem",
    "BundleVerification",
    "CaptureResult",
    "IngestResult",
    "capture_bundle",
    "ingest_bundle",
    "ingest_request_schema",
    "ingest_request_schema_json",
    "load_bundle",
    "validate_ingest_request_document",
    "verify_bundle",
]
