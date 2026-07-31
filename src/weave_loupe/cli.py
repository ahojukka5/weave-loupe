"""Command-line entry point for ``loupe``."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from weave_loupe.commands.audit import run_audit
from weave_loupe.commands.capture import run_capture
from weave_loupe.commands.diff import run_diff
from weave_loupe.commands.report import run_report
from weave_loupe.commands.verify_bundle import run_verify_bundle
from weave_loupe.commands.verify_report import run_verify_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="loupe",
        description="Capture, inspect, compare, and audit Weave compiler evidence.",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    subparsers = parser.add_subparsers(dest="command", required=True)

    capture = subparsers.add_parser(
        "capture", help="Compile sources into a portable evidence bundle."
    )
    capture.add_argument("weave_files", nargs="+", type=Path)
    capture.add_argument("--output", "-o", type=Path, required=True)
    capture.add_argument("--weavec", type=Path, default=None)
    capture.add_argument("--include-executable", action="store_true")
    capture.add_argument(
        "--compiler-timeout-seconds",
        type=float,
        default=None,
        help="Override the compiler wall-clock limit.",
    )
    capture.add_argument(
        "--compiler-output-bytes",
        type=int,
        default=None,
        help="Override the stdout and stderr byte ceiling per stream.",
    )

    report = subparsers.add_parser(
        "report", help="Generate a deterministic self-contained HTML report."
    )
    report.add_argument("bundle", type=Path)
    report.add_argument("--output", "-o", type=Path, required=True)
    report.add_argument("--analysis-json", type=Path, default=None)

    diff = subparsers.add_parser(
        "diff", help="Compare trace actions and LLVM structure between bundles."
    )
    diff.add_argument("before", type=Path)
    diff.add_argument("after", type=Path)
    diff.add_argument("--json-out", type=Path, default=None)
    diff.add_argument("--html-out", type=Path, default=None)

    audit = subparsers.add_parser(
        "audit", help="Ask an LLM to review the complete compiler evidence."
    )
    audit.add_argument("weave_files", nargs="+", type=Path)
    audit.add_argument("--model", default="z-ai/glm-5.2")
    audit.add_argument("--weavec", type=Path, default=None)
    audit.add_argument("--wir-out", type=Path, default=None)
    audit.add_argument("--llvm-out", type=Path, default=None)
    audit.add_argument(
        "--report-out",
        type=Path,
        default=None,
        help="Write a Markdown report only when the audit verdict is OK.",
    )
    audit.add_argument("--max-tokens", type=int, default=4096)
    audit.add_argument(
        "--compiler-timeout-seconds",
        type=float,
        default=None,
        help="Override the compiler wall-clock limit.",
    )
    audit.add_argument(
        "--compiler-output-bytes",
        type=int,
        default=None,
        help="Override the compiler stdout and stderr ceiling per stream.",
    )
    audit.add_argument(
        "--runtime-timeout-seconds",
        type=float,
        default=None,
        help="Override each configured runtime-case wall-clock limit.",
    )
    audit.add_argument(
        "--runtime-output-bytes",
        type=int,
        default=None,
        help="Override each runtime stdout and stderr ceiling per stream.",
    )
    audit.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help=(
            "Embed the complete source, WIR, raw and optimized LLVM, assembly, "
            "native disassembly, diagnostics, and analysis in the Markdown report."
        ),
    )

    verify_bundle_parser = subparsers.add_parser(
        "verify-bundle",
        help="Verify bundle structure, paths, sizes, and SHA-256 identities.",
    )
    verify_bundle_parser.add_argument("bundle", type=Path)
    verify_bundle_parser.add_argument("--json-out", type=Path, default=None)
    verify_bundle_parser.add_argument(
        "--allow-undeclared",
        action="store_true",
        help="Permit files not declared by bundle.json.",
    )

    verify = subparsers.add_parser(
        "verify-report",
        help="Check whether a generated audit report is still valid.",
    )
    verify.add_argument("report", type=Path)
    verify.add_argument(
        "--source",
        dest="sources",
        action="append",
        type=Path,
        default=None,
        help=(
            "Audited source in compiler input order; repeat for multi-source or "
            "detached reports. Recorded paths are resolved automatically when omitted."
        ),
    )
    verify.add_argument("--weavec", type=Path, default=None)
    verify.add_argument(
        "--model",
        default=os.environ.get("WEAVE_LLM_MODEL"),
        help="Current review model; defaults to WEAVE_LLM_MODEL when set.",
    )
    verify.add_argument(
        "--llm-endpoint",
        default=os.environ.get("WEAVE_LLM_ENDPOINT"),
        help="Current LLM endpoint; defaults to WEAVE_LLM_ENDPOINT when set.",
    )
    verify.add_argument(
        "--max-tokens",
        type=int,
        default=None,
        help="Current maximum completion size; omit to skip this comparison.",
    )
    verify.add_argument("--max-age-days", type=int, default=30)
    verify.add_argument("--json-out", type=Path, default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "capture":
        return run_capture(
            weave_files=args.weave_files,
            output=args.output,
            weavec=args.weavec,
            include_executable=args.include_executable,
            compiler_timeout_seconds=args.compiler_timeout_seconds,
            compiler_output_bytes=args.compiler_output_bytes,
        )
    if args.command == "report":
        return run_report(
            bundle_path=args.bundle,
            output=args.output,
            analysis_json=args.analysis_json,
        )
    if args.command == "diff":
        return run_diff(
            before=args.before,
            after=args.after,
            json_out=args.json_out,
            html_out=args.html_out,
        )
    if args.command == "audit":
        return run_audit(
            weave_files=args.weave_files,
            model=args.model,
            weavec=args.weavec,
            llvm_out=args.llvm_out,
            wir_out=args.wir_out,
            report_out=args.report_out,
            max_tokens=args.max_tokens,
            verbose=args.verbose,
            compiler_timeout_seconds=args.compiler_timeout_seconds,
            compiler_output_bytes=args.compiler_output_bytes,
            runtime_timeout_seconds=args.runtime_timeout_seconds,
            runtime_output_bytes=args.runtime_output_bytes,
        )
    if args.command == "verify-bundle":
        return run_verify_bundle(
            bundle=args.bundle,
            json_out=args.json_out,
            allow_undeclared=args.allow_undeclared,
        )
    if args.command == "verify-report":
        return run_verify_report(
            report=args.report,
            source=None,
            sources=args.sources,
            weavec=args.weavec,
            model=args.model,
            endpoint=args.llm_endpoint,
            max_tokens=args.max_tokens,
            max_age_days=args.max_age_days,
            json_out=args.json_out,
        )
    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
