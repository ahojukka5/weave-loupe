"""Tests for published JSON Schema compatibility contracts."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from weave_loupe.analysis import analyze_bundle
from weave_loupe.bundle import capture_bundle, load_bundle
from weave_loupe.commands.schema import run_schema, run_validate_json
from weave_loupe.diffing import compare_bundles
from weave_loupe.runtime_cases import RuntimeCasesError, load_runtime_cases
from weave_loupe.schemas import (
    JSON_SCHEMA_DRAFT,
    schema_catalog_document,
    schema_document,
    schema_example,
    schema_formats,
    schema_json,
    schema_location,
    validate_document,
)


def test_every_published_format_has_a_valid_example() -> None:
    formats = schema_formats()

    assert len(formats) >= 17
    assert formats == tuple(sorted(formats))
    for format_name in formats:
        schema = schema_document(format_name)
        example = schema_example(format_name)
        assert schema["$schema"] == JSON_SCHEMA_DRAFT
        assert schema["$id"].endswith(f"/{format_name}.schema.json")
        assert validate_document(example, format_name) == ()
        assert json.loads(schema_json(format_name)) == schema
        location, fragment = schema_location(format_name).rsplit("#", 1)
        assert Path(location).is_file()
        assert fragment == format_name


def test_schema_catalog_is_deterministic_and_independent() -> None:
    first = schema_catalog_document()
    second = schema_catalog_document()

    assert first == second
    assert first is not second
    first["schemas"].clear()
    assert second["schemas"]


def test_schema_reports_precise_structural_diagnostics() -> None:
    document = copy.deepcopy(schema_example("weave-loupe-runtime-cases-v1"))
    document["timeout_seconds"] = "slow"
    document["cases"][0]["expect"]["extra"] = True
    document["cases"][0]["expect"].pop("exit_code")

    problems = validate_document(document)
    facts = {(item.path, item.keyword) for item in problems}

    assert ("$.timeout_seconds", "type") in facts
    assert ("$.cases[0].expect.exit_code", "required") in facts
    assert ("$.cases[0].expect.extra", "additionalProperties") in facts


def test_schema_reports_invalid_enum_and_unknown_top_level_field() -> None:
    document = copy.deepcopy(schema_example("weave-loupe-portable-path-v1"))
    document["scope"] = "host"
    document["absolute_path"] = "/private/source.weave"

    problems = validate_document(document)

    assert [(item.path, item.keyword) for item in problems] == [
        ("$.absolute_path", "additionalProperties"),
        ("$.scope", "enum"),
    ]


def test_runtime_loader_applies_schema_before_semantic_validation(
    tmp_path: Path,
) -> None:
    sidecar = tmp_path / "demo.audit.json"
    sidecar.write_text(
        json.dumps(
            {
                "format": "weave-loupe-runtime-cases-v1",
                "cases": [
                    {
                        "name": "smoke",
                        "expect": {"exit_code": 0, "unexpected": True},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        RuntimeCasesError,
        match=r"\$\.cases\[0\]\.expect\.unexpected: unknown property",
    ):
        load_runtime_cases(sidecar)


def test_generated_bundle_analysis_and_diffs_match_schemas(
    tmp_path: Path,
    source_file: Path,
    fake_weavec: Path,
) -> None:
    first_path = tmp_path / "first.loupe"
    second_path = tmp_path / "second.loupe"
    capture_bundle(sources=[source_file], output=first_path, weavec=fake_weavec)
    capture_bundle(sources=[source_file], output=second_path, weavec=fake_weavec)
    first = load_bundle(first_path)
    second = load_bundle(second_path)

    assert validate_document(first.manifest, "weave-loupe-bundle-v1") == ()
    assert validate_document(analyze_bundle(first)) == ()
    assert validate_document(compare_bundles(first, second, format_version="v1")) == ()
    assert validate_document(compare_bundles(first, second)) == ()


def test_schema_command_writes_deterministic_document(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output = tmp_path / "runtime.schema.json"

    assert (
        run_schema(
            format_name="weave-loupe-runtime-cases-v1",
            output=output,
        )
        == 0
    )
    assert json.loads(output.read_text(encoding="utf-8"))["$id"].endswith(
        "weave-loupe-runtime-cases-v1.schema.json"
    )
    assert "schema:" in capsys.readouterr().out


def test_validate_json_command_returns_stable_evidence(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    document = tmp_path / "sidecar.json"
    evidence = tmp_path / "validation.json"
    value = schema_example("weave-loupe-runtime-cases-v1")
    value["unknown"] = True
    document.write_text(json.dumps(value), encoding="utf-8")

    assert (
        run_validate_json(
            document=document,
            format_name=None,
            json_out=evidence,
        )
        == 2
    )
    result = json.loads(evidence.read_text(encoding="utf-8"))
    assert result["format"] == "weave-loupe-json-validation-v1"
    assert result["valid"] is False
    assert result["problems"] == [
        {
            "code": "additionalProperties",
            "location": "$.unknown",
            "message": "unknown property",
        }
    ]
    assert "INVALID:" in capsys.readouterr().out
