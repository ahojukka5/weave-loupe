"""Human-readable WIR projection for audit prompts and reports."""

from __future__ import annotations

from weave_loupe.wir_syntax import (
    WirAtom,
    WirExpr,
    WirSyntaxError,
    parse_wir,
)


def clean_wir_for_review(wir: str, *, width: int = 96) -> str:
    """Remove provenance comments and pretty-print WIR for review."""
    try:
        document = parse_wir(wir)
        rendered = [
            line
            for expression in document.expressions
            for line in _format(expression, 0, width)
        ]
        return "\n".join(rendered).rstrip() + "\n" if rendered else ""
    except WirSyntaxError:
        fallback = _comment_free_text(wir)
        return fallback.rstrip() + "\n" if fallback.strip() else ""


def _flat(expression: WirExpr) -> str:
    if isinstance(expression, WirAtom):
        return expression.value
    return "(" + " ".join(_flat(value) for value in expression.items) + ")"


def _format(expression: WirExpr, indent: int, width: int) -> list[str]:
    prefix = " " * indent
    flat = _flat(expression)
    if len(prefix) + len(flat) <= width:
        return [prefix + flat]
    if isinstance(expression, WirAtom) or not expression.items:
        return [prefix + flat]

    first, *rest = expression.items
    if isinstance(first, WirAtom):
        lines = [prefix + "(" + first.value]
    else:
        lines = [prefix + "("]
        rest = list(expression.items)
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
