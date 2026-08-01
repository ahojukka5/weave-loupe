"""Markdown rendering for token-aware review provenance."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

_MARKER = "\n## LLM review\n"


def insert_review_provenance(report: str, review: Mapping[str, Any]) -> str:
    """Insert complete review-plan evidence before the final model review."""
    section = _render_review_provenance(review)
    if _MARKER not in report:
        return report.rstrip() + "\n\n" + section + "\n"
    return report.replace(_MARKER, "\n" + section + _MARKER, 1)


def _render_review_provenance(review: Mapping[str, Any]) -> str:
    policy = _mapping(review.get("policy"))
    lines = [
        "## Model review coverage and requests",
        "",
        f"- **Review format:** `{_value(review.get('format'))}`",
        f"- **Review mode:** `{_value(review.get('mode'))}`",
        f"- **Token estimator:** `{_value(review.get('token_estimator'))}`",
        "- **Estimated complete review tokens:** "
        f"`{_value(review.get('estimated_total_tokens'))}`",
        f"- **Request count:** `{_value(review.get('request_count'))}`",
        f"- **Maximum total tokens:** `{_value(policy.get('max_total_tokens'))}`",
        f"- **Maximum request tokens:** `{_value(policy.get('max_request_tokens'))}`",
        f"- **Maximum artifact tokens:** `{_value(policy.get('max_artifact_tokens'))}`",
        "- **Artifact-review completion tokens:** "
        f"`{_value(policy.get('chunk_output_tokens'))}`",
        "",
        "### Artifact coverage",
        "",
    ]
    artifacts = review.get("artifacts")
    if isinstance(artifacts, list) and artifacts:
        for raw_artifact in artifacts:
            artifact = _mapping(raw_artifact)
            lines.extend(_artifact_lines(artifact))
    else:
        lines.append("- No artifact coverage metadata was recorded.")

    lines.extend(["", "### Review requests", ""])
    requests = review.get("requests")
    if isinstance(requests, list) and requests:
        for raw_request in requests:
            request = _mapping(raw_request)
            lines.extend(_request_lines(request))
    else:
        lines.append("- No review requests were recorded.")
    return "\n".join(lines)


def _artifact_lines(artifact: Mapping[str, Any]) -> list[str]:
    ranges = artifact.get("coverage")
    coverage = _range_summary(ranges if isinstance(ranges, list) else [])
    return [
        f"#### `{_value(artifact.get('name'))}` — {_value(artifact.get('label'))}",
        "",
        f"- Language: `{_value(artifact.get('language'))}`",
        f"- UTF-8 bytes: `{_value(artifact.get('size'))}`",
        f"- Estimated tokens: `{_value(artifact.get('estimated_tokens'))}`",
        f"- SHA-256: `{_value(artifact.get('sha256'))}`",
        f"- Complete coverage: `{_value(artifact.get('complete'))}`",
        f"- Covered ranges: {coverage}",
        "",
    ]


def _request_lines(request: Mapping[str, Any]) -> list[str]:
    completion = _mapping(request.get("completion"))
    coverage = request.get("coverage")
    depends_on = request.get("depends_on")
    dependencies = (
        ", ".join(f"`{item}`" for item in depends_on)
        if isinstance(depends_on, list) and depends_on
        else "none"
    )
    return [
        f"#### `{_value(request.get('request_id'))}` — {_value(request.get('kind'))}",
        "",
        f"- Estimated input tokens: `{_value(request.get('estimated_input_tokens'))}`",
        f"- Reserved output tokens: `{_value(request.get('reserved_output_tokens'))}`",
        f"- Depends on: {dependencies}",
        "- Covered ranges: "
        + _range_summary(coverage if isinstance(coverage, list) else []),
        f"- Prompt SHA-256: `{_value(completion.get('prompt_sha256'))}`",
        f"- Request SHA-256: `{_value(completion.get('request_sha256'))}`",
        f"- Requested model: `{_value(completion.get('requested_model'))}`",
        f"- Provider model: `{_value(completion.get('provider_model'))}`",
        f"- Provider response ID: `{_value(completion.get('response_id'))}`",
        f"- Finish reason: `{_value(completion.get('finish_reason'))}`",
        f"- Provider prompt tokens: `{_value(completion.get('prompt_tokens'))}`",
        "- Provider completion tokens: "
        f"`{_value(completion.get('completion_tokens'))}`",
        f"- Provider total tokens: `{_value(completion.get('total_tokens'))}`",
        "",
    ]


def _range_summary(ranges: Sequence[object]) -> str:
    if not ranges:
        return "none"
    values: list[str] = []
    for raw_range in ranges:
        item = _mapping(raw_range)
        values.append(
            "`{}:[{}, {})@{}`".format(
                _value(item.get("artifact")),
                _value(item.get("start")),
                _value(item.get("end")),
                _value(item.get("sha256")),
            )
        )
    return ", ".join(values)


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _value(value: object) -> str:
    return "unavailable" if value is None else str(value)
