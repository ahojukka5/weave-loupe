"""Tests for human-verifiable verbose audit reports."""

from __future__ import annotations

from weave_loupe.evidence_report import insert_complete_evidence, render_complete_evidence


def test_render_complete_evidence_preserves_stage_order() -> None:
    rendered = render_complete_evidence(
        [
            ("Weave source", "lisp", "(program)"),
            ("Raw LLVM IR", "llvm", "define i32 @main() { ret i32 0 }"),
            ("Native disassembly", "asm", "main:\n  ret"),
        ]
    )

    assert rendered.index("### Weave source") < rendered.index("### Raw LLVM IR")
    assert rendered.index("### Raw LLVM IR") < rendered.index("### Native disassembly")
    assert "```llvm" in rendered
    assert "define i32 @main()" in rendered


def test_render_complete_evidence_uses_safe_fence() -> None:
    rendered = render_complete_evidence(
        [("Source", "text", "before\n```\nafter")]
    )

    assert "````text" in rendered
    assert rendered.count("````") == 2


def test_insert_complete_evidence_precedes_llm_review() -> None:
    report = "# Audit\n\n## LLM review\n\nOK\n"
    rendered = insert_complete_evidence(report, [("WIR", "lisp", "(wir)")])

    assert rendered.index("## Complete compiler evidence") < rendered.index("## LLM review")
