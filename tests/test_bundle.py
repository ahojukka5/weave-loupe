"""Tests for portable evidence bundles."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from weave_loupe.bundle import BundleError, capture_bundle, load_bundle


def test_capture_bundle_records_sources_and_artifacts(
    tmp_path: Path, source_file: Path, fake_weavec: Path
) -> None:
    output = tmp_path / "demo.loupe"
    result = capture_bundle(sources=[source_file], output=output, weavec=fake_weavec)
    assert result.compiler_exit_code == 0
    bundle = load_bundle(output)
    assert bundle.manifest["format"] == "weave-loupe-bundle-v1"
    assert bundle.sources[0]["input"] == str(source_file)
    raw_wir = bundle.artifact_text("wir")
    assert raw_wir is not None
    assert "(core-version 2)" in raw_wir
    assert "weavec-source-span-v1" in raw_wir
    assert bundle.artifact_text("optimized_llvm") is not None
    assert bundle.artifact_text("assembly") is not None
    assert bundle.artifact_text("disassembly") is not None
    assert bundle.artifact_text("optimization_record") is not None
    assert bundle.artifact_path("executable") is None


def test_capture_bundle_can_keep_executable(
    tmp_path: Path, source_file: Path, fake_weavec: Path
) -> None:
    output = tmp_path / "demo.loupe"
    capture_bundle(
        sources=[source_file],
        output=output,
        weavec=fake_weavec,
        include_executable=True,
    )
    assert load_bundle(output).artifact_path("executable") is not None


def test_capture_bundle_records_hash(
    tmp_path: Path, source_file: Path, fake_weavec: Path
) -> None:
    output = tmp_path / "demo.loupe"
    capture_bundle(sources=[source_file], output=output, weavec=fake_weavec)
    bundle = load_bundle(output)
    copied = bundle.root / str(bundle.sources[0]["path"])
    expected = hashlib.sha256(copied.read_bytes()).hexdigest()
    assert bundle.sources[0]["sha256"] == expected


def test_capture_bundle_replaces_existing_directory(
    tmp_path: Path, source_file: Path, fake_weavec: Path
) -> None:
    output = tmp_path / "demo.loupe"
    output.mkdir()
    (output / "stale").write_text("old")
    capture_bundle(sources=[source_file], output=output, weavec=fake_weavec)
    assert not (output / "stale").exists()
    assert (output / "bundle.json").is_file()


def test_load_bundle_rejects_unknown_format(tmp_path: Path) -> None:
    bundle = tmp_path / "bad.loupe"
    bundle.mkdir()
    (bundle / "bundle.json").write_text(json.dumps({"format": "unknown"}))
    with pytest.raises(BundleError, match="unsupported"):
        load_bundle(bundle)


def test_bundle_rejects_path_escape(
    tmp_path: Path, source_file: Path, fake_weavec: Path
) -> None:
    output = tmp_path / "demo.loupe"
    capture_bundle(sources=[source_file], output=output, weavec=fake_weavec)
    bundle = load_bundle(output)
    with pytest.raises(BundleError, match="escapes"):
        bundle.read_text("../outside")
