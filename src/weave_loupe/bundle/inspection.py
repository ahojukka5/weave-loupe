"""Deterministic inspection and explanation of one evidence bundle."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from weave_loupe.analysis import analyze_bundle
from weave_loupe.bundle.identity import identity_from_manifest
from weave_loupe.bundle.lineage import (
    completeness_for_bundle,
    lineage_for_bundle,
)
from weave_loupe.bundle.model import Bundle
from weave_loupe.bundle.views import VIEW_NAMES, evidence_view, information_budget

INSPECTION_FORMAT = "weave-loupe-inspection-v1"


def inspect_bundle(bundle: Bundle) -> dict[str, Any]:
    """Summarize identity, lineage, completeness, and supporting artifacts."""
    lineage = lineage_for_bundle(bundle)
    completeness = completeness_for_bundle(bundle)
    identity = identity_from_manifest(bundle.manifest)
    if not identity:
        identity = {
            "compiler_version": None,
            "compiler_sha256": None,
            "note": "historical bundle did not declare compiler content identity",
        }
    compiler = bundle.manifest.get("compiler")
    return {
        "format": INSPECTION_FORMAT,
        "identity": identity,
        "compiler": dict(compiler) if isinstance(compiler, Mapping) else {},
        "lineage": lineage,
        "completeness": completeness,
        "views": {name: evidence_view(bundle, name)["budget"] for name in VIEW_NAMES},
        "budget": information_budget(_all_files(bundle)),
    }


def analyze_evidence(bundle: Bundle) -> dict[str, Any]:
    """Combine structural analysis with lineage, completeness, and explanations."""
    analysis = analyze_bundle(bundle)
    inspection = inspect_bundle(bundle)
    return {
        "format": "weave-loupe-evidence-analysis-v1",
        "inspection": inspection,
        "analysis": analysis,
        "explanations": explanation_paths(bundle, analysis),
    }


def explanation_paths(
    bundle: Bundle, analysis: Mapping[str, Any]
) -> list[dict[str, Any]]:
    """Build deterministic, evidence-referenced explanation paths."""
    lineage = {item["id"]: item for item in lineage_for_bundle(bundle)["stages"]}
    paths: list[dict[str, Any]] = []
    wir = analysis.get("wir") if isinstance(analysis.get("wir"), Mapping) else {}
    llvm_present = lineage.get("llvm", {}).get("status") == "present"
    wir_status = lineage.get("wir", {}).get("status")
    if wir_status in {"failed", "missing"} or (
        isinstance(wir, Mapping) and wir.get("valid") is False
    ):
        paths.append(
            {
                "path": ["source", "wir"],
                "observation": (
                    str(wir.get("failure_reason"))
                    if isinstance(wir, Mapping) and wir.get("failure_reason")
                    else "WIR was not produced or is not valid"
                ),
                "evidence": ["artifacts.wir"],
            }
        )
    if isinstance(wir, Mapping) and wir.get("valid") is True and llvm_present:
        cross = wir.get("cross_stage")
        metrics = cross.get("metrics") if isinstance(cross, Mapping) else {}
        if isinstance(metrics, Mapping):
            missing = metrics.get("missing_definitions")
            unexpected = metrics.get("unexpected_definitions")
            if isinstance(missing, int) and missing:
                paths.append(
                    {
                        "path": ["wir", "llvm"],
                        "observation": (
                            "WIR-to-LLVM correspondence is missing "
                            f"{missing} definition(s)"
                        ),
                        "evidence": ["artifacts.wir", "artifacts.llvm"],
                    }
                )
            if isinstance(unexpected, int) and unexpected:
                paths.append(
                    {
                        "path": ["wir", "llvm"],
                        "observation": (
                            "LLVM contains definitions that do not correspond to WIR"
                        ),
                        "evidence": ["artifacts.wir", "artifacts.llvm"],
                    }
                )
    native = lineage.get("native", {})
    if lineage.get("optimized_llvm", {}).get("status") == "present" and native.get(
        "status"
    ) in {"failed", "missing", "partial"}:
        paths.append(
            {
                "path": ["optimized_llvm", "native"],
                "observation": (
                    "optimized LLVM was produced but native evidence is incomplete"
                ),
                "evidence": ["artifacts.optimized_llvm", "artifacts.assembly"],
            }
        )
    if not paths:
        present = [
            stage_id
            for stage_id, item in lineage.items()
            if item.get("status") == "present"
        ]
        paths.append(
            {
                "path": present,
                "observation": "no intra-bundle contract failure was derived",
                "evidence": ["compilation.lineage"],
            }
        )
    return paths


def render_inspection_text(inspection: Mapping[str, Any]) -> str:
    """Render a concise engineer-facing inspection report."""
    identity = inspection.get("identity")
    identity_map = identity if isinstance(identity, Mapping) else {}
    completeness = inspection.get("completeness")
    completeness_map = completeness if isinstance(completeness, Mapping) else {}
    lineage = inspection.get("lineage")
    lineage_map = lineage if isinstance(lineage, Mapping) else {}
    lines = [
        "Loupe evidence inspection",
        "",
        "Identity",
        f"  compiler_sha256: {identity_map.get('compiler_sha256')}",
        f"  compiler_version: {identity_map.get('compiler_version')}",
        f"  target: {identity_map.get('target')}",
        "",
        "Completeness",
        f"  complete: {completeness_map.get('complete')}",
        f"  evidence_level: {completeness_map.get('evidence_level')}",
        f"  inferred_lineage: {completeness_map.get('inferred_lineage')}",
    ]
    gaps = completeness_map.get("gaps")
    if isinstance(gaps, list):
        for gap in gaps:
            if isinstance(gap, Mapping):
                lines.append(
                    "  gap: "
                    f"{gap.get('stage')} ({gap.get('status')}): {gap.get('reason')}"
                )
    lines.extend(["", "Lineage"])
    stages = lineage_map.get("stages")
    if isinstance(stages, list):
        for item in stages:
            if not isinstance(item, Mapping):
                continue
            produced = ", ".join(str(name) for name in item.get("produced_from", []))
            arrow = f" <- {produced}" if produced else ""
            lines.append(f"  {item.get('id'):<16} {item.get('status')}{arrow}")
    lines.append("")
    return "\n".join(lines)


def render_analysis_text(document: Mapping[str, Any]) -> str:
    """Render analysis plus explanation paths as Markdown."""
    inspection = document.get("inspection")
    body = render_inspection_text(inspection if isinstance(inspection, Mapping) else {})
    lines = [body.rstrip(), "", "Explanation paths"]
    explanations = document.get("explanations")
    if isinstance(explanations, list):
        for item in explanations:
            if not isinstance(item, Mapping):
                continue
            path = " → ".join(str(part) for part in item.get("path", []))
            lines.append(f"- {path}: {item.get('observation')}")
            evidence = item.get("evidence")
            if isinstance(evidence, list):
                lines.append(f"  evidence: {', '.join(str(name) for name in evidence)}")
    lines.append("")
    return "\n".join(lines)


def _all_files(bundle: Bundle) -> dict[str, dict[str, Any]]:
    files: dict[str, dict[str, Any]] = {}
    for index, source in enumerate(bundle.sources):
        size = source.get("size")
        files[f"source[{index}]"] = {
            "size": size if isinstance(size, int) else 0,
            "text_bytes": size if isinstance(size, int) else 0,
        }
    artifacts = bundle.manifest.get("artifacts")
    if isinstance(artifacts, Mapping):
        for name, item in artifacts.items():
            if isinstance(item, Mapping):
                size = item.get("size")
                files[f"artifact.{name}"] = {
                    "size": size if isinstance(size, int) else 0,
                    "text_bytes": (
                        size if isinstance(size, int) and name != "executable" else 0
                    ),
                }
    logs = bundle.manifest.get("logs")
    if isinstance(logs, Mapping):
        for name, item in logs.items():
            if isinstance(item, Mapping):
                size = item.get("size")
                files[f"log.{name}"] = {
                    "size": size if isinstance(size, int) else 0,
                    "text_bytes": size if isinstance(size, int) else 0,
                }
    return files
