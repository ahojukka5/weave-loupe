"""Tests for public bundle comparisons."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from weave_loupe.bundle import Bundle
from weave_loupe.bundle_diffing import compare_bundles


def test_bundle_comparison_reports_wir_only_change(tmp_path: Path) -> None:
    before = _bundle(tmp_path, "before", helper=False)
    after = _bundle(tmp_path, "after", helper=True)

    comparison = compare_bundles(before, after)

    assert comparison["format"] == "weave-loupe-diff-v2"
    assert list(comparison["analysis"])[0] == "wir"
    assert comparison["analysis"]["wir"]["functions"]["added"] == ["helper"]
    assert "analysis.wir" in comparison["summary"]["changed_sections"]
    assert any(
        item["section"] == "analysis.wir"
        and item["path"] == "functions.helper"
        and item["classification"] == "semantic"
        for item in comparison["changes"]
    )
    assert comparison["analysis"]["llvm"]["changed"] is False


def test_bundle_comparison_reports_structured_remark_changes(tmp_path: Path) -> None:
    before = _bundle(
        tmp_path,
        "before",
        helper=False,
        optimization_record="""\
--- !Passed
Pass: inline
Name: Inlined
Function: main
Args:
  - String: inlined helper
...
""",
    )
    after = _bundle(
        tmp_path,
        "after",
        helper=False,
        optimization_record="""\
--- !Missed
Pass: inline
Name: NoDefinition
Function: main
Args:
  - String: helper has no definition
...
""",
    )

    comparison = compare_bundles(before, after)

    remarks = comparison["optimization_remarks"]
    assert remarks["changed"] is True
    assert [item["category"] for item in remarks["added"]] == ["missed"]
    assert [item["category"] for item in remarks["removed"]] == ["passed"]
    assert remarks["counters"]["by_category"] == {
        "missed": {"before": 0, "after": 1, "delta": 1, "changed": True},
        "passed": {"before": 1, "after": 0, "delta": -1, "changed": True},
    }
    remark_changes = {
        item["kind"]: item
        for item in comparison["changes"]
        if item["section"] == "optimization_remarks"
    }
    assert remark_changes["added"]["after"]["name"] == "NoDefinition"
    assert remark_changes["added"]["severity"] == "warning"
    assert remark_changes["removed"]["before"]["name"] == "Inlined"
    assert remark_changes["removed"]["severity"] == "warning"


def test_bundle_comparison_preserves_v1_shape(tmp_path: Path) -> None:
    before = _bundle(tmp_path, "before", helper=False)
    after = _bundle(tmp_path, "after", helper=True)

    comparison = compare_bundles(before, after, format_version="v1")

    assert comparison["format"] == "weave-loupe-diff-v1"
    assert "analysis" not in comparison
    assert set(comparison) == {
        "format",
        "llvm_metrics",
        "trace_actions",
        "trace_passes",
    }


def _bundle(
    tmp_path: Path,
    name: str,
    *,
    helper: bool,
    optimization_record: str | None = None,
) -> Bundle:
    root = tmp_path / name
    source = root / "sources" / "000-demo.weave"
    artifacts = root / "artifacts"
    logs = root / "logs"
    source.parent.mkdir(parents=True)
    artifacts.mkdir(parents=True)
    logs.mkdir(parents=True)
    source.write_text("(program (entry main))\n", encoding="utf-8")
    wir = (
        "(core-module (core-version 2) (decls "
        "(fn main (params) (returns i32) (do (return (const_i32 0))))"
        + (
            " (fn helper (params) (returns i32) (do (return (const_i32 1))))"
            if helper
            else ""
        )
        + "))\n"
    )
    llvm = "define i32 @main() {\nentry:\n  ret i32 0\n}\n"
    values = {
        "wir": wir,
        "llvm": llvm,
        "optimized_llvm": llvm,
        "assembly": "main:\n  retq\n",
        "disassembly": (
            "demo: file format elf64-x86-64\n"
            "0000000000001000 <main>:\n"
            "    1000: c3 retq\n"
        ),
        "optimization_record": optimization_record
        or "--- !Passed\nPass: inline\nName: Inlined\nFunction: main\n...\n",
        "diagnostics": json.dumps({"diagnostics": []}) + "\n",
        "trace": json.dumps({"events": []}) + "\n",
        "build_manifest": json.dumps({"target": "x86_64"}) + "\n",
    }
    paths = {
        "wir": "artifacts/program.wir",
        "llvm": "artifacts/program.ll",
        "optimized_llvm": "artifacts/program.optimized.ll",
        "assembly": "artifacts/program.s",
        "disassembly": "artifacts/program.disasm",
        "optimization_record": "artifacts/program.opt.yaml",
        "diagnostics": "artifacts/diagnostics.json",
        "trace": "artifacts/trace.json",
        "build_manifest": "artifacts/build-manifest.json",
    }
    entries: dict[str, dict[str, Any]] = {}
    for artifact, value in values.items():
        path = root / paths[artifact]
        path.write_text(value, encoding="utf-8")
        entries[artifact] = _entry(root, path)
    stdout = logs / "stdout.txt"
    stderr = logs / "stderr.txt"
    stdout.write_text("", encoding="utf-8")
    stderr.write_text("", encoding="utf-8")
    manifest = {
        "format": "weave-loupe-bundle-v1",
        "compiler": {"binary": "weavec", "command": [], "exit_code": 0},
        "sources": [{**_entry(root, source), "index": 0, "input": "demo.weave"}],
        "artifacts": entries,
        "logs": {"stdout": _entry(root, stdout), "stderr": _entry(root, stderr)},
    }
    return Bundle(root=root, manifest=manifest)


def _entry(root: Path, path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "path": path.relative_to(root).as_posix(),
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }
