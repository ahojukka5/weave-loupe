"""Tests for versioned native runtime audit matrices."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from weave_loupe.bundle import capture_bundle, load_bundle
from weave_loupe.runtime_cases import (
    RuntimeCasesError,
    execute_runtime_cases,
    load_runtime_cases,
)


def _write_sidecar(source: Path, document: dict[str, object]) -> Path:
    sidecar = source.with_suffix(".audit.json")
    sidecar.write_text(json.dumps(document), encoding="utf-8")
    return sidecar


def _document(cases: list[dict[str, object]]) -> dict[str, object]:
    return {
        "format": "weave-loupe-runtime-cases-v1",
        "timeout_seconds": 5,
        "inherit_environment": False,
        "cases": cases,
    }


def test_runtime_matrix_executes_exact_environment_and_output(
    tmp_path: Path, source_file: Path, fake_weavec: Path
) -> None:
    _write_sidecar(
        source_file,
        _document(
            [
                {
                    "name": "observable-result",
                    "env": {
                        "LOUPE_EXIT": "7",
                        "LOUPE_STDOUT": "answer\n",
                        "LOUPE_STDERR": "diagnostic\n",
                    },
                    "expect": {
                        "exit_code": 7,
                        "stdout": "answer\n",
                        "stderr": "diagnostic\n",
                    },
                }
            ]
        ),
    )
    bundle_path = tmp_path / "audit.loupe"
    capture_bundle(
        sources=[source_file],
        output=bundle_path,
        weavec=fake_weavec,
        include_executable=True,
    )

    result = execute_runtime_cases(
        bundle=load_bundle(bundle_path),
        sources=[source_file],
    )

    assert result["configured"] is True
    assert result["passed"] is True
    assert result["case_count"] == 1
    case = result["cases"][0]
    assert case["passed"] is True
    assert case["actual"]["exit_code"] == 7
    assert case["actual"]["stdout"] == "answer\n"
    assert case["actual"]["stderr"] == "diagnostic\n"
    assert len(result["sidecar_sha256"]) == 64
    assert len(result["executable_sha256"]) == 64


def test_runtime_matrix_records_mismatch_without_raising(
    tmp_path: Path, source_file: Path, fake_weavec: Path
) -> None:
    _write_sidecar(
        source_file,
        _document(
            [
                {
                    "name": "wrong-exit",
                    "env": {"LOUPE_EXIT": "3"},
                    "expect": {"exit_code": 4},
                }
            ]
        ),
    )
    bundle_path = tmp_path / "audit.loupe"
    capture_bundle(
        sources=[source_file],
        output=bundle_path,
        weavec=fake_weavec,
        include_executable=True,
    )

    result = execute_runtime_cases(
        bundle=load_bundle(bundle_path),
        sources=[source_file],
    )

    assert result["passed"] is False
    case = result["cases"][0]
    assert case["passed"] is False
    assert case["failures"] == ["exit code 3 did not match 4"]


def test_runtime_matrix_is_optional(
    tmp_path: Path, source_file: Path, fake_weavec: Path
) -> None:
    bundle_path = tmp_path / "audit.loupe"
    capture_bundle(
        sources=[source_file],
        output=bundle_path,
        weavec=fake_weavec,
        include_executable=True,
    )

    result = execute_runtime_cases(
        bundle=load_bundle(bundle_path),
        sources=[source_file],
    )

    assert result == {
        "format": "weave-loupe-runtime-matrix-v1",
        "configured": False,
        "passed": True,
        "case_count": 0,
        "cases": [],
    }


def test_runtime_case_schema_rejects_duplicate_names(tmp_path: Path) -> None:
    sidecar = tmp_path / "demo.audit.json"
    sidecar.write_text(
        json.dumps(
            _document(
                [
                    {"name": "same", "expect": {"exit_code": 0}},
                    {"name": "same", "expect": {"exit_code": 1}},
                ]
            )
        ),
        encoding="utf-8",
    )

    with pytest.raises(RuntimeCasesError, match="names must be unique"):
        load_runtime_cases(sidecar)


def test_runtime_cases_require_captured_executable(
    tmp_path: Path, source_file: Path, fake_weavec: Path
) -> None:
    _write_sidecar(
        source_file,
        _document([{"name": "case", "expect": {"exit_code": 1}}]),
    )
    bundle_path = tmp_path / "audit.loupe"
    capture_bundle(
        sources=[source_file],
        output=bundle_path,
        weavec=fake_weavec,
        include_executable=False,
    )

    with pytest.raises(RuntimeCasesError, match="no executable was captured"):
        execute_runtime_cases(
            bundle=load_bundle(bundle_path),
            sources=[source_file],
        )


def test_budget_only_sidecar_does_not_require_runtime_executable(
    tmp_path: Path, source_file: Path, fake_weavec: Path
) -> None:
    _write_sidecar(
        source_file,
        {
            "format": "weave-loupe-runtime-cases-v1",
            "native_budget": {
                "format": "weave-loupe-native-budget-v1",
                "max_program_owned_functions": 1,
            },
        },
    )
    bundle_path = tmp_path / "audit.loupe"
    capture_bundle(
        sources=[source_file],
        output=bundle_path,
        weavec=fake_weavec,
        include_executable=False,
    )

    result = execute_runtime_cases(
        bundle=load_bundle(bundle_path),
        sources=[source_file],
    )

    assert result["configured"] is True
    assert result["passed"] is True
    assert result["case_count"] == 0
    assert result["cases"] == []
    assert result["executable_sha256"] is None


def test_empty_audit_sidecar_is_rejected(tmp_path: Path) -> None:
    sidecar = tmp_path / "demo.audit.json"
    sidecar.write_text(
        json.dumps({"format": "weave-loupe-runtime-cases-v1"}),
        encoding="utf-8",
    )

    with pytest.raises(RuntimeCasesError, match="runtime cases or a native_budget"):
        load_runtime_cases(sidecar)
