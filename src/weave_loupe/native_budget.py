"""Deterministic native-code budgets for audited compiler outputs."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from weave_loupe.runtime_cases import RUNTIME_CASES_FORMAT

NATIVE_BUDGET_FORMAT = "weave-loupe-native-budget-v1"
_NATIVE_BUDGET_RESULT_FORMAT = "weave-loupe-native-budget-result-v1"
_GLOBAL_LIMITS = {
    "max_program_owned_functions": "program_owned_functions",
    "max_reachable_program_functions": "reachable_program_functions",
    "max_unreachable_program_functions": "unreachable_program_functions",
    "max_unreachable_program_instructions": "unreachable_program_instructions",
}
_FUNCTION_LIMITS = {
    "max_instructions": "instructions",
    "max_padding_instructions": "padding_instructions",
    "max_direct_calls": "direct_calls",
    "max_indirect_calls": "indirect_calls",
}


class NativeBudgetError(ValueError):
    """Raised when a native optimization budget is invalid."""


@dataclass(frozen=True)
class NativeBudget:
    """Validated native-code limits from one adjacent audit sidecar."""

    path: Path
    global_limits: dict[str, int]
    function_limits: dict[str, dict[str, int]]


def discover_native_budget(sources: list[Path]) -> NativeBudget | None:
    """Load the single native budget adjacent to the audited sources."""
    candidates = [source.with_suffix(".audit.json") for source in sources]
    existing = [candidate for candidate in candidates if candidate.is_file()]
    if not existing:
        return None
    if len(existing) > 1:
        names = ", ".join(str(path) for path in existing)
        raise NativeBudgetError(f"multiple audit sidecars found: {names}")
    return load_native_budget(existing[0])


def load_native_budget(path: Path) -> NativeBudget | None:
    """Parse and validate an optional versioned native budget."""
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise NativeBudgetError(f"invalid audit sidecar {path}: {exc}") from exc
    if not isinstance(document, dict):
        raise NativeBudgetError("audit sidecar must be a JSON object")
    if document.get("format") != RUNTIME_CASES_FORMAT:
        raise NativeBudgetError(
            f"audit sidecar format must be {RUNTIME_CASES_FORMAT!r}"
        )

    raw_budget = document.get("native_budget")
    if raw_budget is None:
        return None
    if not isinstance(raw_budget, dict):
        raise NativeBudgetError("native_budget must be a JSON object")
    if raw_budget.get("format") != NATIVE_BUDGET_FORMAT:
        raise NativeBudgetError(
            f"native_budget format must be {NATIVE_BUDGET_FORMAT!r}"
        )

    allowed = {"format", "functions", *_GLOBAL_LIMITS}
    unknown = sorted(set(raw_budget) - allowed)
    if unknown:
        raise NativeBudgetError(
            "native_budget contains unknown fields: " + ", ".join(unknown)
        )

    global_limits = {
        key: _nonnegative_integer(raw_budget[key], f"native_budget.{key}")
        for key in _GLOBAL_LIMITS
        if key in raw_budget
    }
    function_limits = _parse_function_limits(raw_budget.get("functions", {}))
    if not global_limits and not function_limits:
        raise NativeBudgetError("native_budget must contain at least one limit")
    return NativeBudget(
        path=path,
        global_limits=global_limits,
        function_limits=function_limits,
    )


def evaluate_native_budget(
    *,
    sources: list[Path],
    native_analysis: object,
) -> dict[str, Any]:
    """Compare configured native limits with deterministic disassembly metrics."""
    budget = discover_native_budget(sources)
    if budget is None:
        return {
            "format": _NATIVE_BUDGET_RESULT_FORMAT,
            "configured": False,
            "passed": True,
            "failures": [],
        }

    failures: list[str] = []
    native = native_analysis if isinstance(native_analysis, dict) else {}
    if native.get("available") is not True:
        failures.append("linked executable disassembly is unavailable")
    if native.get("reachability_complete") is not True:
        failures.append("native program-function reachability is incomplete")

    observed_globals = _observed_global_metrics(native)
    for limit_name, observed_name in _GLOBAL_LIMITS.items():
        maximum = budget.global_limits.get(limit_name)
        if maximum is None:
            continue
        observed_count = observed_globals[observed_name]
        if observed_count > maximum:
            failures.append(
                f"{_display_name(observed_name)} {observed_count} "
                f"exceeds maximum {maximum}"
            )

    raw_functions = native.get("functions")
    functions = raw_functions if isinstance(raw_functions, dict) else {}
    observed_functions: dict[str, dict[str, int | bool]] = {}
    for name, limits in budget.function_limits.items():
        raw_details = functions.get(name)
        if not isinstance(raw_details, dict):
            observed_functions[name] = {"present": False}
            failures.append(f"required native function {name!r} is missing")
            continue
        observed_metrics = _observed_function_metrics(raw_details)
        observed_functions[name] = {"present": True, **observed_metrics}
        for limit_name, observed_name in _FUNCTION_LIMITS.items():
            maximum = limits.get(limit_name)
            if maximum is None:
                continue
            value = observed_metrics[observed_name]
            if value > maximum:
                failures.append(
                    f"function {name!r} {_display_name(observed_name)} {value} "
                    f"exceeds maximum {maximum}"
                )

    return {
        "format": _NATIVE_BUDGET_RESULT_FORMAT,
        "configured": True,
        "sidecar": str(budget.path),
        "sidecar_sha256": _sha256(budget.path.read_bytes()),
        "passed": not failures,
        "limits": {
            **dict(sorted(budget.global_limits.items())),
            "functions": {
                name: dict(sorted(limits.items()))
                for name, limits in sorted(budget.function_limits.items())
            },
        },
        "observed": {
            **observed_globals,
            "functions": observed_functions,
        },
        "failures": failures,
    }


def _parse_function_limits(value: object) -> dict[str, dict[str, int]]:
    if not isinstance(value, dict):
        raise NativeBudgetError("native_budget.functions must be a JSON object")
    parsed: dict[str, dict[str, int]] = {}
    for name, raw_limits in value.items():
        if not isinstance(name, str) or not name.strip():
            raise NativeBudgetError("native_budget function names must be non-empty")
        if not isinstance(raw_limits, dict):
            raise NativeBudgetError(
                f"native_budget function {name!r} limits must be an object"
            )
        unknown = sorted(set(raw_limits) - set(_FUNCTION_LIMITS))
        if unknown:
            raise NativeBudgetError(
                f"native_budget function {name!r} contains unknown fields: "
                + ", ".join(unknown)
            )
        limits = {
            key: _nonnegative_integer(
                raw_limits[key],
                f"native_budget.functions.{name}.{key}",
            )
            for key in _FUNCTION_LIMITS
            if key in raw_limits
        }
        if not limits:
            raise NativeBudgetError(
                f"native_budget function {name!r} must contain at least one limit"
            )
        parsed[name] = limits
    return dict(sorted(parsed.items()))


def _observed_global_metrics(native: dict[str, Any]) -> dict[str, int]:
    return {
        "program_owned_functions": _list_length(native.get("program_owned_functions")),
        "reachable_program_functions": _list_length(
            native.get("reachable_program_functions")
        ),
        "unreachable_program_functions": _list_length(
            native.get("unreachable_program_functions")
        ),
        "unreachable_program_instructions": _nonnegative_observation(
            native.get("unreachable_program_instructions")
        ),
    }


def _observed_function_metrics(details: dict[str, Any]) -> dict[str, int]:
    return {
        "instructions": _nonnegative_observation(details.get("instructions")),
        "padding_instructions": _nonnegative_observation(
            details.get("padding_instructions")
        ),
        "direct_calls": _list_length(details.get("direct_calls")),
        "indirect_calls": _nonnegative_observation(details.get("indirect_calls")),
    }


def _nonnegative_integer(value: object, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise NativeBudgetError(f"{name} must be a non-negative integer")
    return value


def _nonnegative_observation(value: object) -> int:
    if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
        return value
    return 0


def _list_length(value: object) -> int:
    return len(value) if isinstance(value, list) else 0


def _display_name(value: str) -> str:
    return value.replace("_", " ")


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()
