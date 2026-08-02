"""Tests for deterministic LLVM optimization remark analysis."""

from pathlib import Path

from weave_loupe.optimization_remarks import (
    OPTIMIZATION_REMARKS_FORMAT,
    analyze_optimization_remarks,
)


def test_analyze_optimization_remarks_produces_stable_golden_summary() -> None:
    path = Path(__file__).parent / "fixtures" / "optimization" / "remarks.yaml"
    text = path.read_text(encoding="utf-8")

    analysis = analyze_optimization_remarks(text)

    assert analysis == analyze_optimization_remarks(text)
    assert analysis["format"] == OPTIMIZATION_REMARKS_FORMAT
    assert analysis["available"] is True
    assert analysis["valid"] is True
    assert analysis["failure_reason"] is None
    assert analysis["documents"] == 3
    assert analysis["summary"]["total"] == 3
    assert analysis["summary"]["by_category"] == {
        "analysis-fp-commute": 1,
        "missed": 1,
        "passed": 1,
    }
    assert analysis["summary"]["by_pass"] == {
        "inline": 1,
        "loop-vectorize": 2,
    }
    assert analysis["summary"]["by_function"] == {"main": 3}
    assert analysis["summary"]["by_pass_and_category"] == {
        "inline": {"passed": 1},
        "loop-vectorize": {
            "analysis-fp-commute": 1,
            "missed": 1,
        },
    }

    records = {item["name"]: item for item in analysis["records"]}
    inlined = records["Inlined"]
    assert inlined["location"] == {
        "file": "src/μ.weave",
        "line": 12,
        "column": 4,
    }
    assert inlined["hotness"] == 150
    assert inlined["message"] == "helper inlined into main"
    assert inlined["unknown_fields"] == {"Extra": {"Nested": True}}

    missed = records["CantVectorize"]
    assert missed["location"] is None
    assert missed["message"] == "loop not vectorized: unsafe dependence"
    assert analysis["summary"]["highest_value_missed"] == [
        {
            "identity": missed["identity"],
            "category": "missed",
            "pass": "loop-vectorize",
            "name": "CantVectorize",
            "function": "main",
            "location": None,
            "hotness": 80,
            "message": "loop not vectorized: unsafe dependence",
        }
    ]


def test_analyze_optimization_remarks_ignores_stage_comments() -> None:
    text = """\
# weavec optimization stage: llvm-ir
--- !Passed
Pass: inline
Name: Inlined
Function: main
...

# weavec optimization stage: target-codegen
--- !Analysis
Pass: asm-printer
Name: InstructionCount
Function: main
...
"""

    analysis = analyze_optimization_remarks(text)

    assert analysis["valid"] is True
    assert analysis["documents"] == 2
    assert analysis["summary"]["total"] == 2
    assert analysis["summary"]["by_category"] == {
        "analysis": 1,
        "passed": 1,
    }


def test_analyze_optimization_remarks_reports_bad_documents() -> None:
    text = """\
--- !Passed
Pass: inline
Name: Inlined
Function: main
...
--- !Unexpected
Pass: custom
Name: NewKind
Function: main
...
---
Pass: [unterminated
"""

    analysis = analyze_optimization_remarks(text)

    assert analysis["available"] is True
    assert analysis["valid"] is False
    assert analysis["documents"] == 3
    assert analysis["summary"]["total"] == 2
    assert [item["code"] for item in analysis["errors"]] == [
        "unsupported-remark-kind",
        "malformed-yaml",
    ]
    assert "unsupported LLVM optimization remark kind" in analysis["failure_reason"]
    assert "expected ',' or ']'" in analysis["failure_reason"]


def test_analyze_optimization_remarks_handles_missing_artifact() -> None:
    analysis = analyze_optimization_remarks(None)

    assert analysis["available"] is False
    assert analysis["valid"] is False
    assert analysis["documents"] == 0
    assert analysis["records"] == []
