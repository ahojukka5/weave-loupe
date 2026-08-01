"""Tests for complete bundle comparisons."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from weave_loupe.bundle import Bundle, capture_bundle, load_bundle
from weave_loupe.diffing import compare_bundles


def test_compare_bundles_v2_is_empty_for_identical_evidence(
    tmp_path: Path,
) -> None:
    left = _bundle(tmp_path, "left")
    right = _bundle(tmp_path, "right")

    comparison = compare_bundles(left, right)

    assert comparison["format"] == "weave-loupe-diff-v2"
    assert comparison["summary"] == {
        "changed": False,
        "total_changes": 0,
        "by_classification": {},
        "by_severity": {},
        "changed_sections": [],
        "has_errors": False,
        "has_warnings": False,
    }
    assert comparison["changes"] == []
    assert comparison == compare_bundles(left, right)


def test_compare_bundles_preserves_explicit_v1_projection(
    tmp_path: Path,
    source_file: Path,
    fake_weavec: Path,
) -> None:
    left = tmp_path / "left.loupe"
    right = tmp_path / "right.loupe"
    capture_bundle(sources=[source_file], output=left, weavec=fake_weavec)
    capture_bundle(sources=[source_file], output=right, weavec=fake_weavec)

    comparison = compare_bundles(
        load_bundle(left),
        load_bundle(right),
        format_version="v1",
    )

    assert comparison["format"] == "weave-loupe-diff-v1"
    assert comparison["llvm_metrics"]["instructions"]["delta"] == 0
    assert comparison["trace_actions"]["typed-integer-wrap"]["delta"] == 0


def test_compare_bundles_covers_analysis_and_evidence_categories(
    tmp_path: Path,
) -> None:
    before = _bundle(tmp_path, "before")
    after = _bundle(
        tmp_path,
        "after",
        raw_llvm=_raw_llvm(extra_instruction=True),
        optimized_llvm=_optimized_llvm(helper=True),
        disassembly=_disassembly(helper=True, dead=True),
        diagnostics={
            "diagnostics": [
                {
                    "code": "W100",
                    "severity": "warning",
                    "message": "new warning",
                    "location": {"path": "demo.weave", "line": 2, "column": 3},
                }
            ]
        },
        trace={
            "events": [
                {"action": "lower", "pass": "emit", "category": "codegen"},
                {"action": "parse", "pass": "front", "category": "frontend"},
            ]
        },
        optimization_record=(
            "---\nPass: inline\nName: Missed\nFunction: main\n"
            "---\nPass: loop\nName: Passed\nFunction: helper\n"
        ),
        build_manifest={"target": "x86_64", "optimizer": "new"},
        omit_artifacts={"assembly"},
    )

    comparison = compare_bundles(before, after)
    changes = comparison["changes"]

    assert comparison["summary"]["changed"] is True
    assert comparison["analysis"]["llvm"]["metrics"]["add"]["delta"] == 1
    assert (
        comparison["analysis"]["optimized_llvm"]["metrics"]["functions"]["delta"] == 2
    )
    native = comparison["analysis"]["native"]
    assert "helper" in native["functions"]["added"]
    assert "dead" in native["functions"]["added"]
    assert "dead" in native["sets"]["unreachable_program_functions"]["added"]
    assert comparison["analysis"]["diagnostics"]["added"][0]["code"] == "W100"
    assert comparison["analysis"]["trace"]["events"]["order_changed"] is True
    assert comparison["artifacts"]["items"]["assembly"]["status"] == "removed"
    assert comparison["artifacts"]["items"]["llvm"]["status"] == "hash-changed"
    assert comparison["manifest"]["changed"] is True
    assert comparison["optimization_remarks"]["changed"] is True
    assert any(
        item["classification"] == "semantic"
        and item["section"] == "analysis.diagnostics"
        for item in changes
    )
    assert any(
        item["classification"] == "evidence"
        and item["path"] == "assembly"
        and item["kind"] == "removed"
        for item in changes
    )
    assert changes == sorted(
        changes,
        key=lambda item: (
            item["section"],
            item["path"],
            item["kind"],
            item["classification"],
            item["severity"],
        ),
    )


def test_compare_bundles_compares_runtime_and_contract_context(
    tmp_path: Path,
) -> None:
    before = _bundle(tmp_path, "before")
    after = _bundle(tmp_path, "after")
    before_context = {
        "runtime": {
            "passed": True,
            "cases": [
                {
                    "name": "demo",
                    "stdout": "1\n",
                    "elapsed_seconds": 0.1,
                }
            ],
        },
        "native_budget": {"configured": True, "passed": True, "failures": []},
        "optimized_llvm_budget": {
            "configured": True,
            "passed": True,
            "failures": [],
        },
    }
    after_context = {
        "runtime": {
            "passed": False,
            "cases": [
                {
                    "name": "demo",
                    "stdout": "2\n",
                    "elapsed_seconds": 99.0,
                }
            ],
        },
        "native_budget": {
            "configured": True,
            "passed": False,
            "failures": ["instruction budget exceeded"],
        },
        "optimized_llvm_budget": {
            "configured": True,
            "passed": True,
            "failures": [],
        },
    }

    comparison = compare_bundles(
        before,
        after,
        before_context=before_context,
        after_context=after_context,
    )

    supplemental = comparison["supplemental"]
    assert supplemental["runtime"]["available"] is True
    assert supplemental["runtime"]["changed"] is True
    assert supplemental["native_budget"]["changed"] is True
    assert supplemental["optimized_llvm_budget"]["changed"] is False
    runtime_differences = supplemental["runtime"]["differences"]
    assert not any("elapsed_seconds" in item["path"] for item in runtime_differences)
    assert any(
        item["classification"] == "semantic"
        and item["section"] == "supplemental.runtime"
        for item in comparison["changes"]
    )


def test_compare_bundles_rejects_unknown_format(tmp_path: Path) -> None:
    bundle = _bundle(tmp_path, "bundle")

    try:
        compare_bundles(bundle, bundle, format_version="v99")
    except ValueError as exc:
        assert "expected v1 or v2" in str(exc)
    else:
        raise AssertionError("unknown diff format was accepted")


def _bundle(
    tmp_path: Path,
    name: str,
    *,
    raw_llvm: str | None = None,
    optimized_llvm: str | None = None,
    disassembly: str | None = None,
    diagnostics: dict[str, Any] | None = None,
    trace: dict[str, Any] | None = None,
    optimization_record: str | None = None,
    build_manifest: dict[str, Any] | None = None,
    omit_artifacts: set[str] | None = None,
) -> Bundle:
    root = tmp_path / name
    source_path = root / "sources" / "000-demo.weave"
    artifact_dir = root / "artifacts"
    log_dir = root / "logs"
    source_path.parent.mkdir(parents=True)
    artifact_dir.mkdir(parents=True)
    log_dir.mkdir(parents=True)
    source_path.write_text("(fn main () i32 0)\n", encoding="utf-8")

    artifact_values: dict[str, str] = {
        "wir": "(program (fn main (params) (returns i32) (ret 0)))\n",
        "llvm": raw_llvm or _raw_llvm(),
        "optimized_llvm": optimized_llvm or _optimized_llvm(),
        "assembly": "main:\n  retq\n",
        "disassembly": disassembly or _disassembly(),
        "optimization_record": optimization_record
        or "---\nPass: inline\nName: Passed\nFunction: main\n",
        "diagnostics": json.dumps(
            diagnostics or {"diagnostics": []},
            sort_keys=True,
        )
        + "\n",
        "trace": json.dumps(
            trace
            or {
                "events": [
                    {"action": "parse", "pass": "front", "category": "frontend"},
                    {"action": "lower", "pass": "emit", "category": "codegen"},
                ]
            },
            sort_keys=True,
        )
        + "\n",
        "build_manifest": json.dumps(
            build_manifest or {"target": "x86_64", "optimizer": "old"},
            sort_keys=True,
        )
        + "\n",
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
    artifacts: dict[str, dict[str, Any]] = {}
    for artifact_name, content in artifact_values.items():
        if artifact_name in (omit_artifacts or set()):
            continue
        path = root / paths[artifact_name]
        path.write_text(content, encoding="utf-8")
        artifacts[artifact_name] = _entry(root, path)

    stdout = log_dir / "stdout.txt"
    stderr = log_dir / "stderr.txt"
    stdout.write_text("", encoding="utf-8")
    stderr.write_text("", encoding="utf-8")
    manifest = {
        "format": "weave-loupe-bundle-v1",
        "compiler": {
            "binary": "weavec",
            "command": ["weavec", "build", "sources/000-demo.weave"],
            "exit_code": 0,
            "execution": {"termination_reason": "exited"},
        },
        "sources": [
            {
                **_entry(root, source_path),
                "index": 0,
                "input": "demo.weave",
            }
        ],
        "artifacts": artifacts,
        "logs": {
            "stdout": _entry(root, stdout),
            "stderr": _entry(root, stderr),
        },
    }
    return Bundle(root=root, manifest=manifest)


def _entry(root: Path, path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "path": path.relative_to(root).as_posix(),
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def _raw_llvm(*, extra_instruction: bool = False) -> str:
    instruction = "  %value = add i32 1, 2\n" if extra_instruction else ""
    return (
        'target triple = "x86_64-unknown-linux-gnu"\n'
        "define i32 @main() {\n"
        "entry:\n"
        f"{instruction}"
        "  ret i32 0\n"
        "}\n"
    )


def _optimized_llvm(*, helper: bool = False) -> str:
    result = (
        'target triple = "x86_64-unknown-linux-gnu"\n'
        "define i32 @main() {\n"
        "entry:\n"
        "  ret i32 0\n"
        "}\n"
    )
    if helper:
        result += (
            "define i32 @helper() {\n"
            "entry:\n"
            "  ret i32 1\n"
            "}\n"
            "define i32 @dead() {\n"
            "entry:\n"
            "  ret i32 2\n"
            "}\n"
        )
    return result


def _disassembly(*, helper: bool = False, dead: bool = False) -> str:
    result = (
        "demo: file format elf64-x86-64\n\n"
        "0000000000001000 <main>:\n"
        "    1000: c3 retq\n"
    )
    if helper:
        result += "0000000000001010 <helper>:\n    1010: c3 retq\n"
    if dead:
        result += "0000000000001020 <dead>:\n    1020: c3 retq\n"
    return result
