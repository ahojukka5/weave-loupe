"""Offline JSON Schema catalog and deterministic validation."""

from __future__ import annotations

import copy
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCHEMA_CATALOG_FORMAT = "weave-loupe-schema-catalog-v1"
SCHEMA_EXAMPLES_FORMAT = "weave-loupe-schema-examples-v1"
JSON_VALIDATION_FORMAT = "weave-loupe-json-validation-v1"
JSON_SCHEMA_DRAFT = "https://json-schema.org/draft/2020-12/schema"
_SCHEMA_BASE = "https://weave.dev/schemas/"


class SchemaCatalogError(ValueError):
    """Raised when a schema name or document cannot be resolved."""


class SchemaValidationError(ValueError):
    """Raised when a document violates its published schema."""

    def __init__(
        self,
        format_name: str,
        problems: tuple[SchemaProblem, ...],
    ) -> None:
        self.format_name = format_name
        self.problems = problems
        detail = "; ".join(f"{item.path}: {item.message}" for item in problems)
        super().__init__(f"{format_name} schema validation failed: {detail}")


@dataclass(frozen=True)
class SchemaProblem:
    """One stable JSON Schema validation diagnostic."""

    path: str
    keyword: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {
            "path": self.path,
            "keyword": self.keyword,
            "message": self.message,
        }


def _object(
    *,
    required: tuple[str, ...] = (),
    properties: dict[str, Any] | None = None,
    additional: bool | dict[str, Any] = False,
    min_properties: int | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "type": "object",
        "properties": properties or {},
        "additionalProperties": additional,
    }
    if required:
        result["required"] = list(required)
    if min_properties is not None:
        result["minProperties"] = min_properties
    return result


def _schema(
    format_name: str,
    title: str,
    contract: dict[str, Any],
) -> dict[str, Any]:
    return {
        "$schema": JSON_SCHEMA_DRAFT,
        "$id": f"{_SCHEMA_BASE}{format_name}.schema.json",
        "title": title,
        **contract,
    }


_STRING = {"type": "string"}
_NONEMPTY = {"type": "string", "minLength": 1}
_NONNEGATIVE = {"type": "integer", "minimum": 0}
_SHA256 = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
_STRING_ARRAY = {"type": "array", "items": _STRING}
_ANY_OBJECT = {"type": "object", "additionalProperties": True}
_NULLABLE_OBJECT = {
    "type": ["object", "null"],
    "additionalProperties": True,
}
_COUNT_MAP = {
    "type": "object",
    "additionalProperties": {"type": "integer"},
}
_DELTA_VALUE = _object(
    required=("before", "after", "delta"),
    properties={
        "before": {"type": ["integer", "null"]},
        "after": {"type": ["integer", "null"]},
        "delta": {"type": ["integer", "null"]},
    },
)
_DELTA_MAP = {
    "type": "object",
    "additionalProperties": _DELTA_VALUE,
}

_PORTABLE_PATH = _object(
    required=("format", "path", "scope", "symlinked"),
    properties={
        "format": {"const": "weave-loupe-portable-path-v1"},
        "path": _NONEMPTY,
        "scope": {"enum": ["root", "external"]},
        "symlinked": {"type": "boolean"},
    },
)
_FILE_ENTRY = _object(
    required=("path", "size", "sha256"),
    properties={
        "path": _NONEMPTY,
        "size": _NONNEGATIVE,
        "sha256": _SHA256,
    },
    additional=True,
)
_SOURCE_ENTRY = _object(
    required=("path", "size", "sha256", "index"),
    properties={
        "path": _NONEMPTY,
        "size": _NONNEGATIVE,
        "sha256": _SHA256,
        "index": _NONNEGATIVE,
        "input": _NONEMPTY,
        "identity": _PORTABLE_PATH,
    },
    additional=True,
)
_PROBLEM = _object(
    required=("code", "location", "message"),
    properties={
        "code": _STRING,
        "location": _STRING,
        "message": _STRING,
    },
)

_NATIVE_FUNCTION = _object(
    properties={
        "max_instructions": _NONNEGATIVE,
        "max_padding_instructions": _NONNEGATIVE,
        "max_direct_calls": _NONNEGATIVE,
        "max_indirect_calls": _NONNEGATIVE,
        "max_backward_conditional_branches": _NONNEGATIVE,
        "min_backward_conditional_branches": _NONNEGATIVE,
        "required_direct_calls": {
            "type": "array",
            "items": _NONEMPTY,
            "uniqueItems": True,
        },
    },
    min_properties=1,
)
_NATIVE_BUDGET = _object(
    required=("format",),
    properties={
        "format": {"const": "weave-loupe-native-budget-v1"},
        "max_program_owned_functions": _NONNEGATIVE,
        "max_reachable_program_functions": _NONNEGATIVE,
        "max_unreachable_program_functions": _NONNEGATIVE,
        "max_unreachable_program_instructions": _NONNEGATIVE,
        "functions": {
            "type": "object",
            "additionalProperties": _NATIVE_FUNCTION,
        },
    },
    min_properties=2,
)

_OPTIMIZED_PROPERTIES: dict[str, Any] = {
    "format": {"const": "weave-loupe-optimized-llvm-budget-v1"},
    "required_defined_functions": {
        "type": "array",
        "items": _NONEMPTY,
        "uniqueItems": True,
    },
    "required_call_targets": {
        "type": "array",
        "items": _NONEMPTY,
        "uniqueItems": True,
    },
}
for _metric in (
    "functions",
    "basic_blocks",
    "instructions",
    "alloca",
    "load",
    "store",
    "call",
    "invoke",
    "phi",
    "br",
    "switch",
    "ret",
    "add",
    "sub",
    "mul",
    "sdiv",
    "udiv",
    "icmp",
    "select",
    "identity_adds",
    "anonymous_ssa_lines",
    "numeric_blocks",
    "undef_uses",
    "poison_uses",
):
    _OPTIMIZED_PROPERTIES[f"min_{_metric}"] = _NONNEGATIVE
    _OPTIMIZED_PROPERTIES[f"max_{_metric}"] = _NONNEGATIVE
_OPTIMIZED_BUDGET = _object(
    required=("format",),
    properties=_OPTIMIZED_PROPERTIES,
    min_properties=2,
)

_EXPECTATION = _object(
    required=("exit_code",),
    properties={
        "exit_code": {
            "type": "integer",
            "minimum": -255,
            "maximum": 255,
        },
        "stdout": {"type": ["string", "null"]},
        "stderr": {"type": ["string", "null"]},
    },
)
_RUNTIME_CASE = _object(
    required=("name", "expect"),
    properties={
        "name": _NONEMPTY,
        "args": _STRING_ARRAY,
        "env": {
            "type": "object",
            "additionalProperties": {"type": ["string", "null"]},
        },
        "stdin": _STRING,
        "expect": _EXPECTATION,
    },
)
_RUNTIME_SIDECAR = _object(
    required=("format",),
    properties={
        "format": {"const": "weave-loupe-runtime-cases-v1"},
        "timeout_seconds": {
            "type": "number",
            "exclusiveMinimum": 0,
            "maximum": 60,
        },
        "inherit_environment": {"type": "boolean"},
        "cases": {"type": "array", "items": _RUNTIME_CASE},
        "native_budget": _NATIVE_BUDGET,
        "optimized_llvm_budget": _OPTIMIZED_BUDGET,
    },
)
_RUNTIME_SIDECAR["anyOf"] = [
    {
        "required": ["cases"],
        "properties": {
            "cases": {"type": "array", "minItems": 1},
        },
    },
    {"required": ["native_budget"]},
    {"required": ["optimized_llvm_budget"]},
]

_DIFF_V1 = _object(
    required=("format", "llvm_metrics", "trace_actions", "trace_passes"),
    properties={
        "format": {"const": "weave-loupe-diff-v1"},
        "llvm_metrics": _DELTA_MAP,
        "trace_actions": _DELTA_MAP,
        "trace_passes": _DELTA_MAP,
    },
)
_CHANGE = _object(
    required=(
        "id",
        "section",
        "path",
        "kind",
        "classification",
        "severity",
        "before",
        "after",
    ),
    properties={
        "id": _NONEMPTY,
        "section": _NONEMPTY,
        "path": _NONEMPTY,
        "kind": _NONEMPTY,
        "classification": {"enum": ["semantic", "quality", "provenance", "evidence"]},
        "severity": {"enum": ["info", "warning", "error"]},
        "before": {},
        "after": {},
        "delta": {"type": ["integer", "number", "null"]},
    },
)
_SOURCE_MISMATCH = _object(
    required=(
        "kind",
        "recorded_index",
        "current_index",
        "recorded_path",
        "current_path",
        "recorded_sha256",
        "current_sha256",
        "recorded_size",
        "current_size",
        "detail",
    ),
    properties={
        "kind": _STRING,
        "recorded_index": {"type": ["integer", "null"]},
        "current_index": {"type": ["integer", "null"]},
        "recorded_path": {"type": ["string", "null"]},
        "current_path": {"type": ["string", "null"]},
        "recorded_sha256": {"anyOf": [_SHA256, {"type": "null"}]},
        "current_sha256": {"anyOf": [_SHA256, {"type": "null"}]},
        "recorded_size": {
            "type": ["integer", "null"],
            "minimum": 0,
        },
        "current_size": {
            "type": ["integer", "null"],
            "minimum": 0,
        },
        "detail": _STRING,
    },
)
_COMPILER_POLICY = _object(
    required=("format",),
    properties={
        "format": {"const": "weave-loupe-compiler-audit-policy-v1"},
        "metric_deltas": {
            "type": "object",
            "additionalProperties": _object(
                properties={
                    "minimum": {"type": ["integer", "null"]},
                    "maximum": {"type": ["integer", "null"]},
                },
                min_properties=1,
            ),
        },
        "forbid_changes": {
            "type": "array",
            "items": {
                "enum": [
                    "diagnostics",
                    "evidence",
                    "runtime",
                    "native_budget",
                    "optimized_llvm_budget",
                ]
            },
            "uniqueItems": True,
        },
    },
)
_BUDGET_RESULT_PROPERTIES = {
    "configured": {"type": "boolean"},
    "passed": {"type": "boolean"},
    "failures": {"type": "array", "items": _STRING},
    "sidecar": _STRING,
    "sidecar_sha256": _SHA256,
    "limits": _ANY_OBJECT,
    "observed": _ANY_OBJECT,
}


def _build_schemas() -> dict[str, dict[str, Any]]:
    return {
        "weave-loupe-portable-path-v1": _schema(
            "weave-loupe-portable-path-v1",
            "Weave Loupe portable path identity",
            _PORTABLE_PATH,
        ),
        "weave-loupe-bundle-v1": _schema(
            "weave-loupe-bundle-v1",
            "Weave Loupe evidence bundle manifest",
            _object(
                required=(
                    "format",
                    "compiler",
                    "sources",
                    "artifacts",
                    "logs",
                ),
                properties={
                    "format": {"const": "weave-loupe-bundle-v1"},
                    "source_identity": _object(
                        required=("format", "root_kind"),
                        properties={
                            "format": {"const": "weave-loupe-portable-path-v1"},
                            "root_kind": {"enum": ["explicit", "git", "common-parent"]},
                        },
                    ),
                    "compiler": _object(
                        required=(
                            "binary",
                            "command",
                            "exit_code",
                            "execution",
                        ),
                        properties={
                            "binary": _NONEMPTY,
                            "command": {
                                "type": "array",
                                "items": _STRING,
                                "minItems": 1,
                            },
                            "exit_code": {"type": "integer"},
                            "execution": _ANY_OBJECT,
                        },
                    ),
                    "sources": {
                        "type": "array",
                        "items": _SOURCE_ENTRY,
                        "minItems": 1,
                    },
                    "artifacts": {
                        "type": "object",
                        "additionalProperties": _FILE_ENTRY,
                    },
                    "logs": _object(
                        required=("stdout", "stderr"),
                        properties={
                            "stdout": {"anyOf": [_NONEMPTY, _FILE_ENTRY]},
                            "stderr": {"anyOf": [_NONEMPTY, _FILE_ENTRY]},
                        },
                        additional=_FILE_ENTRY,
                    ),
                },
            ),
        ),
        "weave-loupe-analysis-v1": _schema(
            "weave-loupe-analysis-v1",
            "Weave Loupe deterministic analysis",
            _object(
                required=(
                    "format",
                    "compiler_exit_code",
                    "wir",
                    "llvm",
                    "optimized_llvm",
                    "optimization_remarks",
                    "native",
                    "evidence",
                    "trace",
                    "diagnostics",
                ),
                properties={
                    "format": {"const": "weave-loupe-analysis-v1"},
                    "compiler_exit_code": {"type": "integer"},
                    "wir": _ANY_OBJECT,
                    "llvm": _COUNT_MAP,
                    "optimized_llvm": _COUNT_MAP,
                    "optimization_remarks": _ANY_OBJECT,
                    "native": _ANY_OBJECT,
                    "evidence": {
                        "type": "object",
                        "additionalProperties": {"type": "boolean"},
                    },
                    "trace": _object(
                        required=("events", "actions", "passes", "categories"),
                        properties={
                            "events": _NONNEGATIVE,
                            "actions": _COUNT_MAP,
                            "passes": _COUNT_MAP,
                            "categories": _COUNT_MAP,
                        },
                    ),
                    "diagnostics": _object(
                        required=("available", "items"),
                        properties={
                            "available": {"type": "boolean"},
                            "items": _NONNEGATIVE,
                            "severities": _COUNT_MAP,
                        },
                    ),
                },
            ),
        ),
        "weave-loupe-diff-v1": _schema(
            "weave-loupe-diff-v1",
            "Weave Loupe compact bundle diff",
            _DIFF_V1,
        ),
        "weave-loupe-diff-v2": _schema(
            "weave-loupe-diff-v2",
            "Weave Loupe complete bundle diff",
            _object(
                required=(
                    "format",
                    "summary",
                    "changes",
                    "compiler",
                    "analysis",
                    "sources",
                    "artifacts",
                    "logs",
                    "manifest",
                    "optimization_remarks",
                    "supplemental",
                    "compatibility",
                ),
                properties={
                    "format": {"const": "weave-loupe-diff-v2"},
                    "summary": _ANY_OBJECT,
                    "changes": {"type": "array", "items": _CHANGE},
                    "compiler": _ANY_OBJECT,
                    "analysis": _ANY_OBJECT,
                    "sources": _ANY_OBJECT,
                    "artifacts": _ANY_OBJECT,
                    "logs": _ANY_OBJECT,
                    "manifest": _ANY_OBJECT,
                    "optimization_remarks": _ANY_OBJECT,
                    "supplemental": _ANY_OBJECT,
                    "compatibility": _object(
                        required=(
                            "legacy_format",
                            "legacy_projection",
                            "usage",
                        ),
                        properties={
                            "legacy_format": {"const": "weave-loupe-diff-v1"},
                            "legacy_projection": _DIFF_V1,
                            "usage": _STRING,
                        },
                    ),
                },
            ),
        ),
        "weave-loupe-runtime-cases-v1": _schema(
            "weave-loupe-runtime-cases-v1",
            "Weave Loupe runtime and optimization sidecar",
            _RUNTIME_SIDECAR,
        ),
        "weave-loupe-native-budget-v1": _schema(
            "weave-loupe-native-budget-v1",
            "Weave Loupe native code budget",
            _NATIVE_BUDGET,
        ),
        "weave-loupe-optimized-llvm-budget-v1": _schema(
            "weave-loupe-optimized-llvm-budget-v1",
            "Weave Loupe optimized LLVM budget",
            _OPTIMIZED_BUDGET,
        ),
        "weave-loupe-runtime-matrix-v1": _schema(
            "weave-loupe-runtime-matrix-v1",
            "Weave Loupe runtime result matrix",
            _object(
                required=(
                    "format",
                    "configured",
                    "passed",
                    "case_count",
                    "cases",
                ),
                properties={
                    "format": {"const": "weave-loupe-runtime-matrix-v1"},
                    "configured": {"type": "boolean"},
                    "passed": {"type": "boolean"},
                    "case_count": _NONNEGATIVE,
                    "cases": {"type": "array", "items": _ANY_OBJECT},
                    "sidecar": _STRING,
                    "sidecar_sha256": _SHA256,
                    "executable_sha256": {"anyOf": [_SHA256, {"type": "null"}]},
                    "timeout_seconds": {
                        "type": "number",
                        "exclusiveMinimum": 0,
                    },
                    "inherit_environment": {"type": "boolean"},
                    "sandbox": _NULLABLE_OBJECT,
                    "limits": _NULLABLE_OBJECT,
                },
            ),
        ),
        "weave-loupe-native-budget-result-v1": _schema(
            "weave-loupe-native-budget-result-v1",
            "Weave Loupe native budget result",
            _object(
                required=("format", "configured", "passed", "failures"),
                properties={
                    "format": {"const": "weave-loupe-native-budget-result-v1"},
                    **_BUDGET_RESULT_PROPERTIES,
                },
            ),
        ),
        "weave-loupe-optimized-llvm-budget-result-v1": _schema(
            "weave-loupe-optimized-llvm-budget-result-v1",
            "Weave Loupe optimized LLVM budget result",
            _object(
                required=("format", "configured", "passed", "failures"),
                properties={
                    "format": {"const": "weave-loupe-optimized-llvm-budget-result-v1"},
                    **_BUDGET_RESULT_PROPERTIES,
                },
            ),
        ),
        "weave-loupe-audit-metadata-v1": _schema(
            "weave-loupe-audit-metadata-v1",
            "Weave Loupe audit metadata",
            _object(
                required=(
                    "format",
                    "timestamp_utc",
                    "validity",
                    "model",
                    "llm",
                    "source_repository",
                    "loupe_repository",
                    "auditor",
                    "weavec",
                    "native",
                    "machine",
                    "sources",
                    "runtime_input",
                    "bundle",
                    "github",
                ),
                properties={
                    "format": {"const": "weave-loupe-audit-metadata-v1"},
                    "timestamp_utc": _NONEMPTY,
                    "validity": _ANY_OBJECT,
                    "model": _NONEMPTY,
                    "llm": _ANY_OBJECT,
                    "source_repository": _ANY_OBJECT,
                    "loupe_repository": _ANY_OBJECT,
                    "auditor": _ANY_OBJECT,
                    "weavec": _ANY_OBJECT,
                    "native": _ANY_OBJECT,
                    "machine": _ANY_OBJECT,
                    "sources": {
                        "type": "array",
                        "minItems": 1,
                        "items": _object(
                            required=("path", "sha256", "size"),
                            properties={
                                "path": _STRING,
                                "sha256": _SHA256,
                                "size": _NONNEGATIVE,
                                "identity": _PORTABLE_PATH,
                            },
                        ),
                    },
                    "runtime_input": _NULLABLE_OBJECT,
                    "bundle": _ANY_OBJECT,
                    "github": _ANY_OBJECT,
                },
            ),
        ),
        "weave-loupe-report-verification-v1": _schema(
            "weave-loupe-report-verification-v1",
            "Weave Loupe report verification",
            _object(
                required=(
                    "format",
                    "valid",
                    "checked_at_utc",
                    "max_age_days",
                    "report",
                    "source",
                    "sources",
                    "source_mismatches",
                    "reasons",
                    "report_identity",
                    "current_compiler",
                    "current_auditor",
                    "current_model",
                    "current_endpoint",
                    "current_max_tokens",
                ),
                properties={
                    "format": {"const": "weave-loupe-report-verification-v1"},
                    "valid": {"type": "boolean"},
                    "checked_at_utc": _NONEMPTY,
                    "max_age_days": {"type": "integer", "minimum": 1},
                    "report": _STRING,
                    "source": _STRING,
                    "sources": _STRING_ARRAY,
                    "source_mismatches": {
                        "type": "array",
                        "items": _SOURCE_MISMATCH,
                    },
                    "reasons": _STRING_ARRAY,
                    "report_identity": _ANY_OBJECT,
                    "current_compiler": _ANY_OBJECT,
                    "current_auditor": _ANY_OBJECT,
                    "current_model": {"type": ["string", "null"]},
                    "current_endpoint": {"type": ["string", "null"]},
                    "current_max_tokens": {
                        "type": ["integer", "null"],
                        "minimum": 1,
                    },
                },
            ),
        ),
        "weave-loupe-bundle-verification-v1": _schema(
            "weave-loupe-bundle-verification-v1",
            "Weave Loupe bundle verification",
            _object(
                required=(
                    "format",
                    "bundle",
                    "closed",
                    "valid",
                    "checked_files",
                    "legacy_unhashed_logs",
                    "problem_count",
                    "problems",
                ),
                properties={
                    "format": {"const": "weave-loupe-bundle-verification-v1"},
                    "bundle": _STRING,
                    "closed": {"type": "boolean"},
                    "valid": {"type": "boolean"},
                    "checked_files": _NONNEGATIVE,
                    "legacy_unhashed_logs": _STRING_ARRAY,
                    "problem_count": _NONNEGATIVE,
                    "problems": {"type": "array", "items": _PROBLEM},
                },
            ),
        ),
        "weave-loupe-compiler-audit-policy-v1": _schema(
            "weave-loupe-compiler-audit-policy-v1",
            "Weave Loupe compiler audit policy",
            _COMPILER_POLICY,
        ),
        "weave-loupe-compiler-audit-v1": _schema(
            "weave-loupe-compiler-audit-v1",
            "Weave Loupe compiler audit",
            _object(
                required=(
                    "format",
                    "status",
                    "passed",
                    "sources",
                    "policy",
                    "baseline",
                    "candidate",
                    "comparison",
                    "failures",
                    "review",
                    "seal",
                ),
                properties={
                    "format": {"const": "weave-loupe-compiler-audit-v1"},
                    "status": {
                        "enum": [
                            "pass",
                            "regression",
                            "infrastructure-failure",
                        ]
                    },
                    "passed": {"type": "boolean"},
                    "sources": {"type": "array", "items": _ANY_OBJECT},
                    "policy": _ANY_OBJECT,
                    "baseline": _ANY_OBJECT,
                    "candidate": _ANY_OBJECT,
                    "comparison": _ANY_OBJECT,
                    "failures": {
                        "type": "array",
                        "items": _object(
                            required=("category", "code", "detail"),
                            properties={
                                "category": _STRING,
                                "code": _STRING,
                                "detail": _STRING,
                                "evidence": {},
                            },
                        ),
                    },
                    "review": _NULLABLE_OBJECT,
                    "seal": _object(
                        required=("format", "sha256"),
                        properties={
                            "format": {
                                "const": ("weave-loupe-canonical-json-sha256-v1")
                            },
                            "sha256": _SHA256,
                        },
                    ),
                },
            ),
        ),
        "weave-loupe-json-validation-v1": _schema(
            "weave-loupe-json-validation-v1",
            "Weave Loupe JSON validation result",
            _object(
                required=("format", "document_format", "valid", "problems"),
                properties={
                    "format": {"const": "weave-loupe-json-validation-v1"},
                    "document_format": _STRING,
                    "valid": {"type": "boolean"},
                    "problems": {"type": "array", "items": _PROBLEM},
                },
            ),
        ),
    }


_SCHEMAS = _build_schemas()
_EXAMPLE_SHA = "0" * 64


def _analysis_example() -> dict[str, Any]:
    return {
        "format": "weave-loupe-analysis-v1",
        "compiler_exit_code": 0,
        "wir": {},
        "llvm": {},
        "optimized_llvm": {},
        "optimization_remarks": {},
        "native": {},
        "evidence": {},
        "trace": {
            "events": 0,
            "actions": {},
            "passes": {},
            "categories": {},
        },
        "diagnostics": {"available": False, "items": 0},
    }


def _diff_v1_example() -> dict[str, Any]:
    return {
        "format": "weave-loupe-diff-v1",
        "llvm_metrics": {},
        "trace_actions": {},
        "trace_passes": {},
    }


def _build_examples() -> dict[str, Any]:
    portable = {
        "format": "weave-loupe-portable-path-v1",
        "path": "src/demo.weave",
        "scope": "root",
        "symlinked": False,
    }
    policy = {
        "format": "weave-loupe-compiler-audit-policy-v1",
        "metric_deltas": {},
        "forbid_changes": ["runtime"],
    }
    diff_v1 = _diff_v1_example()
    return {
        "weave-loupe-portable-path-v1": portable,
        "weave-loupe-bundle-v1": {
            "format": "weave-loupe-bundle-v1",
            "source_identity": {
                "format": "weave-loupe-portable-path-v1",
                "root_kind": "git",
            },
            "compiler": {
                "binary": "weavec",
                "command": ["weavec", "build", "sources/000-demo.weave"],
                "exit_code": 0,
                "execution": {},
            },
            "sources": [
                {
                    "path": "sources/000-demo.weave",
                    "size": 10,
                    "sha256": _EXAMPLE_SHA,
                    "index": 0,
                    "input": "src/demo.weave",
                    "identity": portable,
                }
            ],
            "artifacts": {},
            "logs": {
                "stdout": {
                    "path": "logs/stdout.txt",
                    "size": 0,
                    "sha256": _EXAMPLE_SHA,
                },
                "stderr": {
                    "path": "logs/stderr.txt",
                    "size": 0,
                    "sha256": _EXAMPLE_SHA,
                },
            },
        },
        "weave-loupe-analysis-v1": _analysis_example(),
        "weave-loupe-diff-v1": diff_v1,
        "weave-loupe-diff-v2": {
            "format": "weave-loupe-diff-v2",
            "summary": {},
            "changes": [],
            "compiler": {},
            "analysis": {},
            "sources": {},
            "artifacts": {},
            "logs": {},
            "manifest": {},
            "optimization_remarks": {},
            "supplemental": {},
            "compatibility": {
                "legacy_format": "weave-loupe-diff-v1",
                "legacy_projection": diff_v1,
                "usage": "Use v1 when required.",
            },
        },
        "weave-loupe-runtime-cases-v1": {
            "format": "weave-loupe-runtime-cases-v1",
            "timeout_seconds": 5,
            "inherit_environment": False,
            "cases": [
                {
                    "name": "smoke",
                    "args": [],
                    "env": {},
                    "stdin": "",
                    "expect": {
                        "exit_code": 0,
                        "stdout": "",
                        "stderr": "",
                    },
                }
            ],
        },
        "weave-loupe-native-budget-v1": {
            "format": "weave-loupe-native-budget-v1",
            "max_program_owned_functions": 1,
        },
        "weave-loupe-optimized-llvm-budget-v1": {
            "format": "weave-loupe-optimized-llvm-budget-v1",
            "max_instructions": 100,
        },
        "weave-loupe-runtime-matrix-v1": {
            "format": "weave-loupe-runtime-matrix-v1",
            "configured": False,
            "passed": True,
            "case_count": 0,
            "cases": [],
        },
        "weave-loupe-native-budget-result-v1": {
            "format": "weave-loupe-native-budget-result-v1",
            "configured": False,
            "passed": True,
            "failures": [],
        },
        "weave-loupe-optimized-llvm-budget-result-v1": {
            "format": "weave-loupe-optimized-llvm-budget-result-v1",
            "configured": False,
            "passed": True,
            "failures": [],
        },
        "weave-loupe-audit-metadata-v1": {
            "format": "weave-loupe-audit-metadata-v1",
            "timestamp_utc": "2026-08-03T00:00:00+00:00",
            "validity": {},
            "model": "example-model",
            "llm": {},
            "source_repository": {},
            "loupe_repository": {},
            "auditor": {},
            "weavec": {},
            "native": {},
            "machine": {},
            "sources": [
                {
                    "path": "src/demo.weave",
                    "sha256": _EXAMPLE_SHA,
                    "size": 10,
                    "identity": portable,
                }
            ],
            "runtime_input": None,
            "bundle": {},
            "github": {},
        },
        "weave-loupe-report-verification-v1": {
            "format": "weave-loupe-report-verification-v1",
            "valid": True,
            "checked_at_utc": "2026-08-03T00:00:00+00:00",
            "max_age_days": 30,
            "report": "demo.md",
            "source": "src/demo.weave",
            "sources": ["src/demo.weave"],
            "source_mismatches": [],
            "reasons": [],
            "report_identity": {},
            "current_compiler": {},
            "current_auditor": {},
            "current_model": None,
            "current_endpoint": None,
            "current_max_tokens": None,
        },
        "weave-loupe-bundle-verification-v1": {
            "format": "weave-loupe-bundle-verification-v1",
            "bundle": "demo.loupe",
            "closed": True,
            "valid": True,
            "checked_files": 0,
            "legacy_unhashed_logs": [],
            "problem_count": 0,
            "problems": [],
        },
        "weave-loupe-compiler-audit-policy-v1": policy,
        "weave-loupe-compiler-audit-v1": {
            "format": "weave-loupe-compiler-audit-v1",
            "status": "pass",
            "passed": True,
            "sources": [],
            "policy": policy,
            "baseline": {},
            "candidate": {},
            "comparison": {},
            "failures": [],
            "review": None,
            "seal": {
                "format": "weave-loupe-canonical-json-sha256-v1",
                "sha256": _EXAMPLE_SHA,
            },
        },
        "weave-loupe-json-validation-v1": {
            "format": "weave-loupe-json-validation-v1",
            "document_format": "weave-loupe-runtime-cases-v1",
            "valid": True,
            "problems": [],
        },
    }


_EXAMPLES = _build_examples()


def schema_formats() -> tuple[str, ...]:
    """Return every published format in deterministic order."""
    return tuple(sorted(_SCHEMAS))


def schema_document(format_name: str) -> dict[str, Any]:
    """Return an independent schema document for one public format."""
    try:
        value = _SCHEMAS[format_name]
    except KeyError:
        available = ", ".join(schema_formats())
        raise SchemaCatalogError(
            f"unknown schema format {format_name!r}; available: {available}"
        ) from None
    return copy.deepcopy(value)


def schema_example(format_name: str) -> Any:
    """Return an independent representative document for one format."""
    try:
        value = _EXAMPLES[format_name]
    except KeyError:
        raise SchemaCatalogError(
            f"schema format {format_name!r} has no representative example"
        ) from None
    return copy.deepcopy(value)


def schema_json(format_name: str) -> str:
    """Serialize one schema deterministically."""
    return (
        json.dumps(
            schema_document(format_name),
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
        + "\n"
    )


def schema_catalog_document() -> dict[str, Any]:
    """Return the complete offline schema catalog."""
    return {
        "format": SCHEMA_CATALOG_FORMAT,
        "draft": JSON_SCHEMA_DRAFT,
        "schemas": {name: schema_document(name) for name in schema_formats()},
    }


def schema_examples_document() -> dict[str, Any]:
    """Return every representative example in deterministic order."""
    return {
        "format": SCHEMA_EXAMPLES_FORMAT,
        "examples": {name: schema_example(name) for name in schema_formats()},
    }


def schema_location(format_name: str) -> str:
    """Return the installed module location plus the catalog fragment."""
    schema_document(format_name)
    return f"{Path(__file__).resolve()}#{format_name}"


def validate_document(
    document: Any,
    format_name: str | None = None,
) -> tuple[SchemaProblem, ...]:
    """Validate a JSON value against one published offline schema."""
    resolved = format_name or _document_format(document)
    schema = schema_document(resolved)
    problems: list[SchemaProblem] = []
    _validate(document, schema, "$", problems)
    return tuple(
        sorted(
            problems,
            key=lambda item: (item.path, item.keyword, item.message),
        )
    )


def require_valid_document(
    document: Any,
    format_name: str | None = None,
) -> str:
    """Validate a document and return the resolved format."""
    resolved = format_name or _document_format(document)
    problems = validate_document(document, resolved)
    if problems:
        raise SchemaValidationError(resolved, problems)
    return resolved


def _document_format(document: Any) -> str:
    if not isinstance(document, dict):
        raise SchemaCatalogError(
            "document format cannot be inferred from a non-object JSON value"
        )
    format_name = document.get("format")
    if not isinstance(format_name, str) or not format_name:
        raise SchemaCatalogError("document requires a non-empty string format field")
    return format_name


def _validate(
    value: Any,
    schema: dict[str, Any],
    path: str,
    problems: list[SchemaProblem],
) -> None:
    branches = schema.get("anyOf")
    if isinstance(branches, list):
        branch_results: list[list[SchemaProblem]] = []
        for branch in branches:
            nested: list[SchemaProblem] = []
            if isinstance(branch, dict):
                _validate(value, branch, path, nested)
            branch_results.append(nested)
        if not any(not result for result in branch_results):
            problems.append(
                SchemaProblem(
                    path,
                    "anyOf",
                    "does not match any allowed shape",
                )
            )
            return

    expected = schema.get("type")
    if expected is not None and not _matches_type(value, expected):
        problems.append(
            SchemaProblem(
                path,
                "type",
                f"expected {_type_description(expected)}, got {_json_type(value)}",
            )
        )
        return

    if "const" in schema and value != schema["const"]:
        problems.append(
            SchemaProblem(
                path,
                "const",
                f"must equal {schema['const']!r}",
            )
        )
    choices = schema.get("enum")
    if isinstance(choices, list) and value not in choices:
        problems.append(SchemaProblem(path, "enum", f"must be one of {choices!r}"))

    if isinstance(value, dict):
        _validate_object(value, schema, path, problems)
    elif isinstance(value, list):
        _validate_array(value, schema, path, problems)
    elif isinstance(value, str):
        _validate_string(value, schema, path, problems)
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        _validate_number(value, schema, path, problems)


def _validate_object(
    value: dict[Any, Any],
    schema: dict[str, Any],
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
    properties = schema.get("properties")
    known = properties if isinstance(properties, dict) else {}
    additional = schema.get("additionalProperties", True)
    for name, item in value.items():
        key = str(name)
        child_path = _property_path(path, key)
        child_schema = known.get(key)
        if isinstance(child_schema, dict):
            _validate(item, child_schema, child_path, problems)
            continue
        if additional is False:
            problems.append(
                SchemaProblem(
                    child_path,
                    "additionalProperties",
                    "unknown property",
                )
            )
        elif isinstance(additional, dict):
            _validate(item, additional, child_path, problems)


def _validate_array(
    value: list[Any],
    schema: dict[str, Any],
    path: str,
    problems: list[SchemaProblem],
) -> None:
    minimum = schema.get("minItems")
    if isinstance(minimum, int) and len(value) < minimum:
        problems.append(
            SchemaProblem(
                path,
                "minItems",
                f"requires at least {minimum} items",
            )
        )
    maximum = schema.get("maxItems")
    if isinstance(maximum, int) and len(value) > maximum:
        problems.append(
            SchemaProblem(
                path,
                "maxItems",
                f"allows at most {maximum} items",
            )
        )
    if schema.get("uniqueItems") is True:
        canonical = [json.dumps(item, sort_keys=True) for item in value]
        if len(canonical) != len(set(canonical)):
            problems.append(
                SchemaProblem(
                    path,
                    "uniqueItems",
                    "array items must be unique",
                )
            )
    item_schema = schema.get("items")
    if isinstance(item_schema, dict):
        for index, item in enumerate(value):
            _validate(item, item_schema, f"{path}[{index}]", problems)


def _validate_string(
    value: str,
    schema: dict[str, Any],
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
        problems.append(
            SchemaProblem(
                path,
                "pattern",
                f"does not match {pattern!r}",
            )
        )


def _validate_number(
    value: int | float,
    schema: dict[str, Any],
    path: str,
    problems: list[SchemaProblem],
) -> None:
    minimum = schema.get("minimum")
    if isinstance(minimum, (int, float)) and value < minimum:
        problems.append(SchemaProblem(path, "minimum", f"must be at least {minimum}"))
    maximum = schema.get("maximum")
    if isinstance(maximum, (int, float)) and value > maximum:
        problems.append(SchemaProblem(path, "maximum", f"must be at most {maximum}"))
    exclusive = schema.get("exclusiveMinimum")
    if isinstance(exclusive, (int, float)) and value <= exclusive:
        problems.append(
            SchemaProblem(
                path,
                "exclusiveMinimum",
                f"must be greater than {exclusive}",
            )
        )


def _matches_type(value: Any, expected: Any) -> bool:
    names = expected if isinstance(expected, list) else [expected]
    return any(_matches_single_type(value, name) for name in names)


def _matches_single_type(value: Any, name: Any) -> bool:
    if name == "null":
        return value is None
    if name == "boolean":
        return isinstance(value, bool)
    if name == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if name == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if name == "string":
        return isinstance(value, str)
    if name == "array":
        return isinstance(value, list)
    if name == "object":
        return isinstance(value, dict)
    return True


def _type_description(expected: Any) -> str:
    if isinstance(expected, list):
        return " or ".join(str(item) for item in expected)
    return str(expected)


def _json_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
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
