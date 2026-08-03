"""Deterministic audits for intentionally rejected Weave programs."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from weave_loupe.analysis import analyze_bundle
from weave_loupe.audit_result import (
    AuditVerdict,
    collect_audit_metadata,
    render_audit_report,
)
from weave_loupe.bundle import Bundle, BundleError, capture_bundle, load_bundle
from weave_loupe.evidence_report import insert_complete_evidence
from weave_loupe.llm import normalize_endpoint_identity
from weave_loupe.path_identity import (
    PathIdentityError,
    canonical_sidecar_identity,
    canonicalize_audit_metadata,
    plan_public_paths,
    redact_private_paths,
)
from weave_loupe.report_integrity import seal_audit_report

EXPECTED_FAILURE_FORMAT = "weave-loupe-expected-failure-v1"
EXPECTED_FAILURE_RESULT_FORMAT = "weave-loupe-expected-failure-result-v1"
EXPECTED_FAILURE_SUFFIX = ".audit.failure.toml"
_DEFAULT_FORBIDDEN_ARTIFACTS = (
    "executable",
    "assembly",
    "disassembly",
)
_CONTRACT_INPUT = re.compile(
    r"^- Runtime matrix `(?P<path>[^`]+)` — SHA-256 "
    r"`(?P<sha256>[0-9a-f]{64})`$"
)


class ExpectedFailureError(ValueError):
    """Raised when an expected-failure contract is invalid or mismatched."""


@dataclass(frozen=True)
class ExpectedDiagnostic:
    """One exact diagnostic expectation."""

    code: str
    severity: str
    phase: str
    source_index: int
    start_line: int
    start_column: int
    end_line: int
    end_column: int
    span_text: str
    operand_role: str | None
    symbol: str | None
    span_origin: str | None
    analysis_complete: bool | None


@dataclass(frozen=True)
class ExpectedFailureContract:
    """Validated deterministic compiler-failure contract."""

    path: Path
    sources: tuple[Path, ...]
    exit_code: int
    phase: str
    diagnostics: tuple[ExpectedDiagnostic, ...]
    forbidden_artifacts: tuple[str, ...]

    @property
    def report(self) -> Path:
        return report_path_for_contract(self.path)


def report_path_for_contract(path: Path) -> Path:
    """Return the workflow-owned report path adjacent to a contract."""
    name = str(path)
    if not name.endswith(EXPECTED_FAILURE_SUFFIX):
        raise ExpectedFailureError(f"not an expected-failure contract: {path}")
    return Path(name[: -len(EXPECTED_FAILURE_SUFFIX)] + ".md")


def contract_path_for_report(report: Path) -> Path:
    """Return the adjacent expected-failure contract for a report."""
    return report.with_name(report.stem + EXPECTED_FAILURE_SUFFIX)


def expected_failure_report_reasons(report: Path) -> tuple[str, ...]:
    """Verify an adjacent negative contract identity recorded in a report."""
    contract = contract_path_for_report(report)
    if not contract.is_file():
        return ()
    try:
        lines = report.read_text(encoding="utf-8").splitlines()
        digest = _sha256(contract.read_bytes())
    except OSError as exc:
        return (f"expected-failure contract could not be read: {exc}",)

    recorded_path: str | None = None
    recorded_digest: str | None = None
    for line in lines:
        match = _CONTRACT_INPUT.fullmatch(line)
        if match is not None and match.group("path").endswith(EXPECTED_FAILURE_SUFFIX):
            recorded_path = match.group("path")
            recorded_digest = match.group("sha256")
            break

    reasons: list[str] = []
    if recorded_path is None or recorded_digest is None:
        reasons.append("report does not record expected-failure contract identity")
        return tuple(reasons)
    normalized = recorded_path.replace("\\", "/")
    if not normalized.endswith(contract.name):
        reasons.append("expected-failure contract path changed since audit")
    if recorded_digest != digest:
        reasons.append("expected-failure contract content changed since audit")
    return tuple(reasons)


def load_expected_failure_contract(path: Path) -> ExpectedFailureContract:
    """Parse one strict TOML expected-failure contract."""
    try:
        document = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        message = f"invalid expected-failure contract {path}: {exc}"
        raise ExpectedFailureError(message) from exc
    if not isinstance(document, dict):
        raise ExpectedFailureError("expected-failure contract must be a TOML table")

    _reject_unknown_keys(
        document,
        {
            "format",
            "sources",
            "exit_code",
            "phase",
            "forbidden_artifacts",
            "diagnostics",
        },
        "contract",
    )
    if document.get("format") != EXPECTED_FAILURE_FORMAT:
        raise ExpectedFailureError(
            f"expected-failure format must be {EXPECTED_FAILURE_FORMAT!r}"
        )

    raw_sources = document.get("sources")
    if not isinstance(raw_sources, list) or not raw_sources:
        raise ExpectedFailureError("expected-failure sources must be a non-empty array")
    if not all(isinstance(item, str) and item.strip() for item in raw_sources):
        raise ExpectedFailureError(
            "expected-failure sources must contain non-empty strings"
        )
    entries = tuple(item.strip() for item in raw_sources)
    sources = _resolve_sources(path, entries)

    exit_code = document.get("exit_code")
    if not isinstance(exit_code, int) or isinstance(exit_code, bool) or exit_code == 0:
        raise ExpectedFailureError(
            "expected-failure exit_code must be a nonzero integer"
        )
    phase = _required_text(document, "phase", "contract")

    raw_diagnostics = document.get("diagnostics")
    if not isinstance(raw_diagnostics, list) or not raw_diagnostics:
        raise ExpectedFailureError(
            "expected-failure diagnostics must be a non-empty array of tables"
        )
    diagnostics = tuple(
        _parse_diagnostic(item, index, default_phase=phase)
        for index, item in enumerate(raw_diagnostics)
    )

    raw_forbidden = document.get(
        "forbidden_artifacts",
        list(_DEFAULT_FORBIDDEN_ARTIFACTS),
    )
    if not isinstance(raw_forbidden, list) or not raw_forbidden:
        raise ExpectedFailureError(
            "forbidden_artifacts must be a non-empty array of artifact names"
        )
    if not all(isinstance(item, str) and item.strip() for item in raw_forbidden):
        raise ExpectedFailureError("forbidden_artifacts must contain non-empty strings")
    forbidden = tuple(item.strip() for item in raw_forbidden)
    if len(forbidden) != len(set(forbidden)):
        raise ExpectedFailureError("forbidden_artifacts must be unique")

    return ExpectedFailureContract(
        path=path,
        sources=sources,
        exit_code=exit_code,
        phase=phase,
        diagnostics=diagnostics,
        forbidden_artifacts=forbidden,
    )


def evaluate_expected_failure(
    *,
    bundle: Bundle,
    contract: ExpectedFailureContract,
) -> dict[str, Any]:
    """Compare captured compiler evidence with one exact failure contract."""
    failures: list[str] = []
    compiler = bundle.manifest.get("compiler")
    observed_exit = compiler.get("exit_code") if isinstance(compiler, dict) else None
    if observed_exit != contract.exit_code:
        failures.append(
            f"compiler exit code was {observed_exit!r}, expected {contract.exit_code}"
        )

    diagnostics_document = bundle.artifact_json("diagnostics")
    observed_phase: object = None
    observed_items: list[Any] = []
    if not isinstance(diagnostics_document, dict):
        failures.append("structured diagnostics artifact is missing or invalid")
    else:
        if diagnostics_document.get("format") != "weavec-diagnostics-v1":
            failures.append("diagnostics format is not 'weavec-diagnostics-v1'")
        if diagnostics_document.get("status") != "failed":
            failures.append("diagnostics status is not 'failed'")
        observed_phase = diagnostics_document.get("phase")
        if observed_phase != contract.phase:
            failures.append(
                f"diagnostics phase was {observed_phase!r}, expected {contract.phase!r}"
            )
        if diagnostics_document.get("exit_code") != contract.exit_code:
            failures.append("diagnostics exit_code does not match the contract")
        raw_items = diagnostics_document.get("diagnostics")
        if isinstance(raw_items, list):
            observed_items = raw_items
        else:
            failures.append("diagnostics list is missing or invalid")

    if len(observed_items) != len(contract.diagnostics):
        failures.append(
            "diagnostic count was "
            f"{len(observed_items)}, expected {len(contract.diagnostics)}"
        )

    diagnostic_results: list[dict[str, Any]] = []
    for index, expected in enumerate(contract.diagnostics):
        actual = observed_items[index] if index < len(observed_items) else None
        item_failures = _compare_diagnostic(
            actual=actual,
            expected=expected,
            sources=contract.sources,
            index=index,
        )
        failures.extend(item_failures)
        diagnostic_results.append(
            {
                "index": index,
                "code": expected.code,
                "source_index": expected.source_index,
                "span": {
                    "start_line": expected.start_line,
                    "start_column": expected.start_column,
                    "end_line": expected.end_line,
                    "end_column": expected.end_column,
                },
                "span_text": expected.span_text,
                "passed": not item_failures,
                "failures": item_failures,
            }
        )

    published_forbidden = [
        name
        for name in contract.forbidden_artifacts
        if bundle.artifact_path(name) is not None
    ]
    if published_forbidden:
        failures.append(
            "compiler published forbidden native artifacts: "
            + ", ".join(published_forbidden)
        )

    return {
        "format": EXPECTED_FAILURE_RESULT_FORMAT,
        "configured": True,
        "passed": not failures,
        "expected_exit_code": contract.exit_code,
        "observed_exit_code": observed_exit,
        "expected_phase": contract.phase,
        "observed_phase": observed_phase,
        "diagnostic_count": len(observed_items),
        "diagnostics": diagnostic_results,
        "forbidden_artifacts": list(contract.forbidden_artifacts),
        "published_forbidden_artifacts": published_forbidden,
        "failures": failures,
    }


def run_expected_failure_audit(
    *,
    contract_path: Path,
    weavec: Path | None,
    model: str,
    max_tokens: int,
    report_out: Path | None,
    llm_endpoint: str | None = None,
) -> int:
    """Capture, verify, render, and seal one deterministic failure report."""
    report = ""
    try:
        if max_tokens <= 0:
            raise ExpectedFailureError("max_tokens must be positive")
        contract = load_expected_failure_contract(contract_path)
        plan = plan_public_paths(contract.sources)
        configured_endpoint = llm_endpoint or os.environ.get("WEAVE_LLM_ENDPOINT")
        endpoint = (
            normalize_endpoint_identity(configured_endpoint)
            if configured_endpoint
            else "deterministic-expected-failure"
        )

        with tempfile.TemporaryDirectory(prefix="loupe-expected-failure-") as temp_dir:
            bundle_path = Path(temp_dir) / "failure.loupe"
            capture = capture_bundle(
                sources=contract.sources,
                output=bundle_path,
                weavec=weavec,
                include_executable=True,
            )
            bundle = load_bundle(capture.bundle)
            result = evaluate_expected_failure(
                bundle=bundle,
                contract=contract,
            )
            analysis = analyze_bundle(bundle)
            analysis["expected_failure"] = result

            runtime_input = {
                "format": EXPECTED_FAILURE_FORMAT,
                "configured": True,
                "sidecar": canonical_sidecar_identity(contract.path, plan),
                "sidecar_sha256": _sha256(contract.path.read_bytes()),
                "case_count": len(contract.diagnostics),
            }
            native = analysis.get("native")
            metadata = collect_audit_metadata(
                sources=list(contract.sources),
                weavec=weavec,
                model=model,
                llm_endpoint=endpoint,
                bundle=bundle,
                runtime_matrix=runtime_input,
                native_analysis=native if isinstance(native, dict) else None,
            )
            metadata = canonicalize_audit_metadata(
                metadata,
                plan=plan,
                runtime_sidecar=contract.path,
            )
            llm = metadata.get("llm")
            if isinstance(llm, dict):
                llm.update(
                    {
                        "max_tokens": max_tokens,
                        "temperature": 0,
                        "review_mode": "deterministic-expected-failure",
                    }
                )
            metadata["review"] = {
                "format": "weave-loupe-deterministic-review-v1",
                "mode": "deterministic-expected-failure",
                "model_request_performed": False,
            }

            verdict = _verdict(result)
            narrative = _render_narrative(contract=contract, result=result)
            raw_response = (
                "DETERMINISTIC EXPECTED-FAILURE REVIEW\n"
                "No model request was made; the versioned compiler-failure "
                "contract was evaluated directly."
            )
            report = render_audit_report(
                verdict=AuditVerdict(
                    status=verdict.status,
                    code=verdict.code,
                    reason=verdict.reason,
                    body=narrative,
                ),
                metadata=metadata,
                model_response=raw_response,
            )

            sources_text = "\n\n".join(
                f"--- {plan.sources[index].identity} ---\n"
                + source.read_text(encoding="utf-8")
                for index, source in enumerate(contract.sources)
            )
            result_json = json.dumps(
                result,
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
            )
            diagnostics_json = json.dumps(
                bundle.artifact_json("diagnostics"),
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
            )
            analysis_json = json.dumps(
                analysis,
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
            )
            report = insert_complete_evidence(
                report,
                [
                    ("Weave source", "lisp", sources_text),
                    (
                        "Expected compiler failure contract",
                        "toml",
                        contract.path.read_text(encoding="utf-8"),
                    ),
                    ("Expected failure result", "json", result_json),
                    ("Diagnostics", "json", diagnostics_json),
                    ("Deterministic analysis", "json", analysis_json),
                    (
                        "Compiler build manifest",
                        "json",
                        bundle.artifact_text("build_manifest") or "",
                    ),
                    (
                        "Compiler trace",
                        "json",
                        bundle.artifact_text("trace") or "",
                    ),
                    ("Compiler stdout", "text", bundle.log_text("stdout") or ""),
                    ("Compiler stderr", "text", bundle.log_text("stderr") or ""),
                ],
            )
            report = seal_audit_report(redact_private_paths(report, plan=plan))

        sys.stdout.write(report)
        if not report.endswith("\n"):
            sys.stdout.write("\n")
        if not verdict.passed:
            if report_out is not None and report_out.exists():
                report_out.unlink()
            print(
                f"loupe expected-failure audit: FAILED [{verdict.code}]: "
                f"{verdict.reason}",
                file=sys.stderr,
            )
            return 2
        if report_out is not None:
            report_out.parent.mkdir(parents=True, exist_ok=True)
            report_out.write_text(report, encoding="utf-8")
        return 0
    except (
        OSError,
        BundleError,
        ExpectedFailureError,
        PathIdentityError,
        ValueError,
    ) as exc:
        if report_out is not None and report_out.exists():
            report_out.unlink()
        print(f"loupe expected-failure audit: {exc}", file=sys.stderr)
        return 1


def _parse_diagnostic(
    value: object,
    index: int,
    *,
    default_phase: str,
) -> ExpectedDiagnostic:
    if not isinstance(value, dict):
        raise ExpectedFailureError(f"diagnostic {index} must be a TOML table")
    _reject_unknown_keys(
        value,
        {
            "code",
            "severity",
            "phase",
            "source_index",
            "start_line",
            "start_column",
            "end_line",
            "end_column",
            "span_text",
            "operand_role",
            "symbol",
            "span_origin",
            "analysis_complete",
        },
        f"diagnostic {index}",
    )
    source_index = _required_nonnegative_int(value, "source_index", index)
    positions = {
        name: _required_positive_int(value, name, index)
        for name in ("start_line", "start_column", "end_line", "end_column")
    }
    if (positions["end_line"], positions["end_column"]) < (
        positions["start_line"],
        positions["start_column"],
    ):
        raise ExpectedFailureError(f"diagnostic {index} span ends before it starts")
    analysis_complete = value.get("analysis_complete")
    if analysis_complete is not None and not isinstance(
        analysis_complete,
        bool,
    ):
        raise ExpectedFailureError(
            f"diagnostic {index} analysis_complete must be a boolean"
        )
    return ExpectedDiagnostic(
        code=_required_text(value, "code", f"diagnostic {index}"),
        severity=_optional_text(value, "severity") or "error",
        phase=_optional_text(value, "phase") or default_phase,
        source_index=source_index,
        start_line=positions["start_line"],
        start_column=positions["start_column"],
        end_line=positions["end_line"],
        end_column=positions["end_column"],
        span_text=_required_text(value, "span_text", f"diagnostic {index}"),
        operand_role=_optional_text(value, "operand_role"),
        symbol=_optional_text(value, "symbol"),
        span_origin=_optional_text(value, "span_origin"),
        analysis_complete=analysis_complete,
    )


def _compare_diagnostic(
    *,
    actual: object,
    expected: ExpectedDiagnostic,
    sources: tuple[Path, ...],
    index: int,
) -> list[str]:
    prefix = f"diagnostic {index}"
    if not isinstance(actual, dict):
        return [f"{prefix} is missing or invalid"]
    failures: list[str] = []
    for field, text_expected in (
        ("code", expected.code),
        ("severity", expected.severity),
        ("phase", expected.phase),
    ):
        if actual.get(field) != text_expected:
            failures.append(
                f"{prefix} {field} was {actual.get(field)!r}, "
                f"expected {text_expected!r}"
            )
    for field, optional_expected in (
        ("operand_role", expected.operand_role),
        ("symbol", expected.symbol),
        ("span_origin", expected.span_origin),
        ("analysis_complete", expected.analysis_complete),
    ):
        if optional_expected is not None and actual.get(field) != optional_expected:
            failures.append(
                f"{prefix} {field} was {actual.get(field)!r}, "
                f"expected {optional_expected!r}"
            )

    if expected.source_index >= len(sources):
        failures.append(
            f"{prefix} source_index {expected.source_index} exceeds source count"
        )
        return failures
    source = sources[expected.source_index]
    actual_source = actual.get("source")
    if not isinstance(actual_source, str):
        failures.append(f"{prefix} source is missing")
    else:
        try:
            if Path(actual_source).resolve() != source.resolve():
                failures.append(
                    f"{prefix} source does not match source[{expected.source_index}]"
                )
        except OSError:
            failures.append(f"{prefix} source path cannot be resolved")

    span = actual.get("span")
    if not isinstance(span, dict):
        failures.append(f"{prefix} span is missing or invalid")
        return failures
    for field, position_expected in (
        ("start_line", expected.start_line),
        ("start_column", expected.start_column),
        ("end_line", expected.end_line),
        ("end_column", expected.end_column),
    ):
        if span.get(field) != position_expected:
            failures.append(
                f"{prefix} span.{field} was {span.get(field)!r}, "
                f"expected {position_expected}"
            )
    start_byte = span.get("start_byte")
    end_byte = span.get("end_byte")
    if not isinstance(start_byte, int) or not isinstance(end_byte, int):
        failures.append(f"{prefix} byte span is missing or invalid")
    else:
        observed = source.read_bytes()[start_byte:end_byte]
        expected_bytes = expected.span_text.encode("utf-8")
        if observed != expected_bytes:
            failures.append(
                f"{prefix} span text was {observed!r}, expected {expected_bytes!r}"
            )
    return failures


def _resolve_sources(
    contract: Path,
    entries: tuple[str, ...],
) -> tuple[Path, ...]:
    root = contract.parent.resolve()
    sources: list[Path] = []
    seen: set[Path] = set()
    for entry in entries:
        raw = Path(entry)
        if raw.is_absolute():
            raise ExpectedFailureError(f"source path must be relative: {entry}")
        candidate = contract.parent / raw
        resolved = candidate.resolve()
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            message = f"source path escapes contract directory: {entry}"
            raise ExpectedFailureError(message) from exc
        if resolved in seen:
            raise ExpectedFailureError(f"source path is duplicated: {entry}")
        if not candidate.is_file():
            message = f"expected-failure source does not exist: {candidate}"
            raise ExpectedFailureError(message)
        seen.add(resolved)
        sources.append(candidate)
    return tuple(sources)


def _verdict(result: dict[str, Any]) -> AuditVerdict:
    failures = result.get("failures")
    items = failures if isinstance(failures, list) else []
    if result.get("passed") is True:
        return AuditVerdict(
            status="OK",
            code=None,
            reason=None,
            body="",
        )
    first = next(
        (item for item in items if isinstance(item, str)),
        "contract mismatch",
    )
    return AuditVerdict(
        status="FAILED",
        code="expected-compiler-failure-mismatch",
        reason=first,
        body="",
    )


def _render_narrative(
    *,
    contract: ExpectedFailureContract,
    result: dict[str, Any],
) -> str:
    status = "PASS" if result.get("passed") is True else "FAIL"
    published = result.get("published_forbidden_artifacts", [])
    published_text = (
        "`, `".join(item for item in published if isinstance(item, str)) or "none"
    )
    lines = [
        "## Deterministic expected-failure verification",
        "",
        "No model request was made. This report verifies an intentionally "
        "invalid program against a versioned, exact compiler-failure contract.",
        "",
        f"- **Overall contract:** {status}",
        f"- **Compiler exit code:** expected `{contract.exit_code}`, observed "
        f"`{result.get('observed_exit_code')}`",
        f"- **Compiler phase:** expected `{contract.phase}`, observed "
        f"`{result.get('observed_phase')}`",
        f"- **Expected diagnostics:** `{len(contract.diagnostics)}`",
        f"- **Observed diagnostics:** `{result.get('diagnostic_count')}`",
        "- **Forbidden native artifacts:** `"
        + "`, `".join(contract.forbidden_artifacts)
        + "`",
        f"- **Published forbidden artifacts:** `{published_text}`",
        "",
        "## Diagnostic matrix",
        "",
    ]
    for item in result.get("diagnostics", []):
        if not isinstance(item, dict):
            continue
        state = "PASS" if item.get("passed") is True else "FAIL"
        raw_span = item.get("span")
        span = raw_span if isinstance(raw_span, dict) else {}
        lines.append(
            f"- {state} `{item.get('code')}` at "
            f"source[{item.get('source_index')}] "
            f"{span.get('start_line')}:{span.get('start_column')}-"
            f"{span.get('end_line')}:{span.get('end_column')} covering "
            f"`{item.get('span_text')}`"
        )
    failures = result.get("failures")
    if isinstance(failures, list) and failures:
        lines.extend(["", "## Blocking findings", ""])
        lines.extend(f"- {item}" for item in failures if isinstance(item, str))
    else:
        lines.extend(
            [
                "",
                "## Blocking findings",
                "",
                "None found. The compiler rejected the source exactly as "
                "declared and published no forbidden native artifact.",
            ]
        )
    return "\n".join(lines)


def _reject_unknown_keys(
    value: dict[str, Any],
    allowed: set[str],
    label: str,
) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise ExpectedFailureError(
            f"{label} contains unknown fields: {', '.join(unknown)}"
        )


def _required_text(value: dict[str, Any], key: str, label: str) -> str:
    item = value.get(key)
    if not isinstance(item, str) or not item.strip():
        raise ExpectedFailureError(f"{label} requires a non-empty {key}")
    return item.strip()


def _optional_text(value: dict[str, Any], key: str) -> str | None:
    item = value.get(key)
    if item is None:
        return None
    if not isinstance(item, str) or not item.strip():
        raise ExpectedFailureError(f"{key} must be a non-empty string")
    return item.strip()


def _required_nonnegative_int(
    value: dict[str, Any],
    key: str,
    index: int,
) -> int:
    item = value.get(key)
    if not isinstance(item, int) or isinstance(item, bool) or item < 0:
        raise ExpectedFailureError(
            f"diagnostic {index} {key} must be a nonnegative integer"
        )
    return item


def _required_positive_int(
    value: dict[str, Any],
    key: str,
    index: int,
) -> int:
    item = value.get(key)
    if not isinstance(item, int) or isinstance(item, bool) or item <= 0:
        raise ExpectedFailureError(
            f"diagnostic {index} {key} must be a positive integer"
        )
    return item


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point used by trusted audit workflows."""
    parser = argparse.ArgumentParser()
    parser.add_argument("contract", type=Path)
    parser.add_argument("--weavec", type=Path, required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--max-tokens", type=int, required=True)
    parser.add_argument("--llm-endpoint", default=None)
    parser.add_argument("--report-out", type=Path, required=True)
    args = parser.parse_args(argv)
    return run_expected_failure_audit(
        contract_path=args.contract,
        weavec=args.weavec,
        model=args.model,
        max_tokens=args.max_tokens,
        report_out=args.report_out,
        llm_endpoint=args.llm_endpoint,
    )


if __name__ == "__main__":
    raise SystemExit(main())
