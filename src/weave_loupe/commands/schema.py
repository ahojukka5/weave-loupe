"""Schema publication and offline JSON validation commands."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from weave_loupe.schemas import (
    JSON_VALIDATION_FORMAT,
    SchemaCatalogError,
    SchemaProblem,
    schema_json,
    validate_document,
)


def run_schema(*, format_name: str, output: Path | None) -> int:
    """Print or write one deterministic JSON Schema document."""
    try:
        content = schema_json(format_name)
        if output is None:
            sys.stdout.write(content)
        else:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(content, encoding="utf-8")
            print(f"schema: {output.resolve()}")
        return 0
    except (OSError, SchemaCatalogError) as exc:
        print(f"loupe schema: {exc}", file=sys.stderr)
        return 1


def run_validate_json(
    *,
    document: Path,
    format_name: str | None,
    json_out: Path | None,
) -> int:
    """Validate one JSON document without network access."""
    try:
        value = json.loads(document.read_text(encoding="utf-8"))
        resolved_format = format_name or _document_format(value)
        problems = validate_document(value, resolved_format)
        result = _result_document(resolved_format, problems)
        if json_out is not None:
            json_out.parent.mkdir(parents=True, exist_ok=True)
            json_out.write_text(
                json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
        if problems:
            print(f"INVALID: {document}")
            for problem in problems:
                print(f"- {problem.path} [{problem.keyword}]: {problem.message}")
            return 2
        print(f"VALID: {document} ({resolved_format})")
        return 0
    except (OSError, json.JSONDecodeError, SchemaCatalogError) as exc:
        print(f"loupe validate-json: {exc}", file=sys.stderr)
        return 1


def _document_format(value: Any) -> str:
    if not isinstance(value, dict):
        raise SchemaCatalogError(
            "document format cannot be inferred from a non-object JSON value"
        )
    format_name = value.get("format")
    if not isinstance(format_name, str) or not format_name:
        raise SchemaCatalogError("document requires a non-empty string format field")
    return format_name


def _result_document(
    format_name: str,
    problems: tuple[SchemaProblem, ...],
) -> dict[str, Any]:
    return {
        "format": JSON_VALIDATION_FORMAT,
        "document_format": format_name,
        "valid": not problems,
        "problems": [
            {
                "code": problem.keyword,
                "location": problem.path,
                "message": problem.message,
            }
            for problem in problems
        ],
    }
