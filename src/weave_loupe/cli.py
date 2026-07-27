"""Command-line entry point for ``loupe``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from weave_loupe.commands.audit import run_audit
from weave_loupe.commands.capture import run_capture
from weave_loupe.commands.diff import run_diff
from weave_loupe.commands.report import run_report


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
        "--verbose",
        "-v",
        action="store_true",
        help=(
            "Embed the complete source, WIR, raw and optimized LLVM, assembly, "
            "native disassembly, diagnostics, and analysis in the Markdown report."
        ),
    )
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
        )
    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
