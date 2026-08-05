"""Public compiler integration boundary for Loupe."""

from .capabilities import (
    CAPABILITIES_FORMAT,
    CAPABILITIES_SCHEMA_ID,
    CAPABILITIES_SCHEMA_VERSION,
    CAPABILITY_IDENTITY_FORMAT,
    CAPTURE_PROFILE_FORMAT,
    CompilerCapabilityError,
    capability_identity_from_document,
    require_capture_capabilities,
    validate_capability_document,
)
from .cli import main
from .client import (
    CAPABILITIES_TIMEOUT_SECONDS,
    MAX_CAPABILITIES_BYTES,
    CompilerCapabilityRegistry,
    clear_capability_cache,
    load_compiler_capabilities,
)

__all__ = [
    "CAPABILITIES_FORMAT",
    "CAPABILITIES_SCHEMA_ID",
    "CAPABILITIES_SCHEMA_VERSION",
    "CAPABILITIES_TIMEOUT_SECONDS",
    "CAPABILITY_IDENTITY_FORMAT",
    "CAPTURE_PROFILE_FORMAT",
    "MAX_CAPABILITIES_BYTES",
    "CompilerCapabilityError",
    "CompilerCapabilityRegistry",
    "capability_identity_from_document",
    "clear_capability_cache",
    "load_compiler_capabilities",
    "main",
    "require_capture_capabilities",
    "validate_capability_document",
]
