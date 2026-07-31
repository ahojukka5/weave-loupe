"""Tests for the bundle verification command."""

from __future__ import annotations

import json
from pathlib import Path

from weave_loupe.bundle import capture_bundle
from weave_loupe.commands.verify_bundle import run_verify_bundle


def test_verify_bundle_command_writes_valid_json(
    tmp_path: Path,
    source_file: Path,
    fake_weavec: Path,
    capsys,
) -> None:
    bundle = tmp_path / "demo.loupe"
    capture_bundle(sources=[source_file], output=bundle, weavec=fake_weavec)

    code = run_verify_bundle(
        bundle=bundle,
        json_out=None,
        allow_undeclared=False,
    )

    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert payload["format"] == "weave-loupe-bundle-verification-v1"
    assert payload["valid"] is True
    assert payload["problem_count"] == 0


def test_verify_bundle_command_reports_integrity_failure(
    tmp_path: Path,
    source_file: Path,
    fake_weavec: Path,
    capsys,
) -> None:
    bundle = tmp_path / "demo.loupe"
    output = tmp_path / "verification.json"
    capture_bundle(sources=[source_file], output=bundle, weavec=fake_weavec)
    (bundle / "undeclared.txt").write_text("extra", encoding="utf-8")

    code = run_verify_bundle(
        bundle=bundle,
        json_out=output,
        allow_undeclared=False,
    )

    captured = capsys.readouterr()
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert code == 2
    assert payload["valid"] is False
    assert payload["problems"][0]["code"] == "undeclared-file"
    assert "1 integrity problem" in captured.err
