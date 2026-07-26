"""Tests for audit prompts."""

from weave_loupe.templates import AUDIT_REPORT_TEMPLATE, render_audit_prompt


def test_prompt_includes_complete_evidence() -> None:
    prompt = render_audit_prompt(
        source_path="demo.weave",
        weave_source="source {brace}",
        wir="wir {brace}",
        llvm_ir="llvm {brace}",
        diagnostics_json='{"diagnostics": []}',
        trace_summary_json='{"events": 1}',
        llvm_metrics_json='{"instructions": 2}',
    )
    assert "source {brace}" in prompt
    assert "wir {brace}" in prompt
    assert "llvm {brace}" in prompt
    assert '"events": 1' in prompt
    assert '"instructions": 2' in prompt
    assert AUDIT_REPORT_TEMPLATE in prompt
