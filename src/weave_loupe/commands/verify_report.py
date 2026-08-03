"""``loupe verify-report`` — deterministic report freshness verification."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from weave_loupe.auditor_identity import identify_auditor, sha256_file
from weave_loupe.compiler_version import CompilerVersion, identify_weavec
from weave_loupe.expected_failure_audit import expected_failure_report_reasons
from weave_loupe.llm import (
    LlmError,
    normalize_endpoint_identity,
    resolve_unsafe_http_policy,
)
from weave_loupe.report_validity import ValidityResult, evaluate_report
from weave_loupe.weavec import WeavecError, resolve_weavec


def run_verify_report(
    *,
    report: Path,
    source: Path | None,
    weavec: Path | None,
    model: str | None,
    endpoint: str | None,
    max_tokens: int | None,
    max_age_days: int,
    json_out: Path | None,
    sources: list[Path] | None = None,
    allow_unsafe_http: bool | None = None,
) -> int:
    """Verify a report without compiling sources or calling an LLM."""
    try:
        if max_age_days <= 0:
            raise ValueError("max_age_days must be positive")
        if max_tokens is not None and max_tokens <= 0:
            raise ValueError("max_tokens must be positive")
        if not report.is_file():
            raise ValueError(f"audit report not found: {report}")
        if source is not None and sources is not None:
            raise ValueError("source and sources cannot both be provided")
        unsafe_http = resolve_unsafe_http_policy(allow_unsafe_http)
        current_endpoint = (
            normalize_endpoint_identity(
                endpoint,
                allow_unsafe_http=unsafe_http,
            )
            if endpoint is not None
            else None
        )
        binary = resolve_weavec(weavec)
        compiler = identify_weavec(binary)
        compiler_binary_sha256 = sha256_file(binary)
        auditor = identify_auditor()
        now = datetime.now(UTC)
        result = evaluate_report(
            report=report,
            source=source,
            sources=sources,
            compiler_identity=compiler,
            compiler_binary_sha256=compiler_binary_sha256,
            auditor=auditor,
            current_model=model,
            current_endpoint=current_endpoint,
            current_max_tokens=max_tokens,
            now=now,
            max_age=timedelta(days=max_age_days),
        )
        result = _include_expected_failure_contract(result)
        document = _result_document(
            result=result,
            checked_at=now,
            compiler=compiler,
            compiler_binary_sha256=compiler_binary_sha256,
            auditor=auditor.metadata(),
            model=model,
            endpoint=current_endpoint,
            max_tokens=max_tokens,
            max_age_days=max_age_days,
        )
        if json_out is not None:
            json_out.parent.mkdir(parents=True, exist_ok=True)
            json_out.write_text(
                json.dumps(document, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        _print_result(result)
        return 0 if result.valid else 2
    except (OSError, ValueError, WeavecError, LlmError) as exc:
        print(f"loupe verify-report: {exc}", file=sys.stderr)
        return 1


def _include_expected_failure_contract(result: ValidityResult) -> ValidityResult:
    reasons = expected_failure_report_reasons(result.report)
    if not reasons:
        return result
    return ValidityResult(
        report=result.report,
        source=result.source,
        identity=result.identity,
        reasons=(*result.reasons, *reasons),
        sources=result.sources,
        source_mismatches=result.source_mismatches,
    )


def _result_document(
    *,
    result: ValidityResult,
    checked_at: datetime,
    compiler: CompilerVersion,
    compiler_binary_sha256: str,
    auditor: dict[str, Any],
    model: str | None,
    endpoint: str | None,
    max_tokens: int | None,
    max_age_days: int,
) -> dict[str, Any]:
    identity = asdict(result.identity)
    timestamp = identity.get("timestamp")
    if isinstance(timestamp, datetime):
        identity["timestamp"] = timestamp.isoformat()
    return {
        "format": "weave-loupe-report-verification-v1",
        "valid": result.valid,
        "checked_at_utc": checked_at.replace(microsecond=0).isoformat(),
        "max_age_days": max_age_days,
        "report": str(result.report),
        "source": str(result.source),
        "sources": [str(path) for path in result.sources],
        "source_mismatches": [
            asdict(mismatch) for mismatch in result.source_mismatches
        ],
        "reasons": list(result.reasons),
        "report_identity": identity,
        "current_compiler": {
            **asdict(compiler),
            "binary_sha256": compiler_binary_sha256,
        },
        "current_auditor": auditor,
        "current_model": model,
        "current_endpoint": endpoint,
        "current_max_tokens": max_tokens,
    }


def _print_result(result: ValidityResult) -> None:
    if result.valid:
        print(f"VALID: {result.report}")
        return
    print(f"STALE: {result.report}")
    for reason in result.reasons:
        print(f"- {reason}")
