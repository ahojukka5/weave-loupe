"""Prompt and report templates for `loupe audit`."""

from __future__ import annotations

AUDIT_REPORT_TEMPLATE = """\
# Weave Loupe Audit Report

## Summary
One short paragraph stating overall risk and whether the emitted LLVM IR looks
performance-ready. Mention whether problems appear in surface Weave, WIR, or
LLVM.

## Serious issues
List each serious correctness or safety problem found in the Weave source, the
WIR, or the emitted LLVM IR. Include memory leaks, use-after-free, undefined
behavior, broken control flow, wrong SSA/phi usage, incorrect lowering from
Weave to WIR or WIR to LLVM, and similar defects.

For each issue use:

### Issue: <short title>
- Severity: critical | high | medium
- Location: Weave / WIR / LLVM (function, approximate region)
- Evidence: what in the artifacts shows the problem
- Why it matters: concrete failure mode
- Suggestion: specific fix

If none: write `None found.`

## Performance opportunities
List LLVM IR that could theoretically be optimized away or rewritten for better
performance. Prefer concrete IR-level observations (redundant loads/stores,
stack traffic that mem2reg/SSA should remove, dead instructions, avoidable
branches, missing strength reduction, loop-carried values kept on the stack,
etc.). When useful, also note where the suboptimal shape already appears in WIR
versus only after LLVM emission.

For each opportunity use:

### Opportunity: <short title>
- Impact: high | medium | low
- Location: function / IR region (and WIR form if relevant)
- Evidence: the suboptimal pattern
- Ideal shape: what better IR would look like
- Suggestion: how Weave lowering, WIR, or the source should change

If none: write `None found.`

## Algorithmic notes
Comment on the Weave algorithm itself: asymptotic cost, unnecessary work,
better algorithms, or clearer structure. Separate algorithmic advice from
codegen/IR advice.

If none: write `None found.`

## Suggested next steps
Numbered list of the highest-value follow-ups, most important first.
"""

AUDIT_PROMPT_TEMPLATE = """\
You are an expert Weave and LLVM code reviewer helping compiler developers.

Your job is to inspect the full weavec compilation pipeline artifacts:
1. Surface Weave source (.weave)
2. Intermediate representation emitted by the frontend (.wir)
3. LLVM IR emitted by the backend (.ll)

Focus on:
- Serious issues such as memory leaks, unsafe memory use, undefined behavior,
  broken control flow, and clearly incorrect lowering between stages
- Performance of the emitted LLVM IR: flag any instruction, memory traffic, or
  control-flow pattern that could theoretically be optimized away or rewritten
  into a tighter form. We want IR that is already close to the best practical
  shape for this algorithm
- Whether a problem originates in the Weave source, appears first in WIR, or is
  introduced during LLVM emission
- Algorithmic problems in the Weave source itself

Be concrete and evidence-based. Quote or paraphrase the relevant Weave forms,
WIR forms, or LLVM instructions. Do not invent problems. If something looks
intentional but suboptimal, say so clearly.

Write the final answer by filling the report template below. Keep the section
headings exactly as given. Do not wrap the report in markdown fences.

Source path: {source_path}

=== Weave source (.weave) ===
{weave_source}
=== End Weave source ===

=== Intermediate representation (.wir) ===
{wir}
=== End Intermediate representation ===

=== Emitted LLVM IR (.ll) ===
{llvm_ir}
=== End Emitted LLVM IR ===

=== Report template ===
{report_template}
=== End Report template ===
"""


def render_audit_prompt(
    *,
    source_path: str,
    weave_source: str,
    wir: str,
    llvm_ir: str,
) -> str:
    # Use replace() so braces inside source/IR cannot break formatting.
    return (
        AUDIT_PROMPT_TEMPLATE.replace("{source_path}", source_path)
        .replace("{weave_source}", weave_source)
        .replace("{wir}", wir)
        .replace("{llvm_ir}", llvm_ir)
        .replace("{report_template}", AUDIT_REPORT_TEMPLATE)
    )
