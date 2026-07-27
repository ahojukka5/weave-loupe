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
    body = verdict.body.rstrip()
    body = f"{body}\n\n{override}" if body else override
    return AuditVerdict(
        status="FAILED",
        code="dead-native-code",
        reason=reason,
        body=body,
    )
