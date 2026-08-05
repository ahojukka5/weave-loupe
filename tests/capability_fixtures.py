from __future__ import annotations

import copy
from typing import Any


def capability_document(
    *,
    version: str = "0.1.0",
    target: str = "x86_64-unknown-linux-gnu",
) -> dict[str, Any]:
    return {
        "format": "weavec-capabilities-v1",
        "schema_id": "urn:weavec:schema:capabilities:v1",
        "schema_version": 1,
        "compiler": {
            "name": "weavec",
            "version": version,
            "public_variant": "final",
        },
        "language": {
            "name": "Weave",
            "surface_version": "weave-surface-v1",
            "grammar_id": "weave-surface-grammar-v1",
            "syntax": "s-expression",
            "case_sensitive": True,
            "wir_core_version": 2,
        },
        "protocols": [
            {
                "id": "weavec-capabilities-v1",
                "version": 1,
                "kind": "capability-registry",
            },
            {
                "id": "weavec-build-manifest-v1",
                "version": 1,
                "kind": "build-manifest",
            },
            {
                "id": "weavec-diagnostics-v1",
                "version": 1,
                "kind": "diagnostics",
            },
            {
                "id": "weavec-compilation-trace-v1",
                "version": 1,
                "kind": "compilation-trace",
            },
            {
                "id": "weave-wir-core-v2",
                "version": 2,
                "kind": "intermediate-representation",
            },
        ],
        "commands": [
            {
                "name": "capabilities",
                "spelling": "capabilities --json",
                "audience": "public-tooling",
                "status": "stable",
                "protocols": ["weavec-capabilities-v1"],
            },
            {
                "name": "build",
                "spelling": "build",
                "audience": "public",
                "status": "stable",
                "protocols": [
                    "weavec-build-manifest-v1",
                    "weavec-diagnostics-v1",
                    "weavec-compilation-trace-v1",
                ],
            },
        ],
        "targets": {
            "default": target,
            "installed": [
                {
                    "triple": target,
                    "native": True,
                    "cross_compilation": False,
                    "runtime": "static-private-target-archive",
                    "optimization_levels": ["O0", "O3"],
                    "cpu_selection": ["native"],
                }
            ],
        },
        "features": [],
        "surface": {
            "grammar_document": "docs/language-reference.md",
            "canonical_document": "docs/canonical-surface.md",
            "child_count_excludes_head": True,
            "types": ["i32", "void"],
            "operators": [
                {
                    "group": "integer-arithmetic",
                    "forms": ["add_i32"],
                    "operand_types": ["i32"],
                    "result_type": "same-as-operands",
                }
            ],
            "casts": [],
            "contextual_literals": [],
            "forms": [
                {
                    "head": "program",
                    "status": "canonical",
                    "arity": {"min_children": 2, "max_children": None},
                    "type_information": "semantic",
                    "feature": None,
                    "canonical_replacement": None,
                    "roles": [],
                }
            ],
            "compatibility_families": [],
        },
    }


def capability_document_copy(**kwargs: Any) -> dict[str, Any]:
    return copy.deepcopy(capability_document(**kwargs))
