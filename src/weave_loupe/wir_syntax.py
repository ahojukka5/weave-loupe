"""Deterministic positional parser for WIR S-expressions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

# Every WIR core version Loupe can read, lowest first.
#
# A compiler consumes the one contract it targets. An analyser consumes every
# contract that was ever published, because bundles retain WIR text: evidence
# captured under an earlier version stays readable for as long as the bundle
# does. So this set only ever grows, and a version is removed from it only when
# no retained bundle can still contain it.
#
# Version 3 is accepted before any compiler emits it, so that a Loupe release
# capable of reading it exists first. See ahojukka5/weavec#208.
SUPPORTED_CORE_VERSIONS: tuple[int, ...] = (2, 3)


def describe_supported_core_versions() -> str:
    """Render the supported versions for a diagnostic message."""
    versions = [str(version) for version in SUPPORTED_CORE_VERSIONS]
    if len(versions) == 1:
        return versions[0]
    return f"{', '.join(versions[:-1])} or {versions[-1]}"


class WirSyntaxError(ValueError):
    """Raised when WIR cannot be tokenized or parsed."""

    def __init__(self, message: str, *, offset: int) -> None:
        super().__init__(f"{message} at byte offset {offset}")
        self.message = message
        self.offset = offset


@dataclass(frozen=True)
class WirAtom:
    """One exact WIR atom with source offsets."""

    value: str
    start: int
    end: int


@dataclass(frozen=True)
class WirList:
    """One parenthesized WIR list with source offsets."""

    items: tuple[WirExpr, ...]
    start: int
    end: int


type WirExpr = WirAtom | WirList


@dataclass(frozen=True)
class WirComment:
    """One semicolon comment retained for provenance analysis."""

    text: str
    start: int
    end: int
    line: int


@dataclass(frozen=True)
class WirDocument:
    """Parsed top-level expressions and comments."""

    expressions: tuple[WirExpr, ...]
    comments: tuple[WirComment, ...]


@dataclass(frozen=True)
class _Token:
    kind: Literal["atom", "left", "right"]
    value: str
    start: int
    end: int


def parse_wir(text: str) -> WirDocument:
    """Parse WIR while retaining exact atom and comment positions."""
    tokens, comments = _tokenize(text)
    expressions: list[WirExpr] = []
    index = 0
    while index < len(tokens):
        expression, index = _parse_one(tokens, index)
        expressions.append(expression)
    return WirDocument(tuple(expressions), tuple(comments))


def head(expression: WirExpr) -> str | None:
    """Return the first atom of a list when one exists."""
    if not isinstance(expression, WirList) or not expression.items:
        return None
    first = expression.items[0]
    return first.value if isinstance(first, WirAtom) else None


def atom_text(expression: WirExpr) -> str | None:
    """Return exact atom text or ``None`` for a list."""
    return expression.value if isinstance(expression, WirAtom) else None


def walk(expression: WirExpr) -> tuple[WirExpr, ...]:
    """Return a deterministic pre-order traversal."""
    result: list[WirExpr] = []

    def visit(node: WirExpr) -> None:
        result.append(node)
        if isinstance(node, WirList):
            for child in node.items:
                visit(child)

    visit(expression)
    return tuple(result)


def _tokenize(text: str) -> tuple[list[_Token], list[WirComment]]:
    tokens: list[_Token] = []
    comments: list[WirComment] = []
    index = 0
    line = 1
    while index < len(text):
        char = text[index]
        if char.isspace():
            if char == "\n":
                line += 1
            index += 1
            continue
        if char == ";":
            comment, index = _read_comment(text, index, line)
            comments.append(comment)
            continue
        if char == "(":
            tokens.append(_Token("left", char, index, index + 1))
            index += 1
            continue
        if char == ")":
            tokens.append(_Token("right", char, index, index + 1))
            index += 1
            continue
        if char == '"':
            value, end = _read_string(text, index)
            tokens.append(_Token("atom", value, index, end))
            line += value.count("\n")
            index = end
            continue
        start = index
        while index < len(text):
            char = text[index]
            if char.isspace() or char in "();":
                break
            index += 1
        if start == index:
            raise WirSyntaxError("invalid WIR token", offset=index)
        tokens.append(_Token("atom", text[start:index], start, index))
    return tokens, comments


def _read_comment(text: str, index: int, line: int) -> tuple[WirComment, int]:
    start = index
    newline = text.find("\n", index)
    end = len(text) if newline < 0 else newline
    comment = WirComment(text[index + 1 : end].strip(), start, end, line)
    return comment, len(text) if newline < 0 else newline + 1


def _read_string(text: str, index: int) -> tuple[str, int]:
    start = index
    index += 1
    escaped = False
    while index < len(text):
        char = text[index]
        index += 1
        if escaped:
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == '"':
            return text[start:index], index
    raise WirSyntaxError("unterminated WIR string", offset=start)


def _parse_one(tokens: list[_Token], index: int) -> tuple[WirExpr, int]:
    if index >= len(tokens):
        offset = tokens[-1].end if tokens else 0
        raise WirSyntaxError("unexpected end of WIR", offset=offset)
    token = tokens[index]
    if token.kind == "right":
        raise WirSyntaxError("unexpected closing parenthesis", offset=token.start)
    if token.kind == "atom":
        return WirAtom(token.value, token.start, token.end), index + 1

    items: list[WirExpr] = []
    cursor = index + 1
    while cursor < len(tokens) and tokens[cursor].kind != "right":
        child, cursor = _parse_one(tokens, cursor)
        items.append(child)
    if cursor >= len(tokens):
        raise WirSyntaxError("unclosed WIR list", offset=token.start)
    closing = tokens[cursor]
    return WirList(tuple(items), token.start, closing.end), cursor + 1
