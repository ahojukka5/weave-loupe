"""``loupe audit`` — gated LLM review of compiler evidence."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from typing import Any

from weave_loupe.analysis import analyze_bundle
from weave_loupe.audit_result import (
    AuditProtocolError,
    collect_audit_metadata,
    metadata_json,
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
from weave_loupe.path_identity import (
    PathIdentityError,
    canonicalize_audit_metadata,
    plan_public_paths,
    redact_private_paths,
)
from weave_loupe.report_integrity import seal_audit_report
from weave_loupe.review_report import insert_review_provenance
from weave_loupe.runtime_cases import (
    RuntimeCasesError,
    discover_runtime_cases,
    execute_runtime_cases,
)
from weave_loupe.scalable_review import (
    EvidenceArtifact,
    ReviewPlanningError,
    ReviewPolicy,
    review_evidence,
)
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
    review_total_tokens: int = 524_288,
    review_request_tokens: int = 98_304,
    review_artifact_tokens: int = 262_144,
    audit_root: Path | None = None,
    source_names: list[str] | None = None,
) -> int:
    response = ""
    report = ""
    try:
        plan = plan_public_paths(
            weave_files,
            audit_root=audit_root,
            logical_names=source_names,
        )
        runtime_configuration = discover_runtime_cases(weave_files)
        runtime_sidecar = (
            runtime_configuration.path if runtime_configuration is not None else None
        )
        with tempfile.TemporaryDirectory(prefix="loupe-audit-") as temp_dir:
            bundle_path = Path(temp_dir) / "audit.loupe"
            capture = capture_bundle(
                sources=weave_files,
                output=bundle_path,
                weavec=weavec,
                include_executable=True,
                compiler_timeout_seconds=compiler_timeout_seconds,
                compiler_output_bytes=compiler_output_bytes,
                audit_root=audit_root,
                source_names=source_names,
            )
            bundle = load_bundle(capture.bundle)
            if capture.compiler_exit_code != 0:
                raise BundleError(
                    _compiler_failure_message(
                        bundle,
                        capture.compiler_exit_code,
                    )
                )

            raw_wir = bundle.artifact_text("wir") or ""
            raw_llvm = bundle.artifact_text("llvm") or ""
            if wir_out is not None:
                wir_out.parent.mkdir(parents=True, exist_ok=True)
                wir_out.write_text(raw_wir, encoding="utf-8")
            if llvm_out is not None:
                llvm_out.parent.mkdir(parents=True, exist_ok=True)
                llvm_out.write_text(raw_llvm, encoding="utf-8")

            def redact(value: str) -> str:
                return redact_private_paths(value, plan=plan)

            wir = redact(raw_wir)
            review_wir = clean_wir_for_review(wir)
            llvm_ir = redact(raw_llvm)
            optimized_llvm = redact(bundle.artifact_text("optimized_llvm") or "")
            assembly = redact(bundle.artifact_text("assembly") or "")
            disassembly = redact(bundle.artifact_text("disassembly") or "")
            optimization_record = redact(
                bundle.artifact_text("optimization_record") or ""
            )
            build_manifest = redact(bundle.artifact_text("build_manifest") or "")
            trace = redact(bundle.artifact_text("trace") or "")

            source_blocks: list[str] = []
            public_source_names: list[str] = []
            for source in bundle.sources:
                source_name = str(source.get("input", source["path"]))
                public_source_names.append(source_name)
                source_blocks.append(
                    f"--- {source_name} ---\n"
                    + redact(bundle.read_text(str(source["path"])))
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
                audit_root=audit_root,
                source_names=source_names,
            )
            analysis["optimized_llvm_budget"] = optimized_llvm_budget
            analysis["native_budget"] = native_budget
            analysis["runtime"] = runtime_matrix
            diagnostics = bundle.artifact_json("diagnostics")
            diagnostics_text = redact(
                json.dumps(
                    diagnostics,
                    indent=2,
                    sort_keys=True,
                    ensure_ascii=False,
                )
            )
            optimized_llvm_budget_text = redact(
                json.dumps(
                    optimized_llvm_budget,
                    indent=2,
                    sort_keys=True,
                    ensure_ascii=False,
                )
            )
            native_budget_text = redact(
                json.dumps(
                    native_budget,
                    indent=2,
                    sort_keys=True,
                    ensure_ascii=False,
                )
            )
            runtime_text = redact(
                json.dumps(
                    runtime_matrix,
                    indent=2,
                    sort_keys=True,
                    ensure_ascii=False,
                )
            )
            analysis_text = redact(
                json.dumps(
                    analysis,
                    indent=2,
                    sort_keys=True,
                    ensure_ascii=False,
                )
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
            metadata = canonicalize_audit_metadata(
                metadata,
                plan=plan,
                runtime_sidecar=runtime_sidecar,
            )
            stable_metadata = _stable_review_metadata(metadata)
            stable_metadata_text = redact(metadata_json(stable_metadata))
            prompt = render_audit_prompt(
                source_path=", ".join(public_source_names),
                weave_source=weave_source,
                wir=review_wir,
                llvm_ir=llvm_ir,
                optimized_llvm=optimized_llvm,
                assembly=assembly,
                disassembly=disassembly,
                optimization_record=optimization_record,
                diagnostics_json=diagnostics_text,
                analysis_json=analysis_text,
                metadata_json=stable_metadata_text,
                build_manifest=build_manifest,
                trace_json=trace,
            )
            artifacts = _review_artifacts(
                weave_source=weave_source,
                review_wir=review_wir,
                llvm_ir=llvm_ir,
                optimized_llvm=optimized_llvm,
                assembly=assembly,
                disassembly=disassembly,
                optimization_record=optimization_record,
                diagnostics_text=diagnostics_text,
                analysis_text=analysis_text,
                metadata_text=stable_metadata_text,
                build_manifest=build_manifest,
                trace=trace,
            )
            outcome = review_evidence(
                config=config,
                full_prompt=prompt,
                artifacts=artifacts,
                deterministic_summary=_deterministic_summary(
                    metadata=stable_metadata,
                    analysis=analysis,
                ),
                policy=ReviewPolicy(
                    max_total_tokens=review_total_tokens,
                    max_request_tokens=review_request_tokens,
                    max_artifact_tokens=review_artifact_tokens,
                ),
                complete=chat_completion,
            )
            response = outcome.response
            metadata["llm"] = outcome.final_completion.metadata()
            metadata["review"] = outcome.metadata
            verdict = apply_deterministic_gate(outcome.verdict, analysis)
            report = render_audit_report(
                verdict=verdict,
                metadata=metadata,
                model_response=response,
            )
            report = insert_review_provenance(report, outcome.metadata)
            if verbose:
                report = insert_complete_evidence(
                    report,
                    [
                        ("Weave source", "lisp", weave_source),
                        (
                            "WIR (provenance comments hidden)",
                            "lisp",
                            review_wir,
                        ),
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
                        (
                            "Native optimization budget",
                            "json",
                            native_budget_text,
                        ),
                        (
                            "Runtime execution matrix",
                            "json",
                            runtime_text,
                        ),
                        ("Diagnostics", "json", diagnostics_text),
                        (
                            "Deterministic analysis",
                            "json",
                            analysis_text,
                        ),
                        ("Build manifest", "json", build_manifest),
                        ("Compiler trace", "json", trace),
                    ],
                )
            report = seal_audit_report(redact(report))

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
        PathIdentityError,
        RuntimeCasesError,
        ReviewPlanningError,
    ) as exc:
        if report_out is not None and report_out.exists():
            report_out.unlink()
        if response:
            sys.stdout.write(response)
            if not response.endswith("\n"):
                sys.stdout.write("\n")
        print(f"loupe audit: {exc}", file=sys.stderr)
        return 1


def _review_artifacts(
    *,
    weave_source: str,
    review_wir: str,
    llvm_ir: str,
    optimized_llvm: str,
    assembly: str,
    disassembly: str,
    optimization_record: str,
    diagnostics_text: str,
    analysis_text: str,
    metadata_text: str,
    build_manifest: str,
    trace: str,
) -> tuple[EvidenceArtifact, ...]:
    return (
        EvidenceArtifact(
            "metadata",
            "Reproducibility metadata",
            "json",
            metadata_text,
        ),
        EvidenceArtifact("source", "Weave source", "lisp", weave_source),
        EvidenceArtifact("wir", "WIR review projection", "lisp", review_wir),
        EvidenceArtifact("raw_llvm", "Raw LLVM IR", "llvm", llvm_ir),
        EvidenceArtifact(
            "optimized_llvm",
            "Optimized LLVM IR",
            "llvm",
            optimized_llvm,
        ),
        EvidenceArtifact("assembly", "Target assembly", "asm", assembly),
        EvidenceArtifact(
            "disassembly",
            "Linked executable disassembly",
            "asm",
            disassembly,
        ),
        EvidenceArtifact(
            "optimization_record",
            "LLVM optimization record",
            "yaml",
            optimization_record,
        ),
        EvidenceArtifact(
            "diagnostics",
            "Diagnostics",
            "json",
            diagnostics_text,
        ),
        EvidenceArtifact(
            "analysis",
            "Complete deterministic analysis",
            "json",
            analysis_text,
        ),
        EvidenceArtifact(
            "build_manifest",
            "Compiler build manifest",
            "json",
            build_manifest,
        ),
        EvidenceArtifact("trace", "Compiler trace", "json", trace),
    )


def _stable_review_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    """Remove run-specific facts while retaining review-relevant identities."""
    source_repository = _mapping(metadata.get("source_repository"))
    loupe_repository = _mapping(metadata.get("loupe_repository"))
    weavec = _mapping(metadata.get("weavec"))
    weavec_repository = _mapping(weavec.get("repository"))
    return {
        "format": "weave-loupe-review-metadata-v1",
        "model": metadata.get("model"),
        "llm": {
            "endpoint": _mapping(metadata.get("llm")).get("endpoint"),
        },
        "source_repository_sha": source_repository.get("sha"),
        "loupe_repository_sha": loupe_repository.get("sha"),
        "auditor": metadata.get("auditor"),
        "weavec": {
            "sha256": weavec.get("sha256"),
            "version": weavec.get("version"),
            "base_version": weavec.get("base_version"),
            "git_sha": weavec.get("git_sha"),
            "development": weavec.get("development"),
            "version_source": weavec.get("version_source"),
            "repository_sha": weavec_repository.get("sha"),
        },
        "native": metadata.get("native"),
        "sources": metadata.get("sources"),
        "runtime_input": metadata.get("runtime_input"),
        "bundle": metadata.get("bundle"),
    }


def _deterministic_summary(
    *,
    metadata: dict[str, Any],
    analysis: dict[str, Any],
) -> dict[str, Any]:
    native = _mapping(analysis.get("native"))
    return {
        "format": "weave-loupe-deterministic-review-summary-v1",
        "metadata": metadata,
        "compiler_exit_code": analysis.get("compiler_exit_code"),
        "evidence": analysis.get("evidence"),
        "native": {
            "supported": native.get("supported"),
            "failure_reason": native.get("failure_reason"),
            "architecture": native.get("architecture"),
            "object_format": native.get("object_format"),
            "parser_format": native.get("parser_format"),
            "reachability_complete": native.get("reachability_complete"),
            "program_instruction_count": native.get("program_instruction_count"),
            "unreachable_program_instructions": native.get(
                "unreachable_program_instructions"
            ),
            "reachable_indirect_calls": native.get("reachable_indirect_calls"),
        },
        "deterministic_gates": {
            "optimized_llvm_budget": _gate_summary(
                analysis.get("optimized_llvm_budget")
            ),
            "native_budget": _gate_summary(analysis.get("native_budget")),
            "runtime": _runtime_summary(analysis.get("runtime")),
        },
    }


def _gate_summary(value: object) -> dict[str, Any]:
    gate = _mapping(value)
    failures = gate.get("failures")
    return {
        "configured": gate.get("configured"),
        "passed": gate.get("passed"),
        "format": gate.get("format"),
        "failure_count": (len(failures) if isinstance(failures, list) else None),
    }


def _runtime_summary(value: object) -> dict[str, Any]:
    runtime = _mapping(value)
    failures = runtime.get("failures")
    return {
        "configured": runtime.get("configured"),
        "passed": runtime.get("passed"),
        "format": runtime.get("format"),
        "case_count": runtime.get("case_count"),
        "failure_count": (len(failures) if isinstance(failures, list) else None),
    }


def _mapping(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _compiler_failure_message(bundle: Bundle, exit_code: int) -> str:
    stderr = (bundle.log_text("stderr") or "").strip()
    message = f"weavec exited with code {exit_code}"
    return f"{message}: {stderr}" if stderr else message
