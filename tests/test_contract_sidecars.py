"""Tests for audit sidecars that contain contracts without runtime cases."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from weave_loupe.runtime_cases import RuntimeCasesError, load_runtime_cases


def test_optimized_llvm_only_sidecar_is_valid(tmp_path: Path) -> None:
    sidecar = tmp_path / "demo.audit.json"
    sidecar.write_text(
        json.dumps(
            {
                "format": "weave-loupe-runtime-cases-v1",
                "optimized_llvm_budget": {
                    "format": "weave-loupe-optimized-llvm-budget-v1",
                    "max_instructions": 1,
                },
            }
        ),
        encoding="utf-8",
    )

    configuration = load_runtime_cases(sidecar)

    assert configuration.path == sidecar
    assert configuration.cases == ()


def test_contractless_sidecar_remains_invalid(tmp_path: Path) -> None:
    sidecar = tmp_path / "demo.audit.json"
    sidecar.write_text(
        json.dumps({"format": "weave-loupe-runtime-cases-v1"}),
        encoding="utf-8",
    )

    with pytest.raises(RuntimeCasesError, match="optimized_llvm_budget"):
        load_runtime_cases(sidecar)
