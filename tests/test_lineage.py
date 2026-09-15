"""Tests for compilation identity, lineage, and completeness."""

from __future__ import annotations

import json
from pathlib import Path

from weave_loupe.bundle import capture_bundle, load_bundle
from weave_loupe.bundle.inspection import analyze_evidence, inspect_bundle
from weave_loupe.bundle.lineage import lineage_for_bundle
from weave_loupe.bundle.localization import localize_bundle_comparison
from weave_loupe.bundle.model import Bundle
from weave_loupe.bundle.verification import verify_bundle
from weave_loupe.bundle.views import evidence_view
from weave_loupe.commands.analyze import run_analyze
from weave_loupe.commands.inspect import run_inspect
from weave_loupe.diffing import compare_bundles


def test_capture_records_compiler_identity_and_declared_lineage(
    tmp_path: Path,
    source_file: Path,
    fake_weavec: Path,
) -> None:
    output = tmp_path / "demo.loupe"
    capture_bundle(sources=[source_file], output=output, weavec=fake_weavec)
    bundle = load_bundle(output)
    compilation = bundle.manifest["compilation"]
    identity = compilation["identity"]
    lineage = compilation["lineage"]

    assert identity["compiler_sha256"]
    assert identity["compiler_version"] == "weavec v0.3.0+git.test123"
    assert identity["git_sha"] == "test123"
    assert (
        identity["capability_registry_sha256"]
        == bundle.manifest["artifacts"]["compiler_capabilities"]["sha256"]
    )
    assert compilation["retention"]["level"] == "standard"
    assert lineage["declared"] is True
    stages = {item["id"]: item for item in lineage["stages"]}
    assert stages["source"]["produced_from"] == []
    assert stages["wir"]["produced_from"] == ["source"]
    assert stages["llvm"]["produced_from"] == ["wir"]
    assert stages["optimized_llvm"]["produced_from"] == ["llvm"]
    assert stages["native"]["produced_from"] == ["optimized_llvm"]
    wir_hash = bundle.manifest["artifacts"]["wir"]["sha256"]
    assert stages["wir"]["artifact_sha256"]["wir"] == wir_hash
    assert stages["runtime"]["status"] == "unavailable"
    inspection = inspect_bundle(bundle)
    assert inspection["completeness"]["complete"] is True
    assert inspection["completeness"]["inferred_lineage"] is False


def test_wrong_compiler_hashes_are_not_comparable_by_filename(
    tmp_path: Path,
    source_file: Path,
    fake_weavec: Path,
) -> None:
    first = tmp_path / "a.loupe"
    second = tmp_path / "b.loupe"
    capture_bundle(sources=[source_file], output=first, weavec=fake_weavec)
    other = tmp_path / "weavec-other"
    other.write_bytes(fake_weavec.read_bytes() + b"\n")
    other.chmod(0o755)
    capture_bundle(sources=[source_file], output=second, weavec=other)

    left = load_bundle(first)
    right = load_bundle(second)
    localization = localize_bundle_comparison(left, right)

    assert localization["matched_inputs"] is True
    assert localization["compiler_identity_changed"] is True
    assert (
        left.manifest["compilation"]["identity"]["compiler_sha256"]
        != right.manifest["compilation"]["identity"]["compiler_sha256"]
    )


def test_historical_bundle_infers_lineage_without_rewriting_manifest(
    tmp_path: Path,
    source_file: Path,
    fake_weavec: Path,
) -> None:
    output = tmp_path / "demo.loupe"
    capture_bundle(sources=[source_file], output=output, weavec=fake_weavec)
    bundle = load_bundle(output)
    historical = bundle.manifest.copy()
    historical.pop("compilation")
    inferred = Bundle(root=bundle.root, manifest=historical)
    lineage = lineage_for_bundle(inferred)
    assert lineage["inferred"] is True
    assert "compilation" not in historical
    assert any(
        item["id"] == "wir" and item["status"] == "present"
        for item in lineage["stages"]
    )


def test_lightweight_capture_omits_ir_and_records_gaps(
    tmp_path: Path,
    source_file: Path,
    fake_weavec: Path,
) -> None:
    output = tmp_path / "light.loupe"
    capture_bundle(
        sources=[source_file],
        output=output,
        weavec=fake_weavec,
        evidence_level="lightweight",
    )
    bundle = load_bundle(output)
    assert bundle.artifact_path("wir") is None
    assert bundle.manifest["compilation"]["retention"]["level"] == "lightweight"
    stages = {
        item["id"]: item for item in bundle.manifest["compilation"]["lineage"]["stages"]
    }
    assert stages["wir"]["status"] in {"missing", "unavailable"}
    completeness = inspect_bundle(bundle)["completeness"]
    assert completeness["complete"] is True
    assert completeness["evidence_level"] == "lightweight"


def test_comparison_reports_first_changed_stage_for_wir_edit(
    tmp_path: Path,
    source_file: Path,
    fake_weavec: Path,
) -> None:
    good = tmp_path / "good.loupe"
    bad = tmp_path / "bad.loupe"
    capture_bundle(sources=[source_file], output=good, weavec=fake_weavec)
    compiler = tmp_path / "weavec-bad"
    body = fake_weavec.read_text(encoding="utf-8").replace(
        "(return (const_i32 1))",
        "(return (const_i32 2))",
    )
    compiler.write_text(body, encoding="utf-8")
    compiler.chmod(0o755)
    capture_bundle(sources=[source_file], output=bad, weavec=compiler)

    comparison = compare_bundles(load_bundle(good), load_bundle(bad))
    localization = comparison["localization"]
    assert localization["first_changed_stage"] == "wir"
    assert "source" in localization["unchanged_stages"]
    assert "not a proven defect origin" in localization["caveat"]
    assert localization["matched_inputs"] is True


def test_evidence_views_are_projections_of_one_bundle(
    tmp_path: Path,
    source_file: Path,
    fake_weavec: Path,
) -> None:
    output = tmp_path / "demo.loupe"
    capture_bundle(sources=[source_file], output=output, weavec=fake_weavec)
    bundle = load_bundle(output)
    source_tests = evidence_view(bundle, "source_tests")
    source_ir = evidence_view(bundle, "source_ir")
    full = evidence_view(bundle, "full")

    assert "artifact.wir" not in source_tests["files"]
    assert "artifact.wir" in source_ir["files"]
    assert source_ir["budget"]["raw_bytes"] <= full["budget"]["raw_bytes"]
    assert full["budget"]["objects"] >= source_tests["budget"]["objects"]


def test_inspect_and_analyze_commands(
    tmp_path: Path,
    source_file: Path,
    fake_weavec: Path,
    capsys,
) -> None:
    output = tmp_path / "demo.loupe"
    capture_bundle(sources=[source_file], output=output, weavec=fake_weavec)
    json_out = tmp_path / "inspect.json"
    analysis_out = tmp_path / "analyze.json"
    markdown_out = tmp_path / "analyze.md"

    assert (
        run_inspect(bundle_path=output, json_out=json_out, stage=None, view=None) == 0
    )
    assert (
        run_analyze(
            bundle_path=output,
            json_out=analysis_out,
            markdown_out=markdown_out,
        )
        == 0
    )
    document = analyze_evidence(load_bundle(output))
    assert document["explanations"]
    captured = capsys.readouterr()
    assert "inspection:" in captured.out
    assert json_out.is_file()
    assert "source" in markdown_out.read_text(encoding="utf-8")


def test_lineage_hash_mismatch_fails_closed(
    tmp_path: Path,
    source_file: Path,
    fake_weavec: Path,
) -> None:
    output = tmp_path / "demo.loupe"
    capture_bundle(sources=[source_file], output=output, weavec=fake_weavec)

    manifest = json.loads((output / "bundle.json").read_text(encoding="utf-8"))
    stages = manifest["compilation"]["lineage"]["stages"]
    wir = next(item for item in stages if item["id"] == "wir")
    wir["artifact_sha256"]["wir"] = "0" * 64
    (output / "bundle.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    codes = {problem.code for problem in verify_bundle(output).problems}
    assert "stage-artifact-hash-mismatch" in codes
