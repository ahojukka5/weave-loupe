#!/usr/bin/env python3
"""Validate and score the frozen compiler-evidence regression study."""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
from collections import Counter
from pathlib import Path
from typing import Any

CORPUS_SCHEMA = "weave-loupe-regression-corpus-v1"
RESULT_SCHEMA = "weave-loupe-regression-results-v1"
SCORE_SCHEMA = "weave-loupe-regression-score-v1"
CONDITIONS = (
    "source-tests",
    "source-ir",
    "full-evidence",
    "deterministic",
    "deterministic-model",
)
STAGES = {
    "formatter",
    "frontend",
    "wir",
    "llvm",
    "optimization",
    "native",
    "protocol",
    "toolchain",
}
GATE_STATUSES = {"pass", "fail", "unavailable"}


class ProtocolError(ValueError):
    """Raised when research evidence violates the frozen protocol."""


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProtocolError(f"cannot load JSON from {path}: {exc}") from exc


def _object(value: Any, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ProtocolError(f"{context} must be an object")
    return value


def _text(value: Any, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProtocolError(f"{context} must be a non-empty string")
    return value


def _nonnegative_int(
    value: Any,
    context: str,
    *,
    allow_none: bool = False,
) -> int | None:
    if allow_none and value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ProtocolError(f"{context} must be a non-negative integer")
    return value


def _nonnegative_number(value: Any, context: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ProtocolError(f"{context} must be a non-negative number")
    result = float(value)
    if result < 0:
        raise ProtocolError(f"{context} must be a non-negative number")
    return result


def _command(value: Any, context: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ProtocolError(f"{context} must be a non-empty argument list")
    return [_text(item, f"{context}[{index}]") for index, item in enumerate(value)]


def canonical_corpus_hash(corpus: dict[str, Any]) -> str:
    payload = dict(corpus)
    payload.pop("corpus_sha256", None)
    payload.pop("corpus_summary", None)
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_corpus(value: Any, *, require_frozen: bool = False) -> dict[str, Any]:
    corpus = _object(value, "corpus")
    if corpus.get("schema") != CORPUS_SCHEMA:
        raise ProtocolError(f"corpus schema must be {CORPUS_SCHEMA}")
    status = corpus.get("status")
    if status not in {"draft", "frozen"}:
        raise ProtocolError("corpus status must be draft or frozen")
    if require_frozen and status != "frozen":
        raise ProtocolError("experiment scoring requires a frozen corpus")

    loupe = _object(corpus.get("loupe"), "corpus.loupe")
    compiler = _object(corpus.get("compiler"), "corpus.compiler")
    _text(loupe.get("repository"), "corpus.loupe.repository")
    loupe_revision = _text(loupe.get("revision"), "corpus.loupe.revision")
    _text(compiler.get("repository"), "corpus.compiler.repository")
    if status == "frozen" and len(loupe_revision) < 12:
        raise ProtocolError("frozen Loupe revision must be immutable")

    review = _object(corpus.get("model_review"), "corpus.model_review")
    for field in ("provider", "model", "configuration_id", "prompt_id"):
        _text(review.get(field), f"corpus.model_review.{field}")

    if corpus.get("conditions") != list(CONDITIONS):
        raise ProtocolError(
            f"corpus conditions must be exactly {list(CONDITIONS)}"
        )

    cases = corpus.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ProtocolError("corpus.cases must be a non-empty list")

    ids: set[str] = set()
    families: Counter[str] = Counter()
    normalized: list[dict[str, Any]] = []
    for index, raw_case in enumerate(cases):
        case = _object(raw_case, f"corpus.cases[{index}]")
        case_id = _text(case.get("id"), f"corpus.cases[{index}].id")
        if case_id in ids:
            raise ProtocolError(f"duplicate case id: {case_id}")
        ids.add(case_id)

        family = _text(case.get("family"), f"case {case_id}.family")
        families[family] += 1
        bad_revision = _text(
            case.get("bad_revision"), f"case {case_id}.bad_revision"
        )
        good_revision = _text(
            case.get("good_revision"), f"case {case_id}.good_revision"
        )
        if bad_revision == good_revision:
            raise ProtocolError(f"case {case_id}: good and bad revisions are equal")
        if status == "frozen" and (
            len(bad_revision) < 12 or len(good_revision) < 12
        ):
            raise ProtocolError(
                f"case {case_id}: frozen revisions must be immutable"
            )

        stage = case.get("expected_stage")
        if stage not in STAGES:
            raise ProtocolError(
                f"case {case_id}: expected_stage must be one of {sorted(STAGES)}"
            )
        _text(
            case.get("failure_mechanism"),
            f"case {case_id}.failure_mechanism",
        )
        oracle = _object(case.get("oracle"), f"case {case_id}.oracle")
        _command(oracle.get("command"), f"case {case_id}.oracle.command")
        tests = case.get("relevant_tests")
        if not isinstance(tests, list) or not tests:
            raise ProtocolError(
                f"case {case_id}: relevant_tests must be a non-empty list"
            )
        for test_index, test in enumerate(tests):
            _text(test, f"case {case_id}.relevant_tests[{test_index}]")
        normalized.append(case)

    if status == "frozen" and len(cases) < 10:
        raise ProtocolError(
            "frozen first corpus must contain at least 10 qualified real cases"
        )
    if status == "frozen" and len(families) < 4:
        raise ProtocolError(
            "frozen first corpus must span at least four failure families"
        )

    return {
        **corpus,
        "cases": normalized,
        "corpus_summary": {
            "case_count": len(cases),
            "family_count": len(families),
            "family_counts": dict(sorted(families.items())),
        },
    }


def load_corpus(path: Path, *, require_frozen: bool = False) -> dict[str, Any]:
    corpus = validate_corpus(_read_json(path), require_frozen=require_frozen)
    expected = canonical_corpus_hash(corpus)
    declared = corpus.get("corpus_sha256")
    if corpus["status"] == "frozen" and declared != expected:
        raise ProtocolError(f"frozen corpus_sha256 mismatch: expected {expected}")
    if corpus["status"] == "draft" and declared not in {None, expected}:
        raise ProtocolError(f"draft corpus_sha256 mismatch: expected {expected}")
    corpus["corpus_sha256"] = expected
    return corpus


def validate_results(value: Any, corpus: dict[str, Any]) -> dict[str, Any]:
    results = _object(value, "results")
    if results.get("schema") != RESULT_SCHEMA:
        raise ProtocolError(f"results schema must be {RESULT_SCHEMA}")
    if results.get("corpus_sha256") != corpus["corpus_sha256"]:
        raise ProtocolError("results corpus_sha256 does not match frozen corpus")

    rows = results.get("rows")
    if not isinstance(rows, list):
        raise ProtocolError("results.rows must be a list")
    case_ids = {case["id"] for case in corpus["cases"]}
    expected = {
        (case_id, condition)
        for case_id in case_ids
        for condition in CONDITIONS
    }
    seen: set[tuple[str, str]] = set()
    normalized: list[dict[str, Any]] = []

    for index, raw_row in enumerate(rows):
        row = _object(raw_row, f"results.rows[{index}]")
        case_id = _text(row.get("case_id"), f"results.rows[{index}].case_id")
        condition = _text(
            row.get("condition"), f"results.rows[{index}].condition"
        )
        key = (case_id, condition)
        if key not in expected:
            raise ProtocolError(f"unexpected case/condition row: {case_id}/{condition}")
        if key in seen:
            raise ProtocolError(f"duplicate case/condition row: {case_id}/{condition}")
        seen.add(key)

        for field in (
            "defect_detected",
            "phase_localized",
            "mechanism_localized",
            "false_positive_on_good",
        ):
            if not isinstance(row.get(field), bool):
                raise ProtocolError(f"{case_id}/{condition}: {field} must be boolean")
        _nonnegative_int(
            row.get("evidence_bytes"), f"{case_id}/{condition}.evidence_bytes"
        )
        for field in ("input_tokens", "output_tokens"):
            _nonnegative_int(
                row.get(field),
                f"{case_id}/{condition}.{field}",
                allow_none=True,
            )
        _nonnegative_number(
            row.get("review_seconds"), f"{case_id}/{condition}.review_seconds"
        )
        gate = row.get("deterministic_gate_status")
        if condition in {"deterministic", "deterministic-model"}:
            if gate not in GATE_STATUSES:
                raise ProtocolError(
                    f"{case_id}/{condition}: deterministic_gate_status must be "
                    f"one of {sorted(GATE_STATUSES)}"
                )
        elif gate is not None:
            raise ProtocolError(
                f"{case_id}/{condition}: deterministic_gate_status must be null"
            )
        normalized.append(row)

    missing = expected - seen
    if missing:
        formatted = ", ".join(
            f"{case}/{condition}" for case, condition in sorted(missing)
        )
        raise ProtocolError(f"results are incomplete: missing {formatted}")

    row_by_key = {(row["case_id"], row["condition"]): row for row in normalized}
    for case_id in sorted(case_ids):
        deterministic = row_by_key[(case_id, "deterministic")]
        model = row_by_key[(case_id, "deterministic-model")]
        if (
            model["deterministic_gate_status"]
            != deterministic["deterministic_gate_status"]
        ):
            raise ProtocolError(
                f"{case_id}: model condition changed deterministic gate status"
            )

    return {**results, "rows": normalized}


def _median(values: list[float]) -> float | None:
    if not values:
        return None
    return float(statistics.median(values))


def _rate(rows: list[dict[str, Any]], field: str) -> float:
    if not rows:
        return 0.0
    return sum(bool(row[field]) for row in rows) / len(rows)


def score(corpus: dict[str, Any], results: dict[str, Any]) -> dict[str, Any]:
    by_condition: dict[str, list[dict[str, Any]]] = {
        condition: [] for condition in CONDITIONS
    }
    for row in results["rows"]:
        by_condition[row["condition"]].append(row)

    summaries: dict[str, Any] = {}
    for condition in CONDITIONS:
        rows = by_condition[condition]
        token_totals = [
            float(row["input_tokens"] + row["output_tokens"])
            for row in rows
            if row["input_tokens"] is not None and row["output_tokens"] is not None
        ]
        summaries[condition] = {
            "case_count": len(rows),
            "detection_rate": _rate(rows, "defect_detected"),
            "phase_localization_rate": _rate(rows, "phase_localized"),
            "mechanism_localization_rate": _rate(rows, "mechanism_localized"),
            "false_positive_rate": _rate(rows, "false_positive_on_good"),
            "median_evidence_bytes": _median(
                [float(row["evidence_bytes"]) for row in rows]
            ),
            "median_model_tokens": _median(token_totals),
            "median_review_seconds": _median(
                [float(row["review_seconds"]) for row in rows]
            ),
        }

    deterministic = {
        row["case_id"]: row for row in by_condition["deterministic"]
    }
    model = {
        row["case_id"]: row for row in by_condition["deterministic-model"]
    }
    added = 0
    lost = 0
    same = 0
    for case_id in sorted(deterministic):
        base_detected = bool(deterministic[case_id]["defect_detected"])
        model_detected = bool(model[case_id]["defect_detected"])
        if model_detected and not base_detected:
            added += 1
        elif base_detected and not model_detected:
            lost += 1
        else:
            same += 1

    return {
        "schema": SCORE_SCHEMA,
        "corpus_sha256": corpus["corpus_sha256"],
        "case_count": len(corpus["cases"]),
        "conditions": summaries,
        "model_increment_over_deterministic": {
            "added_detections": added,
            "lost_detections": lost,
            "same_detection_status": same,
        },
    }


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate-corpus")
    validate_parser.add_argument("corpus", type=Path)
    validate_parser.add_argument("--require-frozen", action="store_true")

    hash_parser = subparsers.add_parser("hash-corpus")
    hash_parser.add_argument("corpus", type=Path)

    score_parser = subparsers.add_parser("score")
    score_parser.add_argument("corpus", type=Path)
    score_parser.add_argument("results", type=Path)
    score_parser.add_argument("--output", required=True, type=Path)

    args = parser.parse_args()
    try:
        if args.command == "validate-corpus":
            corpus = load_corpus(args.corpus, require_frozen=args.require_frozen)
            print(json.dumps(corpus["corpus_summary"], sort_keys=True))
            return 0
        if args.command == "hash-corpus":
            corpus = load_corpus(args.corpus)
            print(corpus["corpus_sha256"])
            return 0
        if args.command == "score":
            corpus = load_corpus(args.corpus, require_frozen=True)
            results = validate_results(_read_json(args.results), corpus)
            _write_json(args.output, score(corpus, results))
            return 0
    except ProtocolError as exc:
        parser.error(str(exc))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
