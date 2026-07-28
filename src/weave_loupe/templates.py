"""Prompt templates for compiler-evidence audits."""

from __future__ import annotations

AUDIT_REPORT_TEMPLATE = """\
## Summary
State the concrete audit conclusion. Attribute each important observation to
Weave source, cleaned WIR, raw LLVM, optimized LLVM, target assembly, linked
executable disassembly, direct runtime execution, the native optimization budget,
or the optimization record.

## Verification matrix
For every row below, write `PASS`, `FAIL`, or `UNVERIFIED` and cite concrete
artifact evidence. Do not omit a row.

- Source semantics and expected result
- Weave-to-WIR semantic preservation
- WIR-to-raw-LLVM semantic preservation
- Raw LLVM validity, SSA, types, and control flow
- Optimized LLVM semantic preservation
- Integer signedness, overflow, shifts, and comparisons
- Calls, return values, ABI, stack alignment, and register use
- Memory safety, lifetime, leaks, and undefined behavior
- Target compatibility and native instruction validity
- Native runtime cases and expected observable behavior
- Configured native limits, required call targets, and loop backedges
- Compiler-generated overhead remaining in final native code

An `UNVERIFIED` result is acceptable only for a genuinely nonessential property.
If correctness, safety, ABI compatibility, or the claimed final-code quality is
unverifiable from the supplied evidence, the gate must fail with code
`insufficient-evidence`.

## Blocking findings
List every finding that justifies a failed gate: incorrect behavior, invalid SSA
or IR, undefined behavior, memory unsafety or leakage, target incompatibility,
ABI violation, failed runtime expectations, exceeded native optimization limits,
missing required native structure, or substantial compiler-generated overhead that
remains in optimized LLVM or final machine code. Use `None found.` only when every
essential verification-matrix row has affirmative evidence.

For each finding use:

### Finding: <short title>
- Code: lowercase-kebab-case
- Severity: critical | high | medium
- Stage: Weave | WIR | raw LLVM | optimized LLVM | native code | native execution
- Location: function, source range, or runtime case
- Evidence: concrete artifact or execution evidence
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
You are the adversarial release-gate reviewer for the Weave compiler toolchain.
Your job is to try to falsify the claim that the final native program is correct,
safe, ABI-valid, target-compatible, and free from avoidable compiler-generated
overhead.

Your first output line is a strict machine protocol. It MUST be exactly one of:

OK
FAILED: <lowercase-kebab-code>: <one-line reason>

Do not emit a preamble, Markdown fence, heading, or whitespace before that line.
After it, write the Markdown review using the supplied template.

Do not infer correctness from successful compilation, LLVM optimization, or a
plausible-looking final instruction sequence. Independently trace the expected
source behavior through cleaned WIR, raw LLVM, optimized LLVM, target assembly,
linked executable disassembly, and any direct runtime matrix in the complete
analysis JSON. Inspect final native code instruction by instruction, including
calls, returns, signed comparisons, arithmetic width, register values, stack
behavior, ABI rules, and control-flow edges. Cross-check all stages against each
other, the deterministic analysis, runtime observations, native optimization
budget, and optimization remarks.

A configured runtime matrix is direct evidence from executing the exact linked
artifact. Its expected values come from a versioned, hash-addressed sidecar. Any
failed case is a semantic defect even when the static artifacts look plausible.
When no matrix is configured, do not invent runtime observations.

A configured native optimization budget is a versioned contract for measured
linked-executable properties. Verify maximum and minimum metrics, required direct
call targets, and required loop backedges against the complete analysis JSON. An
exceeded maximum, unmet minimum, or missing required call is a final-code quality
regression. A passing contract does not by itself prove theoretical optimality:
still inspect the disassembly and identify avoidable overhead that the current
ceiling permits. Improvements below the ceiling remain welcome and do not require
weakening the contract.

The WIR shown below is a review projection of the exact captured artifact. Only
source-file and source-span provenance comments are hidden, and whitespace is
normalized. Semantic tokens and structure are preserved. The raw WIR remains
hash-addressed in the bundle and may be exported separately for debugging.

Return FAILED when the evidence supports a merge-blocking defect: incorrect
behavior, invalid SSA or LLVM IR, undefined behavior, memory unsafety or memory
leakage, target incompatibility, ABI violation, failed runtime expectations,
exceeded native optimization limits, missing required native structure, or
substantial compiler-generated overhead that remains in optimized LLVM or final
machine code. Also return FAILED with code `insufficient-evidence` when an
essential correctness, safety, ABI, or final-code-quality claim cannot actually be
verified from the supplied artifacts. A speculative idea, style preference,
source-level algorithm alternative, or inefficiency that disappears during LLVM
optimization is non-blocking. Do not invent problems, but do not soften or omit
supported problems merely because the program is small or the optimizer produced
compact code.

An OK verdict requires affirmative artifact evidence for every essential row in
the verification matrix. A concise final program such as `mov constant; ret` is
not sufficient by itself: prove that the constant and return convention match
the source semantics and all preceding compiler stages.

Source paths: {source_path}

=== Reproducibility metadata JSON ===
{metadata_json}
=== End reproducibility metadata ===

=== Weave source ===
{weave_source}
=== End Weave source ===

=== WIR review projection ===
{wir}
=== End WIR review projection ===

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
