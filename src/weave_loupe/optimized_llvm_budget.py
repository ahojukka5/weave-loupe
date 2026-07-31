"""Deterministic contracts for the exact optimized LLVM module."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from weave_loupe.runtime_cases import RUNTIME_CASES_FORMAT

OPTIMIZED_LLVM_BUDGET_FORMAT = "weave-loupe-optimized-llvm-budget-v1"
_OPTIMIZED_LLVM_RESULT_FORMAT = "weave-loupe-optimized-llvm-budget-result-v1"
_DEFINED_FUNCTION = re.compile(r'^\s*define\b.*?@(?:"([^"]+)"|([-A-Za-z$._0-9]+))\s*\(')
_DIRECT_CALL_TARGET = re.compile(
    r'\b(?:call|invoke)\b[^@]*@(?:"([^"]+)"|([-A-Za-z$._0-9]+))\s*\('
)
_TRACKED_METRICS = (
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
)
_MAXIMUMS = {f"max_{metric}": metric for metric in _TRACKED_METRICS}
_MINIMUMS = {f"min_{metric}": metric for metric in _TRACKED_METRICS}
_REQUIRED_FUNCTIONS = "required_defined_functions"
_REQUIRED_CALLS = "required_call_targets"


class OptimizedLlvmBudgetError(ValueError):
    """Raised when an optimized LLVM contract is invalid."""


@dataclass(frozen=True)
class OptimizedLlvmBudget:
    """Validated post-optimization limits and structural requirements."""

    path: Path
    maximums: dict[str, int]
    minimums: dict[str, int]
    required_functions: tuple[str, ...]
    required_calls: tuple[str, ...]

    def metadata(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            **dict(sorted(self.maximums.items())),
            **dict(sorted(self.minimums.items())),
        }
        if self.required_functions:
            result[_REQUIRED_FUNCTIONS] = list(self.required_functions)
        if self.required_calls:
            result[_REQUIRED_CALLS] = list(self.required_calls)
        return result


def discover_optimized_llvm_budget(
    sources: list[Path],
) -> OptimizedLlvmBudget | None:
    """Load the single optimized LLVM contract adjacent to audited sources."""
    candidates = [source.with_suffix(".audit.json") for source in sources]
    existing = [candidate for candidate in candidates if candidate.is_file()]
    if not existing:
        return None
    if len(existing) > 1:
        names = ", ".join(str(path) for path in existing)
        raise OptimizedLlvmBudgetError(f"multiple audit sidecars found: {names}")
    return load_optimized_llvm_budget(existing[0])


def load_optimized_llvm_budget(path: Path) -> OptimizedLlvmBudget | None:
    """Parse and validate an optional optimized LLVM contract."""
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise OptimizedLlvmBudgetError(f"invalid audit sidecar {path}: {exc}") from exc
    if not isinstance(document, dict):
        raise OptimizedLlvmBudgetError("audit sidecar must be a JSON object")
    if document.get("format") != RUNTIME_CASES_FORMAT:
        raise OptimizedLlvmBudgetError(
            f"audit sidecar format must be {RUNTIME_CASES_FORMAT!r}"
        )

    raw_budget = document.get("optimized_llvm_budget")
    if raw_budget is None:
        return None
    if not isinstance(raw_budget, dict):
        raise OptimizedLlvmBudgetError("optimized_llvm_budget must be a JSON object")
    if raw_budget.get("format") != OPTIMIZED_LLVM_BUDGET_FORMAT:
        raise OptimizedLlvmBudgetError(
            f"optimized_llvm_budget format must be {OPTIMIZED_LLVM_BUDGET_FORMAT!r}"
        )

    allowed = {
        "format",
        _REQUIRED_FUNCTIONS,
        _REQUIRED_CALLS,
        *_MAXIMUMS,
        *_MINIMUMS,
    }
    unknown = sorted(set(raw_budget) - allowed)
    if unknown:
        raise OptimizedLlvmBudgetError(
            "optimized_llvm_budget contains unknown fields: " + ", ".join(unknown)
        )

    maximums = {
        key: _nonnegative_integer(
            raw_budget[key],
            f"optimized_llvm_budget.{key}",
        )
        for key in _MAXIMUMS
        if key in raw_budget
    }
    minimums = {
        key: _nonnegative_integer(
            raw_budget[key],
            f"optimized_llvm_budget.{key}",
        )
        for key in _MINIMUMS
        if key in raw_budget
    }
    required_functions = _required_names(
        raw_budget.get(_REQUIRED_FUNCTIONS, []),
        f"optimized_llvm_budget.{_REQUIRED_FUNCTIONS}",
    )
    required_calls = _required_names(
        raw_budget.get(_REQUIRED_CALLS, []),
        f"optimized_llvm_budget.{_REQUIRED_CALLS}",
    )
    if not maximums and not minimums and not required_functions and not required_calls:
        raise OptimizedLlvmBudgetError(
            "optimized_llvm_budget must contain at least one contract"
        )
    for maximum_name, metric in _MAXIMUMS.items():
        minimum_name = f"min_{metric}"
        maximum = maximums.get(maximum_name)
        minimum = minimums.get(minimum_name)
        if maximum is not None and minimum is not None and minimum > maximum:
            raise OptimizedLlvmBudgetError(
                f"optimized_llvm_budget {metric} minimum must not exceed its maximum"
            )
    return OptimizedLlvmBudget(
        path=path,
        maximums=maximums,
        minimums=minimums,
        required_functions=required_functions,
        required_calls=required_calls,
    )


def evaluate_optimized_llvm_budget(
    *,
    sources: list[Path],
    optimized_llvm: str,
    metrics: object,
) -> dict[str, Any]:
    """Compare the post-optimization module with its versioned contract."""
    budget = discover_optimized_llvm_budget(sources)
    if budget is None:
        return {
            "format": _OPTIMIZED_LLVM_RESULT_FORMAT,
            "configured": False,
            "passed": True,
            "failures": [],
        }

    failures: list[str] = []
    if not optimized_llvm.strip():
        failures.append("optimized LLVM IR is unavailable")
    observed_metrics = _observed_metrics(metrics)
    for contract_name, metric in _MAXIMUMS.items():
        maximum = budget.maximums.get(contract_name)
        if maximum is None:
            continue
        observed = observed_metrics[metric]
        if observed > maximum:
            failures.append(
                f"optimized LLVM {metric.replace('_', ' ')} {observed} "
                f"exceeds maximum {maximum}"
            )
    for contract_name, metric in _MINIMUMS.items():
        minimum = budget.minimums.get(contract_name)
        if minimum is None:
            continue
        observed = observed_metrics[metric]
        if observed < minimum:
            failures.append(
                f"optimized LLVM {metric.replace('_', ' ')} {observed} "
                f"is below minimum {minimum}"
            )

    defined_functions = _defined_functions(optimized_llvm)
    call_targets = _direct_call_targets(optimized_llvm)
    missing_functions = sorted(set(budget.required_functions) - defined_functions)
    if missing_functions:
        failures.append(
            "optimized LLVM missing required defined functions: "
            + ", ".join(missing_functions)
        )
    missing_calls = sorted(set(budget.required_calls) - call_targets)
    if missing_calls:
        failures.append(
            "optimized LLVM missing required call targets: " + ", ".join(missing_calls)
        )

    return {
        "format": _OPTIMIZED_LLVM_RESULT_FORMAT,
        "configured": True,
        "sidecar": str(budget.path),
        "sidecar_sha256": _sha256(budget.path.read_bytes()),
        "passed": not failures,
        "limits": budget.metadata(),
        "observed": {
            **observed_metrics,
            "defined_functions": sorted(defined_functions),
            "call_targets": sorted(call_targets),
        },
        "failures": failures,
    }


def _observed_metrics(value: object) -> dict[str, int]:
    metrics = value if isinstance(value, dict) else {}
    return {
        name: _nonnegative_observation(metrics.get(name)) for name in _TRACKED_METRICS
    }


def _defined_functions(llvm_ir: str) -> set[str]:
    names: set[str] = set()
    for line in llvm_ir.splitlines():
        match = _DEFINED_FUNCTION.match(line)
        if match is not None:
            names.add(match.group(1) or match.group(2))
    return names


def _direct_call_targets(llvm_ir: str) -> set[str]:
    names: set[str] = set()
    for line in llvm_ir.splitlines():
        match = _DIRECT_CALL_TARGET.search(line)
        if match is not None:
            names.add(match.group(1) or match.group(2))
    return names


def _required_names(value: object, name: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        raise OptimizedLlvmBudgetError(f"{name} must be a list of non-empty strings")
    names = [item.strip() for item in value]
    if len(names) != len(set(names)):
        raise OptimizedLlvmBudgetError(f"{name} must not contain duplicates")
    return tuple(sorted(names))


def _nonnegative_integer(value: object, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise OptimizedLlvmBudgetError(f"{name} must be a non-negative integer")
    return value


def _nonnegative_observation(value: object) -> int:
    if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
        return value
    return 0


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()
