"""``loupe audit`` — gated LLM review of compiler evidence."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

from weave_loupe.analysis import analyze_bundle
from weave_loupe.audit_result import (
    AuditProtocolError,
    collect_audit_metadata,
    metadata_json,
    parse_audit_response,
    render_audit_report,
)
from weave_loupe.bundle import BundleError, capture_bundle, load_bundle
from weave_loupe.evidence_report import insert_complete_evidence
from weave_loupe.llm import LlmError, chat_completion, load_config
from weave_loupe.templates import render_audit_prompt


def run_audit(
    *,
    weave_files: list[Path],
    model: str,
    weavec: Path | None,
    llvm_out: Path | None,
    wir_out: Path | None,
    report_out: Path | None,
    max_tokens: int,
    verbose: bool,
) -> int:
    response = ""
    report = ""
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
            optimized_llvm = bundle.artifact_text("optimized_llvm") or ""
            assembly = bundle.artifact_text("assembly") or ""
            disassembly = bundle.artifact_text("disassembly") or ""
            optimization_record = (
                bundle.artifact_text("optimization_record") or ""
            )
            build_manifest = bundle.artifact_text("build_manifest") or ""
            trace = bundle.artifact_text("trace") or ""
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
            weave_source = "\n\n".join(source_blocks)
            analysis = analyze_bundle(bundle)
            diagnostics = bundle.artifact_json("diagnostics")
            diagnostics_text = json.dumps(
                diagnostics, indent=2, sort_keys=True, ensure_ascii=False
            )
            analysis_text = json.dumps(
                analysis, indent=2, sort_keys=True, ensure_ascii=False
            )
            metadata = collect_audit_metadata(
                sources=weave_files,
                weavec=weavec,
                model=model,
                bundle=bundle,
            )
            prompt = render_audit_prompt(
                source_path=", ".join(source_names),
                weave_source=weave_source,
                wir=wir,
                llvm_ir=llvm_ir,
                optimized_llvm=optimized_llvm,
                assembly=assembly,
                disassembly=disassembly,
                optimization_record=optimization_record,
                diagnostics_json=diagnostics_text,
                analysis_json=analysis_text,
                metadata_json=metadata_json(metadata),
            )

            config = load_config(model=model, max_tokens=max_tokens)
            response = chat_completion(config, prompt)
            verdict = parse_audit_response(response)
            report = render_audit_report(
                verdict=verdict,
                metadata=metadata,
                model_response=response,
            )
            if verbose:
                report = insert_complete_evidence(
                    report,
                    [
                        ("Weave source", "lisp", weave_source),
                        ("WIR", "lisp", wir),
                        ("Raw LLVM IR", "llvm", llvm_ir),
                        ("Optimized LLVM IR", "llvm", optimized_llvm),
                        ("Target assembly", "asm", assembly),
                        (
                            "Linked executable disassembly",
                            "asm",
                            disassembly,
                        ),
                        (
                            "LLVM optimization record",
                            "yaml",
                            optimization_record,
                        ),
                        ("Diagnostics", "json", diagnostics_text),
                        ("Deterministic analysis", "json", analysis_text),
                        ("Build manifest", "json", build_manifest),
                        ("Compiler trace", "json", trace),
                    ],
                )

        sys.stdout.write(report)
        if not report.endswith("\n"):
            sys.stdout.write("\n")

        if not verdict.passed:
            if report_out is not None and report_out.exists():
                report_out.unlink()
            print(
                f"loupe audit: FAILED [{verdict.code}]: {verdict.reason}",
                file=sys.stderr,
            )
            return 2

        if report_out is not None:
            report_out.parent.mkdir(parents=True, exist_ok=True)
            report_out.write_text(report, encoding="utf-8")
        return 0
    except (OSError, BundleError, LlmError, AuditProtocolError) as exc:
        if report_out is not None and report_out.exists():
            report_out.unlink()
        if response:
            sys.stdout.write(response)
            if not response.endswith("\n"):
                sys.stdout.write("\n")
        print(f"loupe audit: {exc}", file=sys.stderr)
        return 1
