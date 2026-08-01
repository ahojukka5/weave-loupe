"""Fail-closed native-budget coverage for unsupported architectures."""

from __future__ import annotations

import json
from pathlib import Path

from weave_loupe.native_budget import evaluate_native_budget


def test_native_budget_rejects_unsupported_architecture(tmp_path: Path) -> None:
    source = tmp_path / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")
    source.with_suffix(".audit.json").write_text(
        json.dumps(
            {
                "format": "weave-loupe-runtime-cases-v1",
                "native_budget": {
                    "format": "weave-loupe-native-budget-v1",
                    "max_program_owned_functions": 1,
                },
            }
        ),
        encoding="utf-8",
    )
    unsupported = {
        "available": True,
        "supported": False,
        "architecture": "unknown",
        "failure_reason": "unsupported native architecture 'riscv64'",
        "reachability_complete": False,
        "program_owned_functions": [],
        "reachable_program_functions": [],
        "unreachable_program_functions": [],
        "unreachable_program_instructions": None,
        "functions": {},
    }

    result = evaluate_native_budget(
        sources=[source],
        native_analysis=unsupported,
    )

    assert result["configured"] is True
    assert result["passed"] is False
    assert (
        "native disassembly analysis is unsupported: "
        "unsupported native architecture 'riscv64'"
    ) in result["failures"]
    assert "native program-function reachability is incomplete" in result["failures"]
