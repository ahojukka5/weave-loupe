"""Command-line entry point for `loupe`."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from weave_loupe.commands.audit import run_audit


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="loupe",
        description="Tools to help in Weave compiler development.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    audit = subparsers.add_parser(
        "audit",
        help=(
            "Compile a Weave program to WIR and LLVM IR, then ask an LLM for "
            "a serious-issue and performance report."
        ),
    )
    audit.add_argument(
        "weave_file",
        type=Path,
        help="Path to a .weave source file",
    )
    audit.add_argument(
        "--model",
        default="z-ai/glm-5.2",
        help="OpenAI-compatible chat model id (default: z-ai/glm-5.2)",
    )
    audit.add_argument(
        "--weavec",
        type=Path,
        default=None,
        help="Path to the weavec binary (default: WEAVEC_BIN or PATH)",
    )
    audit.add_argument(
        "--wir-out",
        type=Path,
        default=None,
        help="Optional path to write the emitted WIR",
    )
    audit.add_argument(
        "--llvm-out",
        type=Path,
        default=None,
        help="Optional path to write the emitted LLVM IR",
    )
    audit.add_argument(
        "--max-tokens",
        type=int,
        default=4096,
        help="Maximum completion tokens for the LLM response",
    )
    audit.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print the exact prompt sent to the LLM on stderr",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "audit":
        return run_audit(
            weave_file=args.weave_file,
            model=args.model,
            weavec=args.weavec,
            llvm_out=args.llvm_out,
            wir_out=args.wir_out,
            max_tokens=args.max_tokens,
            verbose=args.verbose,
        )

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
