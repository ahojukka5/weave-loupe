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
_FUNCTION_MAXIMUMS = {
    "max_instructions": "instructions",
    "max_padding_instructions": "padding_instructions",
    "max_direct_calls": "direct_calls",
    "max_indirect_calls": "indirect_calls",
    "max_backward_conditional_branches": "backward_conditional_branches",
}
_FUNCTION_MINIMUMS = {
    "min_backward_conditional_branches": "backward_conditional_branches",
}
_REQUIRED_DIRECT_CALLS = "required_direct_calls"


class NativeBudgetError(ValueError):
    """Raised when a native optimization budget is invalid."""


@dataclass(frozen=True)
class FunctionContract:
    """Validated limits and required native structure for one function."""

    maximums: dict[str, int]
    minimums: dict[str, int]
    required_direct_calls: tuple[str, ...]

    def metadata(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            **dict(sorted(self.maximums.items())),
            **dict(sorted(self.minimums.items())),
        }
        if self.required_direct_calls:
            result[_REQUIRED_DIRECT_CALLS] = list(self.required_direct_calls)
        return result


@dataclass(frozen=True)
class NativeBudget:
    """Validated native-code limits from one adjacent audit sidecar."""

    path: Path
    global_limits: dict[str, int]
    function_contracts: dict[str, FunctionContract]


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
    function_contracts = _parse_function_contracts(raw_budget.get("functions", {}))
    if not global_limits and not function_contracts:
        raise NativeBudgetError("native_budget must contain at least one limit")
    return NativeBudget(
        path=path,
        global_limits=global_limits,
        function_contracts=function_contracts,
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
    observed_functions: dict[str, dict[str, Any]] = {}
    for name, contract in budget.function_contracts.items():
        raw_details = functions.get(name)
        if not isinstance(raw_details, dict):
            observed_functions[name] = {"present": False}
            failures.append(f"required native function {name!r} is missing")
            continue
        observed_metrics = _observed_function_metrics(raw_details)
        observed_calls = _string_set(raw_details.get("direct_calls"))
        observed_functions[name] = {
            "present": True,
            **observed_metrics,
            "direct_call_targets": sorted(observed_calls),
        }
        _check_function_maximums(
            name=name,
            contract=contract,
            observed=observed_metrics,
            failures=failures,
        )
        _check_function_minimums(
            name=name,
            contract=contract,
            observed=observed_metrics,
            failures=failures,
        )
        missing_calls = sorted(set(contract.required_direct_calls) - observed_calls)
        if missing_calls:
            failures.append(
                f"function {name!r} missing required direct calls: "
                + ", ".join(missing_calls)
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
                name: contract.metadata()
                for name, contract in sorted(budget.function_contracts.items())
            },
        },
        "observed": {
            **observed_globals,
            "functions": observed_functions,
        },
        "failures": failures,
    }


def _parse_function_contracts(value: object) -> dict[str, FunctionContract]:
    if not isinstance(value, dict):
        raise NativeBudgetError("native_budget.functions must be a JSON object")
    parsed: dict[str, FunctionContract] = {}
    allowed = {
        *_FUNCTION_MAXIMUMS,
        *_FUNCTION_MINIMUMS,
        _REQUIRED_DIRECT_CALLS,
    }
    for name, raw_contract in value.items():
        if not isinstance(name, str) or not name.strip():
            raise NativeBudgetError("native_budget function names must be non-empty")
        if not isinstance(raw_contract, dict):
            raise NativeBudgetError(
                f"native_budget function {name!r} limits must be an object"
            )
        unknown = sorted(set(raw_contract) - allowed)
        if unknown:
            raise NativeBudgetError(
                f"native_budget function {name!r} contains unknown fields: "
                + ", ".join(unknown)
            )
        maximums = {
            key: _nonnegative_integer(
                raw_contract[key],
                f"native_budget.functions.{name}.{key}",
            )
            for key in _FUNCTION_MAXIMUMS
            if key in raw_contract
        }
        minimums = {
            key: _nonnegative_integer(
                raw_contract[key],
                f"native_budget.functions.{name}.{key}",
            )
            for key in _FUNCTION_MINIMUMS
            if key in raw_contract
        }
        required_calls = _required_call_list(
            raw_contract.get(_REQUIRED_DIRECT_CALLS, []),
            f"native_budget.functions.{name}.{_REQUIRED_DIRECT_CALLS}",
        )
        if not maximums and not minimums and not required_calls:
            raise NativeBudgetError(
                f"native_budget function {name!r} must contain at least one contract"
            )
        minimum = minimums.get("min_backward_conditional_branches")
        maximum = maximums.get("max_backward_conditional_branches")
        if minimum is not None and maximum is not None and minimum > maximum:
            raise NativeBudgetError(
                f"native_budget function {name!r} backward branch minimum "
                "must not exceed its maximum"
            )
        parsed[name] = FunctionContract(
            maximums=maximums,
            minimums=minimums,
            required_direct_calls=required_calls,
        )
    return dict(sorted(parsed.items()))


def _check_function_maximums(
    *,
    name: str,
    contract: FunctionContract,
    observed: dict[str, int],
    failures: list[str],
) -> None:
    for contract_name, observed_name in _FUNCTION_MAXIMUMS.items():
        maximum = contract.maximums.get(contract_name)
        if maximum is None:
            continue
        value = observed[observed_name]
        if value > maximum:
            failures.append(
                f"function {name!r} {_display_name(observed_name)} {value} "
                f"exceeds maximum {maximum}"
            )


def _check_function_minimums(
    *,
    name: str,
    contract: FunctionContract,
    observed: dict[str, int],
    failures: list[str],
) -> None:
    for contract_name, observed_name in _FUNCTION_MINIMUMS.items():
        minimum = contract.minimums.get(contract_name)
        if minimum is None:
            continue
        value = observed[observed_name]
        if value < minimum:
            failures.append(
                f"function {name!r} {_display_name(observed_name)} {value} "
                f"is below minimum {minimum}"
            )


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
        "backward_conditional_branches": _nonnegative_observation(
            details.get("backward_conditional_branches")
        ),
    }


def _required_call_list(value: object, name: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        raise NativeBudgetError(f"{name} must be a list of non-empty strings")
    calls = [item.strip() for item in value]
    if len(calls) != len(set(calls)):
        raise NativeBudgetError(f"{name} must not contain duplicates")
    return tuple(sorted(calls))


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


def _string_set(value: object) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {item for item in value if isinstance(item, str) and item}


def _display_name(value: str) -> str:
    return value.replace("_", " ")


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()
