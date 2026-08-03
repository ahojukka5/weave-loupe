"""``loupe compiler-audit`` differential compiler gate."""

from __future__ import annotations

import json
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from weave_loupe.audit_result import AuditProtocolError, parse_audit_response
from weave_loupe.complete_compiler_audit import (
    CompilerAuditError,
    ReviewCallback,
    audit_compilers,
)
from weave_loupe.llm import LlmError, chat_completion, load_config
from weave_loupe.native_budget import NativeBudgetError
from weave_loupe.optimized_llvm_budget import OptimizedLlvmBudgetError
from weave_loupe.path_identity import PathIdentityError
from weave_loupe.report_integrity import seal_audit_report
from weave_loupe.runtime_cases import RuntimeCasesError


def run_compiler_audit(
    *,
    weave_files: list[Path],
    baseline_weavec: Path,
    candidate_weavec: Path,
    work_dir: Path,
    policy: Path | None,
    json_out: Path | None,
    report_out: Path | None,
    review_model: str | None,
    review_max_tokens: int,
    allow_unsafe_http: bool | None,
    compiler_timeout_seconds: float | None,
    compiler_output_bytes: int | None,
    runtime_timeout_seconds: float | None,
    runtime_output_bytes: int | None,
    audit_root: Path | None = None,
    source_names: list[str] | None = None,
) -> int:
    """Run the differential audit and publish deterministic evidence."""
    try:
        reviewer = _reviewer(
            model=review_model,
            max_tokens=review_max_tokens,
            allow_unsafe_http=allow_unsafe_http,
        )
        result = audit_compilers(
            sources=weave_files,
            baseline_weavec=baseline_weavec,
            candidate_weavec=candidate_weavec,
            work_dir=work_dir,
            policy_path=policy,
            compiler_timeout_seconds=compiler_timeout_seconds,
            compiler_output_bytes=compiler_output_bytes,
            runtime_timeout_seconds=runtime_timeout_seconds,
            runtime_output_bytes=runtime_output_bytes,
            reviewer=reviewer,
            audit_root=audit_root,
            source_names=source_names,
        )
        payload = (
            json.dumps(
                result,
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
            )
            + "\n"
        )
        if json_out is not None:
            json_out.parent.mkdir(parents=True, exist_ok=True)
            json_out.write_text(payload, encoding="utf-8")
        else:
            sys.stdout.write(payload)
        if report_out is not None:
            report_out.parent.mkdir(parents=True, exist_ok=True)
            report_out.write_text(
                _render_markdown(result),
                encoding="utf-8",
            )
    except (
        AuditProtocolError,
        CompilerAuditError,
        LlmError,
        NativeBudgetError,
        OptimizedLlvmBudgetError,
        PathIdentityError,
        RuntimeCasesError,
        OSError,
    ) as exc:
        print(f"loupe compiler-audit: {exc}", file=sys.stderr)
        return 1

    if json_out is not None:
        print(f"comparison: {json_out.resolve()}")
    if report_out is not None:
        print(f"report: {report_out.resolve()}")
    failures = result.get("failures")
    if isinstance(failures, list) and any(
        isinstance(item, Mapping) and item.get("category") == "infrastructure"
        for item in failures
    ):
        return 1
    return 0 if result.get("passed") is True else 2


def _reviewer(
    *,
    model: str | None,
    max_tokens: int,
    allow_unsafe_http: bool | None,
) -> ReviewCallback | None:
    if model is None:
        return None
    config = load_config(
        model=model,
        max_tokens=max_tokens,
        allow_unsafe_http=allow_unsafe_http,
    )

    def review(evidence: Mapping[str, Any]) -> Mapping[str, Any]:
        prompt = (
            "Review this deterministic baseline-versus-candidate compiler audit.\n"
            "The first line must be exactly OK or "
            "FAILED: <lowercase-kebab-code>: <reason>.\n"
            "Do not override deterministic failures. Explain semantic, quality, "
            "provenance, and evidence changes after the first line.\n\n"
            + json.dumps(
                evidence,
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
            )
        )
        completion = chat_completion(config, prompt)
        verdict = parse_audit_response(completion.content)
        return {
            "status": verdict.status,
            "code": verdict.code,
            "reason": verdict.reason,
            "body": verdict.body,
            "provider": completion.metadata(),
        }

    return review


def _render_markdown(result: Mapping[str, Any]) -> str:
    failures = result.get("failures")
    failure_items = failures if isinstance(failures, list) else []
    baseline = _mapping(result.get("baseline"))
    candidate = _mapping(result.get("candidate"))
    baseline_compiler = _mapping(baseline.get("compiler"))
    candidate_compiler = _mapping(candidate.get("compiler"))
    seal = _mapping(result.get("seal"))
    lines = [
        "# Weave Loupe Compiler Audit",
        "",
        "## Verdict",
        "",
        f"- **Status:** `{result.get('status', 'unknown')}`",
        f"- **Passed:** `{result.get('passed', False)}`",
        f"- **Failure count:** `{len(failure_items)}`",
        "",
        "## Reproducibility",
        "",
        f"- **JSON evidence SHA-256:** `{seal.get('sha256', 'unavailable')}`",
        f"- **Baseline compiler:** `{baseline_compiler.get('version', 'unknown')}`",
        "- **Baseline binary SHA-256:** "
        f"`{baseline_compiler.get('sha256', 'unknown')}`",
        f"- **Candidate compiler:** `{candidate_compiler.get('version', 'unknown')}`",
        "- **Candidate binary SHA-256:** "
        f"`{candidate_compiler.get('sha256', 'unknown')}`",
        "",
        "## Audited inputs",
        "",
    ]
    sources = result.get("sources")
    if isinstance(sources, list):
        for source in sources:
            item = _mapping(source)
            lines.append(
                f"- `{item.get('path', 'unknown')}` — SHA-256 "
                f"`{item.get('sha256', 'unavailable')}`"
            )
    lines.extend(["", "## Failures", ""])
    if failure_items:
        for item in failure_items:
            failure = _mapping(item)
            lines.append(
                "- `{}:{}` — {}".format(
                    failure.get("category", "unknown"),
                    failure.get("code", "unknown"),
                    failure.get("detail", "No detail."),
                )
            )
    else:
        lines.append("- None.")

    lines.extend(["", "## Metric deltas", ""])
    comparison = _mapping(result.get("comparison"))
    deltas = comparison.get("metric_deltas")
    if isinstance(deltas, list):
        lines.append("| Metric | Before | After | Delta | Allowed | Result |")
        lines.append("|---|---:|---:|---:|---|---|")
        for item in deltas:
            delta = _mapping(item)
            allowed = f"[{delta.get('minimum')}, {delta.get('maximum')}]"
            lines.append(
                "| `{}` | {} | {} | {} | `{}` | {} |".format(
                    delta.get("path", "unknown"),
                    delta.get("before", "?"),
                    delta.get("after", "?"),
                    delta.get("delta", "?"),
                    allowed,
                    "PASS" if delta.get("passed") is True else "FAIL",
                )
            )

    review = result.get("review")
    if isinstance(review, Mapping):
        lines.extend(
            [
                "",
                "## Optional model review",
                "",
                f"- **Status:** `{review.get('status', 'unknown')}`",
                f"- **Code:** `{review.get('code') or 'none'}`",
                f"- **Reason:** {review.get('reason') or 'No blocking finding.'}",
                "",
                str(review.get("body") or "No narrative review returned."),
            ]
        )
    lines.append("")
    return seal_audit_report("\n".join(lines))


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}
