"""Tests for portable evidence bundles."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from tests.capability_fixtures import capability_document
from weave_loupe.bundle import (
    BUNDLE_FORMAT,
    BundleError,
    capture_bundle,
    load_bundle,
    verify_bundle,
)


def _read_manifest(bundle: Path) -> dict[str, Any]:
    return json.loads((bundle / "bundle.json").read_text(encoding="utf-8"))


def _write_manifest(bundle: Path, manifest: dict[str, Any]) -> None:
    (bundle / "bundle.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _problem_codes(bundle: Path, *, closed: bool = True) -> set[str]:
    return {problem.code for problem in verify_bundle(bundle, closed=closed).problems}


def test_capture_bundle_records_sources_and_artifacts(
    tmp_path: Path,
    source_file: Path,
    fake_weavec: Path,
) -> None:
    output = tmp_path / "demo.loupe"
    result = capture_bundle(
        sources=[source_file],
        output=output,
        weavec=fake_weavec,
    )
    assert result.compiler_exit_code == 0
    bundle = load_bundle(output)
    assert bundle.manifest["format"] == BUNDLE_FORMAT
    assert bundle.sources[0]["input"] == source_file.name
    assert bundle.sources[0]["identity"] == {
        "format": "weave-loupe-portable-path-v1",
        "path": source_file.name,
        "scope": "root",
        "symlinked": False,
    }
    assert str(source_file.parent) not in json.dumps(bundle.manifest)
    compiler = bundle.manifest["compiler"]
    assert compiler["execution"]["termination_reason"] == "exited"
    assert compiler["execution"]["limits"]["timeout_seconds"] == 120.0
    assert len(compiler["execution"]["stdout"]["sha256"]) == 64
    capability_identity = bundle.compiler_capability_identity()
    assert capability_identity is not None
    assert capability_identity["registry_format"] == "weavec-capabilities-v1"
    assert capability_identity["compiler_version"] == "0.1.0"
    assert capability_identity["capture_profile"]["command"] == "build"
    assert bundle.artifact_text("compiler_capabilities") is not None
    raw_wir = bundle.artifact_text("wir")
    assert raw_wir is not None
    assert "(core-version 2)" in raw_wir
    assert "weavec-source-span-v1" in raw_wir
    assert bundle.artifact_text("optimized_llvm") is not None
    assert bundle.artifact_text("assembly") is not None
    assert bundle.artifact_text("disassembly") is not None
    assert bundle.artifact_text("optimization_record") is not None
    assert bundle.artifact_path("executable") is None


def test_capture_bundle_records_compiler_timeout(
    tmp_path: Path,
    source_file: Path,
) -> None:
    compiler = tmp_path / "weavec-timeout"
    registry = repr(capability_document())
    compiler.write_text(
        "#!/usr/bin/env python3\n"
        "import json\n"
        "import sys\n"
        f"CAPABILITIES = {registry}\n"
        "if sys.argv[1:] == ['capabilities', '--json']:\n"
        "    print(json.dumps(CAPABILITIES, sort_keys=True, separators=(',', ':')))\n"
        "    raise SystemExit(0)\n"
        "while True:\n"
        "    pass\n",
        encoding="utf-8",
    )
    compiler.chmod(0o755)
    output = tmp_path / "timeout.loupe"

    result = capture_bundle(
        sources=[source_file],
        output=output,
        weavec=compiler,
        compiler_timeout_seconds=0.2,
    )

    assert result.compiler_exit_code == 124
    bundle = load_bundle(output)
    assert bundle.compiler_capability_identity() is not None
    execution = bundle.manifest["compiler"]["execution"]
    assert execution["termination_reason"] == "timed_out"
    assert execution["exit_code"] is None
    assert execution["elapsed_seconds"] < 2.0


def test_capture_bundle_can_keep_executable(
    tmp_path: Path,
    source_file: Path,
    fake_weavec: Path,
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
    tmp_path: Path,
    source_file: Path,
    fake_weavec: Path,
) -> None:
    output = tmp_path / "demo.loupe"
    capture_bundle(
        sources=[source_file],
        output=output,
        weavec=fake_weavec,
    )
    bundle = load_bundle(output)
    copied = bundle.root / str(bundle.sources[0]["path"])
    expected = hashlib.sha256(copied.read_bytes()).hexdigest()
    assert bundle.sources[0]["sha256"] == expected


def test_capture_bundle_hashes_compiler_logs(
    tmp_path: Path,
    source_file: Path,
    fake_weavec: Path,
) -> None:
    output = tmp_path / "demo.loupe"
    capture_bundle(
        sources=[source_file],
        output=output,
        weavec=fake_weavec,
    )

    manifest = _read_manifest(output)
    stderr = manifest["logs"]["stderr"]
    captured = output / stderr["path"]

    assert stderr["size"] == len(captured.read_bytes())
    assert stderr["sha256"] == hashlib.sha256(captured.read_bytes()).hexdigest()
    assert load_bundle(output).log_text("stderr") == captured.read_text(
        encoding="utf-8"
    )


def test_capture_bundle_replaces_existing_directory(
    tmp_path: Path,
    source_file: Path,
    fake_weavec: Path,
) -> None:
    output = tmp_path / "demo.loupe"
    output.mkdir()
    (output / "stale").write_text("old")
    capture_bundle(
        sources=[source_file],
        output=output,
        weavec=fake_weavec,
    )
    assert not (output / "stale").exists()
    assert (output / "bundle.json").is_file()


def test_verify_bundle_accepts_valid_capture_after_move(
    tmp_path: Path,
    source_file: Path,
    fake_weavec: Path,
) -> None:
    output = tmp_path / "demo.loupe"
    moved = tmp_path / "nested" / "moved.loupe"
    capture_bundle(
        sources=[source_file],
        output=output,
        weavec=fake_weavec,
    )
    moved.parent.mkdir()
    output.rename(moved)

    verification = verify_bundle(moved)

    assert verification.valid is True
    assert verification.checked_files >= 13
    assert verification.as_dict()["format"] == ("weave-loupe-bundle-verification-v1")


def test_verify_bundle_reports_all_content_problems(
    tmp_path: Path,
    source_file: Path,
    fake_weavec: Path,
) -> None:
    output = tmp_path / "demo.loupe"
    capture_bundle(
        sources=[source_file],
        output=output,
        weavec=fake_weavec,
    )
    manifest = _read_manifest(output)

    source_path = output / manifest["sources"][0]["path"]
    source_path.write_text("tampered source", encoding="utf-8")
    llvm_path = output / manifest["artifacts"]["llvm"]["path"]
    llvm_path.unlink()
    (output / "undeclared.txt").write_text("extra", encoding="utf-8")

    verification = verify_bundle(output)
    codes = {problem.code for problem in verification.problems}

    assert verification.valid is False
    assert "file-size-mismatch" in codes
    assert "file-digest-mismatch" in codes
    assert "file-missing" in codes
    assert "undeclared-file" in codes
    with pytest.raises(BundleError, match="integrity verification failed"):
        load_bundle(output)


def test_verify_bundle_rejects_path_traversal(
    tmp_path: Path,
    source_file: Path,
    fake_weavec: Path,
) -> None:
    output = tmp_path / "demo.loupe"
    capture_bundle(
        sources=[source_file],
        output=output,
        weavec=fake_weavec,
    )
    manifest = _read_manifest(output)
    manifest["sources"][0]["path"] = "../outside.weave"
    _write_manifest(output, manifest)

    assert "file-path-traversal" in _problem_codes(output)


def test_verify_bundle_rejects_symlinked_artifact(
    tmp_path: Path,
    source_file: Path,
    fake_weavec: Path,
) -> None:
    output = tmp_path / "demo.loupe"
    capture_bundle(
        sources=[source_file],
        output=output,
        weavec=fake_weavec,
    )
    manifest = _read_manifest(output)
    artifact = output / manifest["artifacts"]["llvm"]["path"]
    target = output / manifest["sources"][0]["path"]
    artifact.unlink()
    artifact.symlink_to(target)

    assert "file-symlink" in _problem_codes(output)


def test_verify_bundle_rejects_duplicate_declared_paths(
    tmp_path: Path,
    source_file: Path,
    fake_weavec: Path,
) -> None:
    output = tmp_path / "demo.loupe"
    capture_bundle(
        sources=[source_file],
        output=output,
        weavec=fake_weavec,
    )
    manifest = _read_manifest(output)
    manifest["logs"]["stderr"] = manifest["logs"]["stdout"]
    _write_manifest(output, manifest)

    assert "duplicate-declared-path" in _problem_codes(output)


def test_verify_bundle_requires_success_artifacts(
    tmp_path: Path,
    source_file: Path,
    fake_weavec: Path,
) -> None:
    output = tmp_path / "demo.loupe"
    capture_bundle(
        sources=[source_file],
        output=output,
        weavec=fake_weavec,
    )
    manifest = _read_manifest(output)
    llvm = manifest["artifacts"].pop("llvm")
    (output / llvm["path"]).unlink()
    _write_manifest(output, manifest)

    assert "required-artifact-missing" in _problem_codes(output)


def test_verify_bundle_can_allow_undeclared_files(
    tmp_path: Path,
    source_file: Path,
    fake_weavec: Path,
) -> None:
    output = tmp_path / "demo.loupe"
    capture_bundle(
        sources=[source_file],
        output=output,
        weavec=fake_weavec,
    )
    (output / "store-note.txt").write_text(
        "external metadata",
        encoding="utf-8",
    )

    assert "undeclared-file" in _problem_codes(output)
    assert verify_bundle(output, closed=False).valid is True


def test_verify_bundle_accepts_legacy_log_paths(
    tmp_path: Path,
    source_file: Path,
    fake_weavec: Path,
) -> None:
    output = tmp_path / "demo.loupe"
    capture_bundle(
        sources=[source_file],
        output=output,
        weavec=fake_weavec,
    )
    manifest = _read_manifest(output)
    manifest["logs"] = {name: entry["path"] for name, entry in manifest["logs"].items()}
    _write_manifest(output, manifest)

    verification = verify_bundle(output)

    assert verification.valid is True
    assert verification.legacy_unhashed_logs == ("stderr", "stdout")
    assert load_bundle(output).log_path("stdout") is not None


def test_load_bundle_rejects_unknown_format(tmp_path: Path) -> None:
    bundle = tmp_path / "bad.loupe"
    bundle.mkdir()
    (bundle / "bundle.json").write_text(json.dumps({"format": "unknown"}))
    with pytest.raises(BundleError, match="format"):
        load_bundle(bundle)


def test_bundle_rejects_path_escape(
    tmp_path: Path,
    source_file: Path,
    fake_weavec: Path,
) -> None:
    output = tmp_path / "demo.loupe"
    capture_bundle(
        sources=[source_file],
        output=output,
        weavec=fake_weavec,
    )
    bundle = load_bundle(output)
    with pytest.raises(BundleError, match="escapes"):
        bundle.read_text("../outside")
