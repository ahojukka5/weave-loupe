"""Tests for audit prompt and report templates."""

from weave_loupe.templates import (
    AUDIT_REPORT_TEMPLATE,
    render_audit_prompt,
)


def test_render_audit_prompt_includes_all_artifacts() -> None:
    prompt = render_audit_prompt(
        source_path="examples/demo.weave",
        weave_source="(program (entry main))",
        wir="(core-module (core-version 1))",
        llvm_ir="define i32 @main() { ret i32 0 }",
    )

    assert "examples/demo.weave" in prompt
    assert "=== Weave source (.weave) ===" in prompt
    assert "(program (entry main))" in prompt
    assert "=== Intermediate representation (.wir) ===" in prompt
    assert "(core-module (core-version 1))" in prompt
    assert "=== Emitted LLVM IR (.ll) ===" in prompt
    assert "define i32 @main()" in prompt
    assert AUDIT_REPORT_TEMPLATE in prompt


def test_render_audit_prompt_preserves_braces_in_artifacts() -> None:
    prompt = render_audit_prompt(
        source_path="x.weave",
        weave_source="source {brace}",
        wir="wir {brace}",
        llvm_ir="llvm {brace}",
    )

    assert "source {brace}" in prompt
    assert "wir {brace}" in prompt
    assert "llvm {brace}" in prompt
