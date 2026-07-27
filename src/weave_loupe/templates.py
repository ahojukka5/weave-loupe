"""Prompt templates for compiler-evidence audits."""

from __future__ import annotations

AUDIT_REPORT_TEMPLATE = """\
## Summary
State the concrete audit conclusion. Attribute each important observation to
Weave source, WIR, raw LLVM, optimized LLVM, target assembly, linked executable
disassembly, or the optimization record.

## Blocking findings
List only findings that justify a failed gate: incorrect behavior, invalid SSA
or IR, undefined behavior, memory unsafety or leakage, target incompatibility,
or substantial compiler-generated overhead that remains in optimized LLVM or
final machine code. Use `None found.` when no blocking finding is supported.

For each finding use:

### Finding: <short title>
- Code: lowercase-kebab-case
- Severity: critical | high | medium
- Stage: Weave | WIR | raw LLVM | optimized LLVM | native code
- Location: function or source range
- Evidence: concrete artifact evidence
- Failure mode: concrete consequence
- Required fix: specific correction

## Non-blocking opportunities
Identify worthwhile but non-gating improvements. Distinguish source algorithm
cost from compiler-generated overhead. Raw LLVM stack traffic or temporary
instructions are not defects when optimized LLVM and final native code remove
them.

## Suggested verification
List focused tests, measurements, or comparisons that would increase confidence.
"""

AUDIT_PROMPT_TEMPLATE = """\
You are the release-gate reviewer for the Weave compiler toolchain.

Your first output line is a strict machine protocol. It MUST be exactly one of:

OK
FAILED: <lowercase-kebab-code>: <one-line reason>

Do not emit a preamble, Markdown fence, heading, or whitespace before that line.
After it, write the Markdown review using the supplied template.

Return FAILED only when the evidence supports a merge-blocking defect:
incorrect behavior, invalid SSA or LLVM IR, undefined behavior, memory unsafety
or memory leakage, target incompatibility, or substantial compiler-generated
overhead that remains in optimized LLVM or final machine code. A speculative
idea, style preference, source-level algorithm alternative, or inefficiency
that disappears during LLVM optimization is non-blocking. Do not invent
problems. When evidence is incomplete, state the limitation without converting
it into a failure unless the missing evidence itself makes the claimed result
unverifiable.

Source paths: {source_path}

=== Reproducibility metadata JSON ===
{metadata_json}
=== End reproducibility metadata ===

=== Weave source ===
{weave_source}
=== End Weave source ===

=== WIR ===
{wir}
=== End WIR ===

=== Raw LLVM IR ===
{llvm_ir}
=== End raw LLVM IR ===

=== Optimized LLVM IR ===
{optimized_llvm}
=== End optimized LLVM IR ===

=== Target assembly ===
{assembly}
=== End target assembly ===

=== Linked executable disassembly ===
{disassembly}
=== End linked executable disassembly ===

=== LLVM optimization record ===
{optimization_record}
=== End optimization record ===

=== Diagnostics JSON ===
{diagnostics_json}
=== End diagnostics ===

=== Complete analysis JSON ===
{analysis_json}
=== End analysis ===

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
    optimized_llvm: str = "",
    assembly: str = "",
    disassembly: str = "",
    optimization_record: str = "",
    diagnostics_json: str = "null",
    analysis_json: str = "{}",
    metadata_json: str = "{}",
) -> str:
    """Insert evidence without treating artifact braces as format syntax."""
    replacements = {
        "{source_path}": source_path,
        "{weave_source}": weave_source,
        "{wir}": wir,
        "{llvm_ir}": llvm_ir,
        "{optimized_llvm}": optimized_llvm,
        "{assembly}": assembly,
        "{disassembly}": disassembly,
        "{optimization_record}": optimization_record,
        "{diagnostics_json}": diagnostics_json,
        "{analysis_json}": analysis_json,
        "{metadata_json}": metadata_json,
        "{report_template}": AUDIT_REPORT_TEMPLATE,
    }
    prompt = AUDIT_PROMPT_TEMPLATE
    for marker, value in replacements.items():
        prompt = prompt.replace(marker, value)
    return prompt
