"""Loading and pure evaluation of compiler audit policy."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any, cast

from weave_loupe.compiler_audit.comparison import stable_contract, stable_runtime
from weave_loupe.compiler_audit.model import (
    COMPILER_AUDIT_POLICY_FORMAT,
    CompilerAuditError,
    CompilerAuditPolicy,
    MetricDeltaRule,
)

_DEFAULT_RULES: dict[str, tuple[int | None, int | None]] = {
    "analysis.optimized_llvm.functions": (None, 0),
    "analysis.optimized_llvm.instructions": (None, 0),
    "analysis.optimized_llvm.alloca": (None, 0),
    "analysis.optimized_llvm.load": (None, 0),
    "analysis.optimized_llvm.store": (None, 0),
    "analysis.optimized_llvm.call": (None, 0),
    "analysis.optimized_llvm.identity_adds": (None, 0),
    "analysis.optimized_llvm.undef_uses": (None, 0),
    "analysis.optimized_llvm.poison_uses": (None, 0),
    "analysis.native.unreachable_program_instructions": (None, 0),
    "analysis.native.reachable_indirect_calls": (None, 0),
}
_POLICY_FIELDS = {"format", "metric_deltas", "forbid_changes"}
_FORBIDDEN_KINDS = {
    "diagnostics",
    "evidence",
    "runtime",
    "native_budget",
    "optimized_llvm_budget",
}
_ALWAYS_FORBIDDEN = {"runtime", "native_budget", "optimized_llvm_budget"}


def load_compiler_audit_policy(path: Path | None) -> CompilerAuditPolicy:
    """Load an optional policy and merge it with fail-closed defaults."""
    document = _read_policy(path)
    rules = {
        name: MetricDeltaRule(minimum=limits[0], maximum=limits[1])
        for name, limits in _DEFAULT_RULES.items()
    }
    raw_rules = document.get("metric_deltas", {})
    if not isinstance(raw_rules, dict):
        raise CompilerAuditError("metric_deltas must be a JSON object")
    for path_name, raw_rule in raw_rules.items():
        rules[_rule_name(path_name)] = _parse_rule(path_name, raw_rule)

    raw_forbidden = document.get("forbid_changes", ["diagnostics", "evidence"])
    if not isinstance(raw_forbidden, list) or not all(
        isinstance(item, str) for item in raw_forbidden
    ):
        raise CompilerAuditError("forbid_changes must be a list of strings")
    forbidden = set(raw_forbidden) | _ALWAYS_FORBIDDEN
    unknown = sorted(forbidden - _FORBIDDEN_KINDS)
    if unknown:
        raise CompilerAuditError(
            "forbid_changes contains unknown values: " + ", ".join(unknown)
        )
    return CompilerAuditPolicy(
        metric_deltas=dict(sorted(rules.items())),
        forbid_changes=tuple(sorted(forbidden)),
    )


def evaluate_compiler_audit_policy(
    *,
    baseline: Mapping[str, Any],
    candidate: Mapping[str, Any],
    policy: CompilerAuditPolicy,
    comparison: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Evaluate a comparison without acquiring or resolving compiler evidence."""
    metric_changes = cast(
        list[dict[str, Any]],
        comparison.get("metric_deltas", []),
    )
    failures: list[dict[str, Any]] = []
    baseline_exit = baseline.get("compiler_exit_code")
    candidate_exit = candidate.get("compiler_exit_code")
    if baseline_exit != 0:
        failures.append(
            _failure(
                "infrastructure",
                "baseline-compilation-failed",
                f"baseline compiler exited with {baseline_exit}",
            )
        )
    if baseline_exit == 0 and candidate_exit != 0:
        failures.append(
            _failure(
                "semantic",
                "candidate-compilation-failed",
                f"candidate compiler exited with {candidate_exit}",
            )
        )
    if baseline_exit != 0 or candidate_exit != 0:
        return failures

    _check_runtime(baseline, candidate, policy, failures)
    _check_contracts(baseline, candidate, policy, failures)
    _check_summaries(baseline, candidate, policy, failures)
    for delta in metric_changes:
        if delta["passed"] is True:
            continue
        if delta["available"] is not True:
            detail = f"{delta['path']} is unavailable for deterministic comparison"
        else:
            detail = (
                f"{delta['path']} delta {delta['delta']} is outside "
                f"[{delta['minimum']}, {delta['maximum']}]"
            )
        failures.append(
            _failure(
                "quality",
                "metric-delta-outside-policy",
                detail,
                evidence=delta,
            )
        )
    return failures


def _check_runtime(
    baseline: Mapping[str, Any],
    candidate: Mapping[str, Any],
    policy: CompilerAuditPolicy,
    failures: list[dict[str, Any]],
) -> None:
    before = baseline["runtime"]
    after = candidate["runtime"]
    if after.get("passed") is not True:
        failures.append(
            _failure(
                "semantic",
                "candidate-runtime-failed",
                "candidate runtime matrix did not satisfy the versioned sidecar",
            )
        )
    if "runtime" in policy.forbid_changes and stable_runtime(before) != stable_runtime(
        after
    ):
        failures.append(
            _failure(
                "semantic",
                "runtime-observations-changed",
                "candidate runtime observations differ from the baseline",
            )
        )


def _check_contracts(
    baseline: Mapping[str, Any],
    candidate: Mapping[str, Any],
    policy: CompilerAuditPolicy,
    failures: list[dict[str, Any]],
) -> None:
    for name, code in (
        ("optimized_llvm_budget", "optimized-llvm-budget-failed"),
        ("native_budget", "native-budget-failed"),
    ):
        after = candidate[name]
        if after.get("passed") is not True:
            failures.append(
                _failure(
                    "quality",
                    code,
                    f"candidate {name.replace('_', ' ')} did not pass",
                )
            )
        if name in policy.forbid_changes and stable_contract(
            baseline[name]
        ) != stable_contract(after):
            failures.append(
                _failure(
                    "quality",
                    f"{name.replace('_', '-')}-changed",
                    f"candidate {name.replace('_', ' ')} evidence differs",
                )
            )


def _check_summaries(
    baseline: Mapping[str, Any],
    candidate: Mapping[str, Any],
    policy: CompilerAuditPolicy,
    failures: list[dict[str, Any]],
) -> None:
    before = baseline["analysis"]
    after = candidate["analysis"]
    if (
        "diagnostics" in policy.forbid_changes
        and before["diagnostics"] != after["diagnostics"]
    ):
        failures.append(
            _failure(
                "semantic",
                "diagnostics-changed",
                "candidate diagnostics summary differs from the baseline",
            )
        )
    if "evidence" in policy.forbid_changes and before["evidence"] != after["evidence"]:
        failures.append(
            _failure(
                "evidence",
                "artifact-presence-changed",
                "candidate evidence availability differs from the baseline",
            )
        )


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


def _read_policy(path: Path | None) -> Mapping[str, Any]:
    if path is None:
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        message = f"invalid compiler audit policy {path}: {exc}"
        raise CompilerAuditError(message) from exc
    if not isinstance(value, dict):
        raise CompilerAuditError("compiler audit policy must be a JSON object")
    if value.get("format") != COMPILER_AUDIT_POLICY_FORMAT:
        raise CompilerAuditError(
            f"compiler audit policy format must be {COMPILER_AUDIT_POLICY_FORMAT!r}"
        )
    unknown = sorted(set(value) - _POLICY_FIELDS)
    if unknown:
        raise CompilerAuditError(
            "compiler audit policy contains unknown fields: " + ", ".join(unknown)
        )
    return value


def _rule_name(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CompilerAuditError("metric delta paths must be non-empty strings")
    return value


def _parse_rule(path_name: object, value: object) -> MetricDeltaRule:
    if not isinstance(value, dict):
        raise CompilerAuditError(
            f"metric delta rule {path_name!r} must be a JSON object"
        )
    unknown = sorted(set(value) - {"minimum", "maximum"})
    if unknown:
        raise CompilerAuditError(
            f"metric delta rule {path_name!r} contains unknown fields: "
            + ", ".join(unknown)
        )
    minimum = _optional_integer(value.get("minimum"), f"{path_name}.minimum")
    maximum = _optional_integer(value.get("maximum"), f"{path_name}.maximum")
    if minimum is None and maximum is None:
        raise CompilerAuditError(
            f"metric delta rule {path_name!r} requires minimum or maximum"
        )
    if minimum is not None and maximum is not None and minimum > maximum:
        raise CompilerAuditError(
            f"metric delta rule {path_name!r} minimum exceeds maximum"
        )
    return MetricDeltaRule(minimum=minimum, maximum=maximum)


def _optional_integer(value: object, name: str) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise CompilerAuditError(f"{name} must be an integer or null")
    return value
