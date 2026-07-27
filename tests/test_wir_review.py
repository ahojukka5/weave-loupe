"""Tests for the human-readable WIR review projection."""

from weave_loupe.wir_review import clean_wir_for_review


def test_clean_wir_removes_inline_provenance_and_reformats() -> None:
    raw = """; weavec-source-file-v1 0 \"demo.weave\"
(core-module
  (core-version 2)
  (decls
    ; weavec-source-span-v1 0 1 9
    (; weavec-source-span-v1 0 2 3
    extern ; weavec-source-span-v1 0 4 5
    getenv
      (params (name ptr))
      (returns ptr))))
"""
    cleaned = clean_wir_for_review(raw)
    assert "weavec-source" not in cleaned
    assert "(core-version 2)" in cleaned
    assert "(extern getenv (params (name ptr)) (returns ptr))" in cleaned
    assert cleaned.count("(") == cleaned.count(")")


def test_clean_wir_preserves_semicolon_inside_string() -> None:
    raw = '(core-module (decls (const_string_ptr "a;b"))) ; hidden\n'
    cleaned = clean_wir_for_review(raw)
    assert '"a;b"' in cleaned
    assert "hidden" not in cleaned
