"""Tests for deterministic expected compiler-failure audits."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from weave_loupe.bundle import Bundle
from weave_loupe.expected_failure_audit import (
    EXPECTED_FAILURE_FORMAT,
    evaluate_expected_failure,
    expected_failure_report_reasons,
    load_expected_failure_contract,
    report_path_for_contract,
)


def _write_contract(tmp_path: Path) -> tuple[Path, Path]:
    source = tmp_path / "missing_module.weave"
    source.write_text(
        "(module application\n"
        "  (import absent (answer))\n"
        "  (entry main (params) (returns i32) "
        "(do (return (call answer)))))\n",
        encoding="utf-8",
    )
    contract = tmp_path / "missing_module.audit.failure.toml"
    contract.write_text(
        f'format = "{EXPECTED_FAILURE_FORMAT}"\n'
        'sources = ["missing_module.weave"]\n'
        "exit_code = 10\n"
        'phase = "frontend"\n\n'
        "[[diagnostics]]\n"
        'code = "frontend.module.import-missing-module"\n'
        'severity = "error"\n'
        "source_index = 0\n"
        "start_line = 2\n"
        "start_column = 11\n"
        "end_line = 2\n"
        "end_column = 17\n"
        'span_text = "absent"\n'
        'operand_role = "import-module"\n'
        'symbol = "absent"\n'
        'span_origin = "compiler-semantic"\n'
        "analysis_complete = true\n",
        encoding="utf-8",
    )
    return source, contract


def _bundle(tmp_path: Path, source: Path, *, executable: bool = False) -> Bundle:
    root = tmp_path / "bundle"
    artifacts = root / "artifacts"
    artifacts.mkdir(parents=True)
    start = source.read_bytes().index(b"absent")
    diagnostics = artifacts / "diagnostics.json"
    diagnostics.write_text(
        json.dumps(
            {
                "format": "weavec-diagnostics-v1",
                "status": "failed",
                "phase": "frontend",
                "exit_code": 10,
                "raw_exit_code": 10,
                "diagnostics": [
                    {
                        "code": "frontend.module.import-missing-module",
                        "severity": "error",
                        "phase": "frontend",
                        "message": "missing module",
                        "source": str(source.resolve()),
                        "span_origin": "compiler-semantic",
                        "span": {
                            "start_byte": start,
                            "end_byte": start + len(b"absent"),
                            "start_line": 2,
                            "start_column": 11,
                            "end_line": 2,
                            "end_column": 17,
                        },
                        "analysis_complete": True,
                        "operand_role": "import-module",
                        "symbol": "absent",
                        "candidates": [],
                        "related_locations": [],
                        "repairs": [],
                    }
                ],
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    artifact_entries: dict[str, dict[str, str]] = {
        "diagnostics": {"path": "artifacts/diagnostics.json"}
    }
    if executable:
        program = artifacts / "program"
        program.write_bytes(b"native")
        artifact_entries["executable"] = {"path": "artifacts/program"}
    return Bundle(
        root=root,
        manifest={
            "compiler": {"exit_code": 10},
            "artifacts": artifact_entries,
            "sources": [],
        },
    )


def test_contract_loads_ordered_sources_and_report_path(tmp_path: Path) -> None:
    source, path = _write_contract(tmp_path)

    contract = load_expected_failure_contract(path)

    assert contract.sources == (source,)
    assert contract.exit_code == 10
    assert contract.diagnostics[0].span_text == "absent"
    assert report_path_for_contract(path) == tmp_path / "missing_module.md"


def test_expected_failure_matches_exact_diagnostic_and_span(
    tmp_path: Path,
) -> None:
    source, path = _write_contract(tmp_path)
    contract = load_expected_failure_contract(path)

    result = evaluate_expected_failure(
        bundle=_bundle(tmp_path, source),
        contract=contract,
    )

    assert result["passed"] is True
    assert result["published_forbidden_artifacts"] == []
    assert result["diagnostics"][0]["passed"] is True


def test_expected_failure_rejects_published_native_artifact(
    tmp_path: Path,
) -> None:
    source, path = _write_contract(tmp_path)
    contract = load_expected_failure_contract(path)

    result = evaluate_expected_failure(
        bundle=_bundle(tmp_path, source, executable=True),
        contract=contract,
    )

    assert result["passed"] is False
    assert result["published_forbidden_artifacts"] == ["executable"]
    assert any("forbidden native artifacts" in item for item in result["failures"])


def test_report_contract_identity_detects_content_drift(tmp_path: Path) -> None:
    _, contract = _write_contract(tmp_path)
    report = tmp_path / "missing_module.md"
    digest = hashlib.sha256(contract.read_bytes()).hexdigest()
    report.write_text(
        "## Audited inputs\n\n"
        "- Runtime matrix `missing_module.audit.failure.toml` — SHA-256 "
        f"`{digest}`\n",
        encoding="utf-8",
    )

    assert expected_failure_report_reasons(report) == ()

    contract.write_text(
        contract.read_text(encoding="utf-8") + "# changed\n",
        encoding="utf-8",
    )
    assert expected_failure_report_reasons(report) == (
        "expected-failure contract content changed since audit",
    )
