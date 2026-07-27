"""Human-readable WIR projection for audit prompts and reports."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class _Token:
    value: str


type WirExpr = str | list[WirExpr]


def clean_wir_for_review(wir: str, *, width: int = 96) -> str:
    """Remove provenance comments and pretty-print WIR for review."""
    try:
        tokens = _tokenize(wir)
        expressions = _parse(tokens)
        rendered = [line for expr in expressions for line in _format(expr, 0, width)]
        return "\n".join(rendered).rstrip() + "\n" if rendered else ""
    except ValueError:
        fallback = _comment_free_text(wir)
        return fallback.rstrip() + "\n" if fallback.strip() else ""


def _tokenize(text: str) -> list[_Token]:
    tokens: list[_Token] = []
    index = 0
    length = len(text)
    while index < length:
        char = text[index]
        if char.isspace():
            index += 1
            continue
        if char == ";":
            index = _skip_comment(text, index)
            continue
        if char in "()":
            tokens.append(_Token(char))
            index += 1
            continue
        if char == '"':
            value, index = _read_string(text, index)
            tokens.append(_Token(value))
            continue
        start = index
        while index < length:
            char = text[index]
            if char.isspace() or char in "();":
                break
            index += 1
        if start == index:
            raise ValueError("invalid WIR token")
        tokens.append(_Token(text[start:index]))
    return tokens


def _skip_comment(text: str, index: int) -> int:
    newline = text.find("\n", index)
    return len(text) if newline < 0 else newline + 1


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
    raise ValueError("unterminated WIR string")


def _parse(tokens: list[_Token]) -> list[WirExpr]:
    expressions: list[WirExpr] = []
    index = 0
    while index < len(tokens):
        expression, index = _parse_one(tokens, index)
        expressions.append(expression)
    return expressions


def _parse_one(tokens: list[_Token], index: int) -> tuple[WirExpr, int]:
    if index >= len(tokens):
        raise ValueError("unexpected end of WIR")
    token = tokens[index].value
    if token == ")":
        raise ValueError("unexpected closing parenthesis")
    if token != "(":
        return token, index + 1

    values: list[WirExpr] = []
    index += 1
    while index < len(tokens) and tokens[index].value != ")":
        value, index = _parse_one(tokens, index)
        values.append(value)
    if index >= len(tokens):
        raise ValueError("unclosed WIR list")
    return values, index + 1


def _flat(expression: WirExpr) -> str:
    if isinstance(expression, str):
        return expression
    return "(" + " ".join(_flat(value) for value in expression) + ")"


def _format(expression: WirExpr, indent: int, width: int) -> list[str]:
    prefix = " " * indent
    flat = _flat(expression)
    if len(prefix) + len(flat) <= width:
        return [prefix + flat]
    if isinstance(expression, str) or not expression:
        return [prefix + flat]

    first, *rest = expression
    if isinstance(first, str):
        lines = [prefix + "(" + first]
    else:
        lines = [prefix + "("]
        rest = expression
    for child in rest:
        lines.extend(_format(child, indent + 2, width))
    lines[-1] += ")"
    return lines


def _comment_free_text(text: str) -> str:
    lines: list[str] = []
    for line in text.splitlines():
        in_string = False
        escaped = False
        output: list[str] = []
        for char in line:
            if escaped:
                output.append(char)
                escaped = False
                continue
            if char == "\\" and in_string:
                output.append(char)
                escaped = True
                continue
            if char == '"':
                in_string = not in_string
                output.append(char)
                continue
            if char == ";" and not in_string:
                break
            output.append(char)
        cleaned = "".join(output).rstrip()
        if cleaned:
            lines.append(cleaned)
    return "\n".join(lines)
