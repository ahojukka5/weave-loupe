"""Markdown rendering for human-verifiable compiler evidence."""

from __future__ import annotations

import re
from collections.abc import Sequence

EvidenceSection = tuple[str, str, str]


def insert_complete_evidence(report: str, sections: Sequence[EvidenceSection]) -> str:
    """Insert complete captured artifacts before the LLM review section."""
    block = render_complete_evidence(sections)
    marker = "\n## LLM review\n"
    if marker not in report:
        return report.rstrip() + "\n\n" + block
    return report.replace(marker, "\n" + block + marker, 1)


def render_complete_evidence(sections: Sequence[EvidenceSection]) -> str:
    """Render source-to-native evidence as readable Markdown code blocks."""
    lines = [
        "## Complete compiler evidence",
        "",
        "This section contains the exact evidence reviewed by the model so that the",
        "source-to-native lowering can also be inspected manually.",
        "",
    ]
    for title, language, content in sections:
        lines.extend([f"### {title}", ""])
        normalized = content.rstrip()
        if not normalized:
            lines.extend(["_Not captured._", ""])
            continue
        fence = _safe_fence(normalized)
        lines.extend([f"{fence}{language}", normalized, fence, ""])
    return "\n".join(lines).rstrip() + "\n"


def _safe_fence(content: str) -> str:
    longest = max((len(match.group(0)) for match in re.finditer(r"`+", content)), default=0)
    return "`" * max(3, longest + 1)
