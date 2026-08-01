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
from weave_loupe.bundle import Bundle, BundleError, capture_bundle, load_bundle
from weave_loupe.deterministic_gate import apply_deterministic_gate
from weave_loupe.evidence_report import insert_complete_evidence
from weave_loupe.llm import LlmError, chat_completion, load_config
from weave_loupe.native_budget import NativeBudgetError, evaluate_native_budget
from weave_loupe.optimized_llvm_budget import (
    OptimizedLlvmBudgetError,
    evaluate_optimized_llvm_budget,
)
from weave_loupe.report_integrity import seal_audit_report
from weave_loupe.runtime_cases import RuntimeCasesError, execute_runtime_cases
from weave_loupe.templates import render_audit_prompt
from weave_loupe.wir_review import clean_wir_for_review


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
    compiler_timeout_seconds: float | None = None,
    compiler_output_bytes: int | None = None,
    runtime_timeout_seconds: float | None = None,
    runtime_output_bytes: int | None = None,
    allow_unsafe_http: bool | None = None,
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
                include_executable=True,
                compiler_timeout_seconds=compiler_timeout_seconds,
                compiler_output_bytes=compiler_output_bytes,
            )
            bundle = load_bundle(capture.bundle)
            if capture.compiler_exit_code != 0:
                raise BundleError(
                    _compiler_failure_message(
                        bundle,
                        capture.compiler_exit_code,
                    )
                )

            wir = bundle.artifact_text("wir") or ""
            review_wir = clean_wir_for_review(wir)
            llvm_ir = bundle.artifact_text("llvm") or ""
            optimized_llvm = bundle.artifact_text("optimized_llvm") or ""
            assembly = bundle.artifact_text("assembly") or ""
            disassembly = bundle.artifact_text("disassembly") or ""
            optimization_record = bundle.artifact_text("optimization_record") or ""
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
                    f"--- {source_name} ---\n" + bundle.read_text(str(source["path"]))
                )
            weave_source = "\n\n".join(source_blocks)
            analysis = analyze_bundle(bundle)
            optimized_llvm_budget = evaluate_optimized_llvm_budget(
                sources=weave_files,
                optimized_llvm=optimized_llvm,
                metrics=analysis.get("optimized_llvm"),
            )
            native_budget = evaluate_native_budget(
                sources=weave_files,
                native_analysis=analysis.get("native"),
            )
            runtime_matrix = execute_runtime_cases(
                bundle=bundle,
                sources=weave_files,
                runtime_timeout_seconds=runtime_timeout_seconds,
                runtime_output_bytes=runtime_output_bytes,
            )
            analysis["optimized_llvm_budget"] = optimized_llvm_budget
            analysis["native_budget"] = native_budget
            analysis["runtime"] = runtime_matrix
            diagnostics = bundle.artifact_json("diagnostics")
            diagnostics_text = json.dumps(
                diagnostics, indent=2, sort_keys=True, ensure_ascii=False
            )
            optimized_llvm_budget_text = json.dumps(
                optimized_llvm_budget,
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
            )
            native_budget_text = json.dumps(
                native_budget, indent=2, sort_keys=True, ensure_ascii=False
            )
            runtime_text = json.dumps(
                runtime_matrix, indent=2, sort_keys=True, ensure_ascii=False
            )
            analysis_text = json.dumps(
                analysis, indent=2, sort_keys=True, ensure_ascii=False
            )
            config = load_config(
                model=model,
                max_tokens=max_tokens,
                allow_unsafe_http=allow_unsafe_http,
            )
            native_analysis = analysis.get("native")
            metadata = collect_audit_metadata(
                sources=weave_files,
                weavec=weavec,
                model=model,
                llm_endpoint=config.endpoint_identity,
                bundle=bundle,
                runtime_matrix=runtime_matrix,
                native_analysis=(
                    native_analysis if isinstance(native_analysis, dict) else None
                ),
            )
            prompt = render_audit_prompt(
                source_path=", ".join(source_names),
                weave_source=weave_source,
                wir=review_wir,
                llvm_ir=llvm_ir,
                optimized_llvm=optimized_llvm,
                assembly=assembly,
                disassembly=disassembly,
                optimization_record=optimization_record,
                diagnostics_json=diagnostics_text,
                analysis_json=analysis_text,
                metadata_json=metadata_json(metadata),
            )

            completion = chat_completion(config, prompt)
            response = completion.content
            metadata["llm"] = completion.metadata()
            model_verdict = parse_audit_response(response)
            verdict = apply_deterministic_gate(model_verdict, analysis)
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
                        ("WIR (provenance comments hidden)", "lisp", review_wir),
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
                        (
                            "Optimized LLVM contract",
                            "json",
                            optimized_llvm_budget_text,
                        ),
                        ("Native optimization budget", "json", native_budget_text),
                        ("Runtime execution matrix", "json", runtime_text),
                        ("Diagnostics", "json", diagnostics_text),
                        ("Deterministic analysis", "json", analysis_text),
                        ("Build manifest", "json", build_manifest),
                        ("Compiler trace", "json", trace),
                    ],
                )
            report = seal_audit_report(report)

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
    except (
        OSError,
        BundleError,
        LlmError,
        AuditProtocolError,
        NativeBudgetError,
        OptimizedLlvmBudgetError,
        RuntimeCasesError,
    ) as exc:
        if report_out is not None and report_out.exists():
            report_out.unlink()
        if response:
            sys.stdout.write(response)
            if not response.endswith("\n"):
                sys.stdout.write("\n")
        print(f"loupe audit: {exc}", file=sys.stderr)
        return 1


def _compiler_failure_message(bundle: Bundle, exit_code: int) -> str:
    compiler = bundle.manifest.get("compiler")
    execution = compiler.get("execution") if isinstance(compiler, dict) else None
    reason = (
        execution.get("termination_reason") if isinstance(execution, dict) else None
    )
    description = (
        f"weavec build {reason} with compatibility exit {exit_code}"
        if isinstance(reason, str) and reason != "exited"
        else f"weavec build failed with exit {exit_code}"
    )
    stderr = (bundle.log_text("stderr") or "").strip()
    return description + (f":\n{stderr}" if stderr else "")
