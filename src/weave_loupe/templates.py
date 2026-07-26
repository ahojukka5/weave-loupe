"""Prompt templates for compiler-evidence audits."""

from __future__ import annotations

AUDIT_REPORT_TEMPLATE = """\
# Weave Loupe Audit Report

## Summary
State overall correctness risk and whether the emitted LLVM is performance-ready.
Attribute each important observation to source, WIR, or LLVM generation.

## Serious issues
List correctness, safety, undefined-behavior, control-flow, SSA, or lowering
problems. Use `None found.` when evidence does not support a serious issue.

For each issue use:

### Issue: <short title>
- Severity: critical | high | medium
- Stage: Weave | WIR | LLVM
- Location: function or source range
- Evidence: concrete artifact evidence
- Why it matters: concrete failure mode
- Suggestion: specific fix

## Performance opportunities
Identify avoidable instructions, memory traffic, control flow, missed folding,
or other work. Distinguish algorithmic cost from compiler-generated overhead.

For each opportunity use:

### Opportunity: <short title>
- Impact: high | medium | low
- Stage: Weave | WIR | LLVM
- Location: function, trace action, or source range
- Evidence: concrete artifact evidence
- Ideal shape: tighter result
- Suggestion: specific compiler or source change

## Algorithmic notes
Discuss asymptotic complexity and better algorithms separately from lowering.
Use `None found.` when the source algorithm is already appropriate.

## Suggested next steps
Number the highest-value follow-ups, most important first.
"""

AUDIT_PROMPT_TEMPLATE = """\
You are an expert Weave, WIR, and LLVM compiler reviewer.

Inspect the complete evidence bundle below. We want generated LLVM that is as
close as practical to the optimum shape for the source algorithm. Do not invent
problems. Attribute each finding to the stage that introduced it. Use source and
WIR provenance comments, trace actions, diagnostics, and structural metrics as
supporting evidence.

Source paths: {source_path}

=== Weave source ===
{weave_source}
=== End Weave source ===

=== WIR ===
{wir}
=== End WIR ===

=== LLVM IR ===
{llvm_ir}
=== End LLVM IR ===

=== Diagnostics JSON ===
{diagnostics_json}
=== End diagnostics ===

=== Trace summary JSON ===
{trace_summary_json}
=== End trace summary ===

=== LLVM metrics JSON ===
{llvm_metrics_json}
=== End LLVM metrics ===

=== Report template ===
{report_template}
=== End report template ===
"""


def render_audit_prompt(
    *,
    source_path: str,
    weave_source: str,
    wir: str,
    llvm_ir: str,
    diagnostics_json: str = "null",
    trace_summary_json: str = "{}",
    llvm_metrics_json: str = "{}",
) -> str:
    """Insert evidence without treating artifact braces as format syntax."""
    return (
        AUDIT_PROMPT_TEMPLATE.replace("{source_path}", source_path)
        .replace("{weave_source}", weave_source)
        .replace("{wir}", wir)
        .replace("{llvm_ir}", llvm_ir)
        .replace("{diagnostics_json}", diagnostics_json)
        .replace("{trace_summary_json}", trace_summary_json)
        .replace("{llvm_metrics_json}", llvm_metrics_json)
        .replace("{report_template}", AUDIT_REPORT_TEMPLATE)
    )
