"""`loupe audit` — LLM review of Weave, WIR, and emitted LLVM IR."""

from __future__ import annotations

import sys
from pathlib import Path

from weave_loupe.llm import LlmError, chat_completion, load_config
from weave_loupe.templates import render_audit_prompt
from weave_loupe.weavec import WeavecError, compile_weave


def run_audit(
    *,
    weave_file: Path,
    model: str,
    weavec: Path | None,
    llvm_out: Path | None,
    wir_out: Path | None,
    max_tokens: int,
    verbose: bool,
) -> int:
    try:
        artifacts = compile_weave(weave_file, weavec=weavec)
        if wir_out is not None:
            wir_out.parent.mkdir(parents=True, exist_ok=True)
            wir_out.write_text(artifacts.wir, encoding="utf-8")
        if llvm_out is not None:
            llvm_out.parent.mkdir(parents=True, exist_ok=True)
            llvm_out.write_text(artifacts.llvm_ir, encoding="utf-8")

        prompt = render_audit_prompt(
            source_path=str(weave_file),
            weave_source=artifacts.weave_source,
            wir=artifacts.wir,
            llvm_ir=artifacts.llvm_ir,
        )
        if verbose:
            print("=== loupe audit prompt begin ===", file=sys.stderr)
            print(prompt, file=sys.stderr, end="")
            if not prompt.endswith("\n"):
                print(file=sys.stderr)
            print("=== loupe audit prompt end ===", file=sys.stderr)

        config = load_config(model=model, max_tokens=max_tokens)
        report = chat_completion(config, prompt)
    except (OSError, WeavecError, LlmError) as exc:
        print(f"loupe audit: {exc}", file=sys.stderr)
        return 1

    sys.stdout.write(report)
    if not report.endswith("\n"):
        sys.stdout.write("\n")
    return 0
