"""Compatibility and fail-closed tests for retained compiler evidence ingestion."""

from __future__ import annotations

import ast
import hashlib
import importlib
import json
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

from tests.capability_fixtures import capability_document
from weave_loupe.analysis import analyze_bundle
from weave_loupe.bundle import (
    INGEST_REQUEST_FORMAT,
    BundleError,
    capture_bundle,
    ingest_bundle,
    load_bundle,
    validate_ingest_request_document,
)
from weave_loupe.cli import main
from weave_loupe.diffing import compare_bundles


def test_ingested_capture_preserves_bundle_and_analysis(
    tmp_path: Path,
    source_file: Path,
    fake_weavec: Path,
) -> None:
    captured_path = tmp_path / "captured.loupe"
    capture_bundle(
        sources=[source_file],
        output=captured_path,
        weavec=fake_weavec,
        include_executable=True,
    )
    captured = load_bundle(captured_path)
    request = _request_from_capture(tmp_path, source_file, captured_path)
    request_path = _write_request(tmp_path, request)
    ingested_path = tmp_path / "ingested.loupe"

    result = ingest_bundle(request=request_path, output=ingested_path)
    ingested = load_bundle(ingested_path)

    assert result.compiler_exit_code == 0
    assert ingested.manifest == captured.manifest
    assert analyze_bundle(ingested) == analyze_bundle(captured)
    comparison = compare_bundles(captured, ingested)
    assert comparison["summary"]["total_changes"] == 0


def test_failed_compiler_evidence_remains_a_valid_bundle(tmp_path: Path) -> None:
    source = tmp_path / "bad.weave"
    source.write_text("(program\n", encoding="utf-8")
    capabilities = tmp_path / "capabilities.json"
    _write_json(capabilities, capability_document())
    diagnostics = tmp_path / "diagnostics.json"
    _write_json(
        diagnostics,
        {
            "format": "weavec-diagnostics-v1",
            "diagnostics": [{"severity": "error", "message": "expected ')'"}],
        },
    )
    stdout = tmp_path / "stdout.txt"
    stdout.write_text("", encoding="utf-8")
    stderr = tmp_path / "stderr.txt"
    stderr.write_text("compile failed\n", encoding="utf-8")
    request = _minimal_request(
        source=source,
        capabilities=capabilities,
        stdout=stdout,
        stderr=stderr,
        exit_code=1,
        artifacts={"diagnostics": _entry(diagnostics, tmp_path)},
        command=[
            "weavec",
            "build",
            source.name,
            "--diagnostics-json",
            diagnostics.name,
        ],
    )
    request_path = _write_request(tmp_path, request)
    output = tmp_path / "failed.loupe"

    assert (
        main(["ingest", "--request", str(request_path), "--output", str(output)]) == 0
    )
    bundle = load_bundle(output)
    analysis = analyze_bundle(bundle)

    assert bundle.manifest["compiler"]["exit_code"] == 1
    assert bundle.artifact_path("diagnostics") is not None
    assert bundle.artifact_path("wir") is None
    assert analysis["compiler_exit_code"] == 1
    assert analysis["diagnostics"]["items"] == 1


def test_source_metadata_and_node_map_flow_into_analysis(tmp_path: Path) -> None:
    source = tmp_path / "generated.weave"
    source.write_text("(program (entry main))\n", encoding="utf-8")
    node_map = tmp_path / "node-map.json"
    _write_json(node_map, {"format": "jacquard-stable-node-map-v1", "nodes": []})
    capabilities = tmp_path / "capabilities.json"
    _write_json(capabilities, capability_document())
    stdout = tmp_path / "stdout.txt"
    stdout.write_text("", encoding="utf-8")
    stderr = tmp_path / "stderr.txt"
    stderr.write_text("", encoding="utf-8")
    request = _minimal_request(
        source=source,
        capabilities=capabilities,
        stdout=stdout,
        stderr=stderr,
        exit_code=1,
        artifacts={},
        command=["weavec", "build", source.name],
    )
    request["sources"][0]["metadata"] = {
        "producer": "weave-jacquard",
        "revision": {
            "id": "abc123",
            "repository": "ahojukka5/weave-jacquard",
            "ref": "refs/heads/main",
        },
        "document": {"id": "doc-7", "version": "3"},
        "node_map": _entry(node_map, tmp_path),
    }
    output = tmp_path / "metadata.loupe"

    ingest_bundle(
        request=_write_request(tmp_path, request),
        output=output,
    )
    bundle = load_bundle(output)
    source_metadata = analyze_bundle(bundle)["wir"]["source_metadata"][0]["metadata"]

    node_reference = source_metadata["node_map"]
    assert node_reference["artifact"] == "source_node_map_000"
    assert bundle.artifact_json(node_reference["artifact"]) == {
        "format": "jacquard-stable-node-map-v1",
        "nodes": [],
    }
    assert source_metadata["revision"]["id"] == "abc123"
    assert source_metadata["document"] == {"id": "doc-7", "version": "3"}


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (
            lambda request: request["sources"][0].__setitem__("sha256", "0" * 64),
            "SHA-256 mismatch",
        ),
        (
            lambda request: request["sources"][0].__setitem__(
                "path", "../outside.weave"
            ),
            "contained relative path",
        ),
        (
            lambda request: request.__setitem__("unknown", True),
            "unknown property",
        ),
    ],
)
def test_ingest_rejects_untrusted_requests_without_publication(
    tmp_path: Path,
    mutate,
    message: str,
) -> None:
    source = tmp_path / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")
    capabilities = tmp_path / "capabilities.json"
    _write_json(capabilities, capability_document())
    stdout = tmp_path / "stdout.txt"
    stdout.write_text("", encoding="utf-8")
    stderr = tmp_path / "stderr.txt"
    stderr.write_text("", encoding="utf-8")
    request = _minimal_request(
        source=source,
        capabilities=capabilities,
        stdout=stdout,
        stderr=stderr,
        exit_code=1,
        artifacts={},
        command=["weavec", "build", source.name],
    )
    mutate(request)
    request_path = _write_request(tmp_path, request)
    output = tmp_path / "rejected.loupe"

    with pytest.raises(BundleError, match=message):
        ingest_bundle(request=request_path, output=output)
    assert not output.exists()


def test_ingest_rejects_symlinked_inputs(tmp_path: Path) -> None:
    source = tmp_path / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")
    linked = tmp_path / "linked.weave"
    linked.symlink_to(source)
    capabilities = tmp_path / "capabilities.json"
    _write_json(capabilities, capability_document())
    stdout = tmp_path / "stdout.txt"
    stdout.write_text("", encoding="utf-8")
    stderr = tmp_path / "stderr.txt"
    stderr.write_text("", encoding="utf-8")
    request = _minimal_request(
        source=linked,
        capabilities=capabilities,
        stdout=stdout,
        stderr=stderr,
        exit_code=1,
        artifacts={},
        command=["weavec", "build", linked.name],
    )

    with pytest.raises(BundleError, match="symbolic links"):
        ingest_bundle(
            request=_write_request(tmp_path, request),
            output=tmp_path / "linked.loupe",
        )


def test_ingest_schema_is_available_offline(tmp_path: Path, capsys) -> None:
    schema_path = tmp_path / "ingest.schema.json"
    assert (
        main(
            [
                "schema",
                INGEST_REQUEST_FORMAT,
                "--output",
                str(schema_path),
            ]
        )
        == 0
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert schema["$id"].endswith(f"{INGEST_REQUEST_FORMAT}.schema.json")

    invalid = tmp_path / "invalid.json"
    _write_json(invalid, {"format": INGEST_REQUEST_FORMAT})
    assert main(["validate-json", str(invalid)]) == 2
    assert "INVALID" in capsys.readouterr().out


def test_ingest_contract_reports_shape_problems() -> None:
    problems = validate_ingest_request_document(
        {
            "format": INGEST_REQUEST_FORMAT,
            "compiler": {},
            "sources": [],
            "artifacts": {},
            "logs": {},
        }
    )
    paths = {problem.path for problem in problems}
    assert "$.compiler.command" in paths
    assert "$.sources" in paths
    assert "$.artifacts.compiler_capabilities" in paths
    assert "$.logs.stdout" in paths


def test_ingest_module_has_no_execution_dependency() -> None:
    ingest_module = importlib.import_module("weave_loupe.bundle.ingest")
    forbidden = {
        "weave_loupe.bounded_process",
        "weave_loupe.llm",
        "weave_loupe.runtime_cases",
        "weave_loupe.weavec",
    }
    assert _imports(ingest_module).isdisjoint(forbidden)


def _request_from_capture(
    root: Path,
    source: Path,
    captured_path: Path,
) -> dict[str, Any]:
    bundle = load_bundle(captured_path)
    manifest = bundle.manifest
    artifacts = manifest["artifacts"]
    assert isinstance(artifacts, dict)
    replacements = {
        str(bundle.sources[0]["path"]): source.name,
        **{
            str(entry["path"]): f"{captured_path.name}/{entry['path']}"
            for name, entry in artifacts.items()
            if name != "compiler_capabilities"
        },
    }
    compiler = manifest["compiler"]
    assert isinstance(compiler, dict)
    command = [
        replacements.get(str(argument), str(argument))
        for argument in compiler["command"]
    ]
    request_artifacts = {
        name: {
            **entry,
            "path": f"{captured_path.name}/{entry['path']}",
        }
        for name, entry in artifacts.items()
    }
    logs = manifest["logs"]
    assert isinstance(logs, dict)
    return {
        "format": INGEST_REQUEST_FORMAT,
        "source_identity": manifest["source_identity"],
        "compiler": {
            "binary": compiler["binary"],
            "command": command,
            "exit_code": compiler["exit_code"],
            "execution": compiler["execution"],
        },
        "sources": [
            {
                **_entry(source, root),
                "input": bundle.sources[0]["input"],
                "identity": bundle.sources[0]["identity"],
            }
        ],
        "artifacts": request_artifacts,
        "logs": {
            name: {
                **entry,
                "path": f"{captured_path.name}/{entry['path']}",
            }
            for name, entry in logs.items()
        },
    }


def _minimal_request(
    *,
    source: Path,
    capabilities: Path,
    stdout: Path,
    stderr: Path,
    exit_code: int,
    artifacts: dict[str, dict[str, Any]],
    command: list[str],
) -> dict[str, Any]:
    root = source.parent
    return {
        "format": INGEST_REQUEST_FORMAT,
        "source_identity": {
            "format": "weave-loupe-portable-path-v1",
            "root_kind": "common-parent",
        },
        "compiler": {
            "binary": "weavec",
            "command": command,
            "exit_code": exit_code,
            "execution": {
                "exit_code": exit_code,
                "termination_reason": "exited",
            },
        },
        "sources": [
            {
                **_entry(source, root),
                "input": source.name,
                "identity": {
                    "format": "weave-loupe-portable-path-v1",
                    "path": source.name,
                    "scope": "root",
                    "symlinked": False,
                },
            }
        ],
        "artifacts": {
            "compiler_capabilities": _entry(capabilities, root),
            **artifacts,
        },
        "logs": {
            "stdout": _entry(stdout, root),
            "stderr": _entry(stderr, root),
        },
    }


def _entry(path: Path, root: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "path": path.relative_to(root).as_posix(),
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def _write_request(root: Path, request: dict[str, Any]) -> Path:
    path = root / "ingest-request.json"
    _write_json(path, request)
    return path


def _write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _imports(module: ModuleType) -> set[str]:
    path = Path(module.__file__ or "")
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            names.add(node.module)
    return names
