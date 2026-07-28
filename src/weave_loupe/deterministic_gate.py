"""Deterministic audit checks that cannot be waived by an LLM verdict."""

from __future__ import annotations

from typing import Any

from weave_loupe.audit_result import AuditVerdict


def apply_deterministic_gate(
    verdict: AuditVerdict, analysis: dict[str, Any]
) -> AuditVerdict:
    """Reject an LLM pass when deterministic evidence proves a native defect."""
    if not verdict.passed:
        return verdict

    runtime_override = _runtime_override(verdict, analysis)
    if runtime_override is not None:
        return runtime_override

    budget_override = _native_budget_override(verdict, analysis)
    if budget_override is not None:
        return budget_override

    native = analysis.get("native")
    if not isinstance(native, dict):
        return verdict
    if native.get("reachability_complete") is not True:
        return verdict

    raw_dead = native.get("unreachable_program_functions")
    if not isinstance(raw_dead, list):
        return verdict
    dead = sorted(name for name in raw_dead if isinstance(name, str) and name)
    if not dead:
        return verdict

    instruction_count = native.get("unreachable_program_instructions", 0)
    names = ", ".join(dead)
    reason = f"unreachable program-owned native functions remain: {names}"
    override = (
        "## Deterministic gate override\n\n"
        "The model returned `OK`, but Loupe's native call-graph analysis proved "
        "that the linked standalone executable retains program-owned functions "
        "that are unreachable from `main`. This is avoidable final-binary "
        "overhead and therefore a merge-blocking compiler defect under the "
        "audit policy.\n\n"
        f"- Unreachable functions: `{names}`\n"
        f"- Non-padding instructions retained: `{instruction_count}`\n"
        "- Required fix: remove the dead functions during LLVM optimization or "
        "link-time section garbage collection."
    )
    return _failed_verdict(
        verdict,
        code="dead-native-code",
        reason=reason,
        override=override,
    )


def _runtime_override(
    verdict: AuditVerdict, analysis: dict[str, Any]
) -> AuditVerdict | None:
    runtime = analysis.get("runtime")
    if not isinstance(runtime, dict) or runtime.get("configured") is not True:
        return None
    if runtime.get("passed") is True:
        return None

    raw_cases = runtime.get("cases")
    cases = raw_cases if isinstance(raw_cases, list) else []
    failed_names: list[str] = []
    details: list[str] = []
    for item in cases:
        if not isinstance(item, dict) or item.get("passed") is True:
            continue
        name = item.get("name")
        case_name = name if isinstance(name, str) and name else "unnamed"
        failed_names.append(case_name)
        raw_failures = item.get("failures")
        failures = (
            [failure for failure in raw_failures if isinstance(failure, str)]
            if isinstance(raw_failures, list)
            else []
        )
        detail = "; ".join(failures) or "observed output did not match"
        details.append(f"- `{case_name}`: {detail}")

    names = ", ".join(failed_names) or "unknown"
    reason = f"native runtime cases failed: {names}"
    override = (
        "## Deterministic gate override\n\n"
        "The model returned `OK`, but direct execution of the linked native "
        "program disagreed with the versioned runtime expectations. A semantic "
        "mismatch in executable behavior is a merge-blocking compiler defect.\n\n"
        + ("\n".join(details) if details else "- Runtime matrix reported failure.")
        + "\n- Required fix: correct lowering or code generation, then regenerate "
        "the passing runtime evidence."
    )
    return _failed_verdict(
        verdict,
        code="runtime-mismatch",
        reason=reason,
        override=override,
    )


def _native_budget_override(
    verdict: AuditVerdict, analysis: dict[str, Any]
) -> AuditVerdict | None:
    budget = analysis.get("native_budget")
    if not isinstance(budget, dict) or budget.get("configured") is not True:
        return None
    if budget.get("passed") is True:
        return None

    raw_failures = budget.get("failures")
    failures = (
        [failure for failure in raw_failures if isinstance(failure, str)]
        if isinstance(raw_failures, list)
        else []
    )
    first = failures[0] if failures else "native optimization budget failed"
    reason = f"native optimization budget exceeded: {first}"
    details = "\n".join(f"- {failure}" for failure in failures)
    override = (
        "## Deterministic gate override\n\n"
        "The model returned `OK`, but deterministic analysis of the linked "
        "executable exceeded the versioned native optimization budget. A passing "
        "semantic result is insufficient when the compiler regresses beyond an "
        "explicit final-code quality contract.\n\n"
        + (details or "- Native optimization budget reported failure.")
        + "\n- Required fix: restore the native-code limits or deliberately review "
        "and update the versioned budget with new evidence."
    )
    return _failed_verdict(
        verdict,
        code="native-budget-exceeded",
        reason=reason,
        override=override,
    )


def _failed_verdict(
    verdict: AuditVerdict,
    *,
    code: str,
    reason: str,
    override: str,
) -> AuditVerdict:
    body = verdict.body.rstrip()
    body = f"{body}\n\n{override}" if body else override
    return AuditVerdict(
        status="FAILED",
        code=code,
        reason=reason,
        body=body,
    )
