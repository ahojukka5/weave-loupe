from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "regression_evidence_protocol.py"
)
SPEC = importlib.util.spec_from_file_location("regression_evidence_protocol", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def case(index: int) -> dict[str, object]:
    stages = sorted(MODULE.STAGES)
    return {
        "id": f"case-{index:02d}",
        "family": f"family-{index % 4}",
        "bad_revision": "a" * 40,
        "good_revision": f"{index:040x}"[-40:],
        "expected_stage": stages[index % len(stages)],
        "failure_mechanism": f"Known historical mechanism {index}",
        "oracle": {"command": ["bash", f"test/case-{index:02d}.sh"]},
        "relevant_tests": [f"test/case-{index:02d}.sh"],
    }


def frozen_corpus() -> dict[str, object]:
    corpus: dict[str, object] = {
        "schema": MODULE.CORPUS_SCHEMA,
        "status": "frozen",
        "loupe": {
            "repository": "ahojukka5/weave-loupe",
            "revision": "b" * 40,
        },
        "compiler": {"repository": "ahojukka5/weavec"},
        "model_review": {
            "provider": "test-provider",
            "model": "test-model",
            "configuration_id": "fixed-config-v1",
            "prompt_id": "review-v1",
        },
        "conditions": list(MODULE.CONDITIONS),
        "cases": [case(index) for index in range(10)],
    }
    normalized = MODULE.validate_corpus(corpus)
    corpus["corpus_sha256"] = MODULE.canonical_corpus_hash(normalized)
    return corpus


def results_for(corpus: dict[str, object]) -> dict[str, object]:
    rows = []
    for case_entry in corpus["cases"]:  # type: ignore[index]
        for condition in MODULE.CONDITIONS:
            deterministic = condition in {
                "deterministic",
                "deterministic-model",
            }
            rows.append(
                {
                    "case_id": case_entry["id"],
                    "condition": condition,
                    "defect_detected": condition != "source-tests",
                    "phase_localized": condition
                    in {"full-evidence", "deterministic", "deterministic-model"},
                    "mechanism_localized": condition
                    in {"deterministic", "deterministic-model"},
                    "false_positive_on_good": False,
                    "evidence_bytes": 1000,
                    "input_tokens": (
                        100 if condition == "deterministic-model" else None
                    ),
                    "output_tokens": (
                        50 if condition == "deterministic-model" else None
                    ),
                    "review_seconds": 1.0,
                    "deterministic_gate_status": (
                        "fail" if deterministic else None
                    ),
                }
            )
    return {
        "schema": MODULE.RESULT_SCHEMA,
        "corpus_sha256": corpus["corpus_sha256"],
        "rows": rows,
    }


def normalized_corpus() -> dict[str, object]:
    corpus = MODULE.validate_corpus(frozen_corpus(), require_frozen=True)
    corpus["corpus_sha256"] = MODULE.canonical_corpus_hash(corpus)
    return corpus


def test_frozen_corpus_requires_multiple_failure_families() -> None:
    corpus = frozen_corpus()
    for entry in corpus["cases"]:  # type: ignore[index]
        entry["family"] = "one-family"
    corpus.pop("corpus_sha256")

    with pytest.raises(MODULE.ProtocolError, match="at least four failure families"):
        MODULE.validate_corpus(corpus, require_frozen=True)


def test_results_require_all_conditions() -> None:
    corpus = normalized_corpus()
    results = results_for(corpus)
    results["rows"].pop()  # type: ignore[union-attr]

    with pytest.raises(MODULE.ProtocolError, match="results are incomplete"):
        MODULE.validate_results(results, corpus)


def test_model_cannot_change_deterministic_gate_status() -> None:
    corpus = normalized_corpus()
    results = results_for(corpus)
    for row in results["rows"]:  # type: ignore[index]
        if (
            row["case_id"] == "case-00"
            and row["condition"] == "deterministic-model"
        ):
            row["deterministic_gate_status"] = "pass"
            break

    with pytest.raises(
        MODULE.ProtocolError,
        match="changed deterministic gate status",
    ):
        MODULE.validate_results(results, corpus)


def test_score_reports_model_increment_without_gate_override() -> None:
    corpus = normalized_corpus()
    validated = MODULE.validate_results(results_for(corpus), corpus)

    scored = MODULE.score(corpus, validated)

    assert scored["conditions"]["source-tests"]["detection_rate"] == 0.0
    assert scored["conditions"]["deterministic"]["detection_rate"] == 1.0
    assert scored["model_increment_over_deterministic"] == {
        "added_detections": 0,
        "lost_detections": 0,
        "same_detection_status": 10,
    }
