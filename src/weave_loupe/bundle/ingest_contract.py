"""Versioned offline contract for retained compiler evidence ingestion."""

from __future__ import annotations

import copy
import json
import re
from collections.abc import Mapping
from typing import Any

from weave_loupe.schemas import JSON_SCHEMA_DRAFT, SchemaProblem

INGEST_REQUEST_FORMAT = "weave-loupe-ingest-request-v1"
MAX_INGEST_REQUEST_BYTES = 1024 * 1024
MAX_INGEST_SOURCES = 256
MAX_INGEST_COMMAND_ARGUMENTS = 512
MAX_INGEST_SOURCE_BYTES = 64 * 1024 * 1024
MAX_INGEST_ARTIFACT_BYTES = 512 * 1024 * 1024
MAX_INGEST_LOG_BYTES = 16 * 1024 * 1024
MAX_INGEST_NODE_MAP_BYTES = 64 * 1024 * 1024
MAX_INGEST_TOTAL_BYTES = 2 * 1024 * 1024 * 1024

COMPILER_ARTIFACT_PATHS: Mapping[str, str] = {
    "compiler_capabilities": "artifacts/compiler-capabilities.json",
    "executable": "artifacts/program",
    "wir": "artifacts/program.wir",
    "llvm": "artifacts/program.ll",
    "optimized_llvm": "artifacts/program.optimized.ll",
    "assembly": "artifacts/program.s",
    "disassembly": "artifacts/program.disasm",
    "optimization_record": "artifacts/program.opt.yaml",
    "diagnostics": "artifacts/diagnostics.json",
    "trace": "artifacts/trace.json",
    "build_manifest": "artifacts/build-manifest.json",
}

_NONEMPTY: dict[str, Any] = {"type": "string", "minLength": 1}
_FILE_ENTRY: dict[str, Any] = {
    "type": "object",
    "required": ["path", "size", "sha256"],
    "properties": {
        "path": _NONEMPTY,
        "size": {"type": "integer", "minimum": 0},
        "sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
    },
    "additionalProperties": False,
}
_PORTABLE_IDENTITY: dict[str, Any] = {
    "type": "object",
    "required": ["format", "path", "scope", "symlinked"],
    "properties": {
        "format": {"const": "weave-loupe-portable-path-v1"},
        "path": _NONEMPTY,
        "scope": {"enum": ["root", "external"]},
        "symlinked": {"type": "boolean"},
    },
    "additionalProperties": False,
}
_SOURCE_METADATA: dict[str, Any] = {
    "type": "object",
    "minProperties": 1,
    "properties": {
        "producer": _NONEMPTY,
        "revision": {
            "type": "object",
            "required": ["id"],
            "properties": {
                "id": _NONEMPTY,
                "repository": _NONEMPTY,
                "ref": _NONEMPTY,
            },
            "additionalProperties": False,
        },
        "document": {
            "type": "object",
            "required": ["id"],
            "properties": {
                "id": _NONEMPTY,
                "version": _NONEMPTY,
            },
            "additionalProperties": False,
        },
        "node_map": _FILE_ENTRY,
    },
    "additionalProperties": False,
}
_SOURCE: dict[str, Any] = {
    "type": "object",
    "required": ["path", "size", "sha256", "input"],
    "properties": {
        **_FILE_ENTRY["properties"],
        "input": _NONEMPTY,
        "identity": _PORTABLE_IDENTITY,
        "metadata": _SOURCE_METADATA,
    },
    "additionalProperties": False,
}
_SCHEMA: dict[str, Any] = {
    "$schema": JSON_SCHEMA_DRAFT,
    "$id": "https://weave.dev/schemas/weave-loupe-ingest-request-v1.schema.json",
    "title": "Weave Loupe retained compiler evidence ingest request",
    "type": "object",
    "required": ["format", "compiler", "sources", "artifacts", "logs"],
    "properties": {
        "format": {"const": INGEST_REQUEST_FORMAT},
        "source_identity": {
            "type": "object",
            "required": ["format", "root_kind"],
            "properties": {
                "format": {"const": "weave-loupe-portable-path-v1"},
                "root_kind": {"enum": ["explicit", "git", "common-parent"]},
            },
            "additionalProperties": False,
        },
        "compiler": {
            "type": "object",
            "required": ["binary", "command", "exit_code", "execution"],
            "properties": {
                "binary": _NONEMPTY,
                "command": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1,
                    "maxItems": MAX_INGEST_COMMAND_ARGUMENTS,
                },
                "exit_code": {"type": "integer"},
                "execution": {
                    "type": "object",
                    "additionalProperties": True,
                },
            },
            "additionalProperties": False,
        },
        "sources": {
            "type": "array",
            "items": _SOURCE,
            "minItems": 1,
            "maxItems": MAX_INGEST_SOURCES,
        },
        "artifacts": {
            "type": "object",
            "required": ["compiler_capabilities"],
            "properties": {name: _FILE_ENTRY for name in COMPILER_ARTIFACT_PATHS},
            "additionalProperties": False,
        },
        "logs": {
            "type": "object",
            "required": ["stdout", "stderr"],
            "properties": {
                "stdout": _FILE_ENTRY,
                "stderr": _FILE_ENTRY,
            },
            "additionalProperties": False,
        },
    },
    "additionalProperties": False,
}


def ingest_request_schema() -> dict[str, Any]:
    """Return an independent offline JSON Schema for ingestion requests."""
    return copy.deepcopy(_SCHEMA)


def ingest_request_schema_json() -> str:
    """Serialize the ingest request schema deterministically."""
    return json.dumps(_SCHEMA, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def validate_ingest_request_document(document: Any) -> tuple[SchemaProblem, ...]:
    """Validate the bounded ingest request shape without touching the filesystem."""
    problems: list[SchemaProblem] = []
    _validate(document, _SCHEMA, "$", problems)
    return tuple(
        sorted(
            problems,
            key=lambda item: (item.path, item.keyword, item.message),
        )
    )


def _validate(
    value: Any,
    schema: Mapping[str, Any],
    path: str,
    problems: list[SchemaProblem],
) -> None:
    expected = schema.get("type")
    if isinstance(expected, str) and not _matches_type(value, expected):
        problems.append(
            SchemaProblem(path, "type", f"expected {expected}, got {_json_type(value)}")
        )
        return
    if "const" in schema and value != schema["const"]:
        problems.append(SchemaProblem(path, "const", f"must equal {schema['const']!r}"))
    choices = schema.get("enum")
    if isinstance(choices, list) and value not in choices:
        problems.append(SchemaProblem(path, "enum", f"must be one of {choices!r}"))

    if isinstance(value, dict):
        _validate_object(value, schema, path, problems)
    elif isinstance(value, list):
        _validate_array(value, schema, path, problems)
    elif isinstance(value, str):
        _validate_string(value, schema, path, problems)
    elif isinstance(value, int) and not isinstance(value, bool):
        minimum = schema.get("minimum")
        if isinstance(minimum, int) and value < minimum:
            problems.append(
                SchemaProblem(path, "minimum", f"must be at least {minimum}")
            )


def _validate_object(
    value: dict[Any, Any],
    schema: Mapping[str, Any],
    path: str,
    problems: list[SchemaProblem],
) -> None:
    required = schema.get("required")
    if isinstance(required, list):
        for name in required:
            if isinstance(name, str) and name not in value:
                problems.append(
                    SchemaProblem(
                        _property_path(path, name),
                        "required",
                        "required property is missing",
                    )
                )
    minimum = schema.get("minProperties")
    if isinstance(minimum, int) and len(value) < minimum:
        problems.append(
            SchemaProblem(
                path,
                "minProperties",
                f"requires at least {minimum} properties",
            )
        )

    raw_properties = schema.get("properties")
    properties = raw_properties if isinstance(raw_properties, Mapping) else {}
    additional = schema.get("additionalProperties", True)
    for raw_name, item in value.items():
        name = str(raw_name)
        child_path = _property_path(path, name)
        child_schema = properties.get(name)
        if isinstance(child_schema, Mapping):
            _validate(item, child_schema, child_path, problems)
        elif additional is False:
            problems.append(
                SchemaProblem(
                    child_path,
                    "additionalProperties",
                    "unknown property",
                )
            )
        elif isinstance(additional, Mapping):
            _validate(item, additional, child_path, problems)


def _validate_array(
    value: list[Any],
    schema: Mapping[str, Any],
    path: str,
    problems: list[SchemaProblem],
) -> None:
    minimum = schema.get("minItems")
    if isinstance(minimum, int) and len(value) < minimum:
        problems.append(
            SchemaProblem(path, "minItems", f"requires at least {minimum} items")
        )
    maximum = schema.get("maxItems")
    if isinstance(maximum, int) and len(value) > maximum:
        problems.append(
            SchemaProblem(path, "maxItems", f"allows at most {maximum} items")
        )
    item_schema = schema.get("items")
    if isinstance(item_schema, Mapping):
        for index, item in enumerate(value):
            _validate(item, item_schema, f"{path}[{index}]", problems)


def _validate_string(
    value: str,
    schema: Mapping[str, Any],
    path: str,
    problems: list[SchemaProblem],
) -> None:
    minimum = schema.get("minLength")
    if isinstance(minimum, int) and len(value) < minimum:
        problems.append(
            SchemaProblem(
                path,
                "minLength",
                f"requires at least {minimum} characters",
            )
        )
    pattern = schema.get("pattern")
    if isinstance(pattern, str) and re.search(pattern, value) is None:
        problems.append(SchemaProblem(path, "pattern", f"does not match {pattern!r}"))


def _matches_type(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    return True


def _json_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def _property_path(path: str, name: str) -> str:
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
        return f"{path}.{name}"
    return f"{path}[{name!r}]"
