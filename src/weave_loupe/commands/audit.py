"""``loupe audit`` — LLM review of a complete compiler-evidence bundle."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

from weave_loupe.analysis import analyze_bundle
from weave_loupe.bundle import BundleError, capture_bundle, load_bundle
from weave_loupe.llm import LlmError, chat_completion, load_config
from weave_loupe.templates import render_audit_prompt


def run_audit(
    *,
    weave_files: list[Path],
    model: str,
    weavec: Path | None,
    llvm_out: Path | None,
    wir_out: Path | None,
    max_tokens: int,
    verbose: bool,
) -> int:
    try:
        with tempfile.TemporaryDirectory(prefix="loupe-audit-") as temp_dir:
            bundle_path = Path(temp_dir) / "audit.loupe"
            capture = capture_bundle(
                sources=weave_files,
                output=bundle_path,
                weavec=weavec,
                include_executable=False,
            )
            bundle = load_bundle(capture.bundle)
            if capture.compiler_exit_code != 0:
                logs = bundle.manifest.get("logs", {})
                stderr_path = logs.get("stderr") if isinstance(logs, dict) else None
                stderr = (
                    bundle.read_text(stderr_path).strip()
                    if isinstance(stderr_path, str)
                    else ""
                )
                raise BundleError(
                    f"weavec build failed with exit {capture.compiler_exit_code}"
                    + (f":\n{stderr}" if stderr else "")
                )

            wir = bundle.artifact_text("wir") or ""
            llvm_ir = bundle.artifact_text("llvm") or ""
            if wir_out is not None:
                wir_out.parent.mkdir(parents=True, exist_ok=True)
                wir_out.write_text(wir, encoding="utf-8")
            if llvm_out is not None:
                llvm_out.parent.mkdir(parents=True, exist_ok=True)
                llvm_out.write_text(llvm_ir, encoding="utf-8")

            source_blocks: list[str] = []
            source_names: list[str] = []
            for source in bundle.sources:
                source_name = str(source.get("input", source["path"]))
                source_names.append(source_name)
                source_blocks.append(
                    f"--- {source_name} ---\n"
                    + bundle.read_text(str(source["path"]))
                )
            analysis = analyze_bundle(bundle)
            diagnostics = bundle.artifact_json("diagnostics")
            prompt = render_audit_prompt(
                source_path=", ".join(source_names),
                weave_source="\n\n".join(source_blocks),
                wir=wir,
                llvm_ir=llvm_ir,
                diagnostics_json=json.dumps(
                    diagnostics, indent=2, sort_keys=True, ensure_ascii=False
                ),
                trace_summary_json=json.dumps(
                    analysis["trace"], indent=2, sort_keys=True
                ),
                llvm_metrics_json=json.dumps(
                    analysis["llvm"], indent=2, sort_keys=True
                ),
            )

        if verbose:
            print("=== loupe audit prompt begin ===", file=sys.stderr)
            print(prompt, file=sys.stderr, end="")
            if not prompt.endswith("\n"):
                print(file=sys.stderr)
            print("=== loupe audit prompt end ===", file=sys.stderr)

        config = load_config(model=model, max_tokens=max_tokens)
        report = chat_completion(config, prompt)
    except (OSError, BundleError, LlmError) as exc:
        print(f"loupe audit: {exc}", file=sys.stderr)
        return 1

    sys.stdout.write(report)
    if not report.endswith("\n"):
        sys.stdout.write("\n")
    return 0
