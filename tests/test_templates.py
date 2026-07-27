"""Tests for audit prompts."""

from weave_loupe.templates import AUDIT_REPORT_TEMPLATE, render_audit_prompt


def test_prompt_includes_complete_evidence_and_verdict_contract() -> None:
    prompt = render_audit_prompt(
        source_path="demo.weave",
        weave_source="source {brace}",
        wir="wir {brace}",
        llvm_ir="raw llvm {brace}",
        optimized_llvm="optimized llvm",
        assembly="assembly",
        disassembly="disassembly",
        optimization_record="remarks",
        diagnostics_json='{"diagnostics": []}',
        analysis_json='{"instructions": 2}',
        metadata_json='{"timestamp_utc": "now"}',
    )
    assert "source {brace}" in prompt
    assert "wir {brace}" in prompt
    assert "raw llvm {brace}" in prompt
    assert "optimized llvm" in prompt
    assert "disassembly" in prompt
    assert "FAILED: <lowercase-kebab-code>" in prompt
    assert '"instructions": 2' in prompt
    assert AUDIT_REPORT_TEMPLATE in prompt
