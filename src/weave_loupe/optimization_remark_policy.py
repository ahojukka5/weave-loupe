"""Versioned compiler-audit policy for LLVM optimization remarks."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from weave_loupe.compiler_audit import (
    COMPILER_AUDIT_POLICY_FORMAT,
    CompilerAuditError,
)
from weave_loupe.optimization_remarks import remark_matches

_POLICY_FIELD = "optimization_remarks"
_RULE_NAMES = ("required", "forbidden", "forbid_added", "forbid_removed")
_SELECTOR_FIELDS = {
    "category",
    "pass",
    "name",
    "function",
    "message_contains",
}
_CATEGORIES = {
    "passed",
    "missed",
    "analysis",
    "failure",
    "analysis-fp-commute",
    "unsupported",
}


def load_optimization_remark_policy(path: Path | None) -> dict[str, Any]:
    """Load and normalize the optimization remark portion of an audit policy."""
    document = _read_document(path)
    raw = document.get(_POLICY_FIELD, {})
    if not isinstance(raw, Mapping):
        raise CompilerAuditError(f"{_POLICY_FIELD} must be a JSON object")
    unknown = sorted(set(str(key) for key in raw) - set(_RULE_NAMES))
    if unknown:
        raise CompilerAuditError(
            f"{_POLICY_FIELD} contains unknown fields: " + ", ".join(unknown)
        )
    return {
        name: _selectors(raw.get(name, []), f"{_POLICY_FIELD}.{name}")
        for name in _RULE_NAMES
    }


def base_policy_path(path: Path | None, destination: Path) -> Path | None:
    """Write a core-policy projection without the extension field."""
    if path is None:
        return None
    document = _read_document(path)
    if _POLICY_FIELD not in document:
        return path
    projected = dict(document)
    projected.pop(_POLICY_FIELD, None)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(projected, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return destination


def evaluate_optimization_remark_policy(
    policy: Mapping[str, Any],
    baseline: Mapping[str, Any],
    candidate: Mapping[str, Any],
    comparison: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Evaluate remark validity and selector rules deterministically."""
    failures: list[dict[str, Any]] = []
    before = _remarks(baseline)
    after = _remarks(candidate)
    if before.get("available") is True and before.get("valid") is not True:
        failures.append(
            _failure(
                "infrastructure",
                "baseline-optimization-remarks-invalid",
                str(
                    before.get("failure_reason")
                    or "baseline optimization remarks are invalid"
                ),
            )
        )
    if before.get("valid") is True and after.get("valid") is not True:
        failures.append(
            _failure(
                "quality",
                "candidate-optimization-remarks-invalid",
                str(
                    after.get("failure_reason")
                    or "candidate optimization remarks are invalid"
                ),
            )
        )

    candidate_records = _records(after.get("records"))
    diff = _mapping(comparison.get("optimization_remarks"))
    checks = (
        (
            "required",
            candidate_records,
            False,
            "required-optimization-remark-missing",
            "required optimization remark is absent from the candidate",
        ),
        (
            "forbidden",
            candidate_records,
            True,
            "forbidden-optimization-remark-present",
            "forbidden optimization remark is present in the candidate",
        ),
        (
            "forbid_added",
            _records(diff.get("added")),
            True,
            "forbidden-optimization-remark-added",
            "candidate added a forbidden optimization remark",
        ),
        (
            "forbid_removed",
            _records(diff.get("removed")),
            True,
            "forbidden-optimization-remark-removed",
            "candidate removed a protected optimization remark",
        ),
    )
    for rule_name, records, fail_on_match, code, detail in checks:
        for selector in _policy_selectors(policy.get(rule_name)):
            matches = [record for record in records if remark_matches(record, selector)]
            failed = bool(matches) if fail_on_match else not matches
            if not failed:
                continue
            evidence: dict[str, Any] = {"selector": selector}
            if matches:
                evidence["matches"] = matches
            failures.append(_failure("quality", code, detail, evidence=evidence))
    return failures


def _read_document(path: Path | None) -> Mapping[str, Any]:
    if path is None:
        return {}
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        message = f"invalid compiler audit policy {path}: {exc}"
        raise CompilerAuditError(message) from exc
    if not isinstance(document, Mapping):
        raise CompilerAuditError("compiler audit policy must be a JSON object")
    if document.get("format") != COMPILER_AUDIT_POLICY_FORMAT:
        raise CompilerAuditError(
            f"compiler audit policy format must be {COMPILER_AUDIT_POLICY_FORMAT!r}"
        )
    return document


def _selectors(value: object, name: str) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise CompilerAuditError(f"{name} must be a list of selector objects")
    selectors = [
        _selector(item, f"{name}[{index}]") for index, item in enumerate(value)
    ]
    return sorted(selectors, key=_selector_key)


def _selector(value: object, name: str) -> dict[str, str]:
    if not isinstance(value, Mapping):
        raise CompilerAuditError(f"{name} must be a JSON object")
    unknown = sorted(set(str(key) for key in value) - _SELECTOR_FIELDS)
    if unknown:
        fields = ", ".join(unknown)
        raise CompilerAuditError(f"{name} contains unknown fields: {fields}")
    selector: dict[str, str] = {}
    for key, raw in value.items():
        field = str(key)
        if not isinstance(raw, str) or not raw:
            raise CompilerAuditError(f"{name}.{field} must be a non-empty string")
        selector[field] = raw
    if not selector:
        raise CompilerAuditError(f"{name} must select at least one remark field")
    category = selector.get("category")
    if category is not None and category not in _CATEGORIES:
        raise CompilerAuditError(f"{name}.category has unknown value {category!r}")
    return dict(sorted(selector.items()))


def _selector_key(selector: Mapping[str, str]) -> tuple[str, ...]:
    return tuple(selector.get(name, "") for name in sorted(_SELECTOR_FIELDS))


def _remarks(result: Mapping[str, Any]) -> Mapping[str, Any]:
    analysis = _mapping(result.get("analysis"))
    return _mapping(analysis.get("optimization_remarks"))


def _records(value: object) -> list[dict[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [dict(item) for item in value if isinstance(item, Mapping)]


def _policy_selectors(value: object) -> list[dict[str, str]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [
        {str(key): str(item) for key, item in selector.items()}
        for selector in value
        if isinstance(selector, Mapping)
    ]


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _failure(
    category: str,
    code: str,
    detail: str,
    *,
    evidence: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "category": category,
        "code": code,
        "detail": detail,
    }
    if evidence is not None:
        result["evidence"] = dict(evidence)
    return result
