"""Compatibility facade for the compiler capability integration."""

from weave_loupe.compiler import (
    CAPABILITIES_FORMAT,
    CAPABILITIES_SCHEMA_ID,
    CAPABILITIES_SCHEMA_VERSION,
    CAPABILITIES_TIMEOUT_SECONDS,
    CAPABILITY_IDENTITY_FORMAT,
    CAPTURE_PROFILE_FORMAT,
    MAX_CAPABILITIES_BYTES,
    CompilerCapabilityError,
    CompilerCapabilityRegistry,
    capability_identity_from_document,
    clear_capability_cache,
    load_compiler_capabilities,
    main,
    require_capture_capabilities,
    validate_capability_document,
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


if __name__ == "__main__":
    raise SystemExit(main())
