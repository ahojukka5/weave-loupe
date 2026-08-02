"""Tests for the positional WIR syntax parser."""

from __future__ import annotations

import pytest

from weave_loupe.wir_syntax import (
    WirAtom,
    WirList,
    WirSyntaxError,
    atom_text,
    head,
    parse_wir,
    walk,
)


def test_parse_wir_retains_comments_offsets_and_strings() -> None:
    text = (
        '; weavec-source-file-v1 0 "demo.weave"\n'
        '(core-module (decls (const_string_ptr "a;b"))) ; trailing\n'
    )

    document = parse_wir(text)

    assert len(document.expressions) == 1
    root = document.expressions[0]
    assert isinstance(root, WirList)
    assert root.start == text.index("(")
    assert root.end == text.rindex(")") + 1
    assert head(root) == "core-module"
    assert [comment.text for comment in document.comments] == [
        'weavec-source-file-v1 0 "demo.weave"',
        "trailing",
    ]
    string_atoms = [
        node.value
        for node in walk(root)
        if isinstance(node, WirAtom) and node.value.startswith('"')
    ]
    assert string_atoms == ['"a;b"']


def test_parse_wir_returns_deterministic_preorder() -> None:
    root = parse_wir("(fn main (params) (returns i32))").expressions[0]

    assert [atom_text(node) for node in walk(root) if isinstance(node, WirAtom)] == [
        "fn",
        "main",
        "params",
        "returns",
        "i32",
    ]


@pytest.mark.parametrize(
    ("text", "message", "offset"),
    [
        (
            ")",
            "unexpected closing parenthesis",
            0,
        ),
        (
            "(core-module",
            "unclosed WIR list",
            0,
        ),
        (
            '(const_string_ptr "unterminated)',
            "unterminated WIR string",
            18,
        ),
    ],
)
def test_parse_wir_reports_explicit_syntax_failures(
    text: str,
    message: str,
    offset: int,
) -> None:
    with pytest.raises(WirSyntaxError) as caught:
        parse_wir(text)

    assert caught.value.message == message
    assert caught.value.offset == offset
