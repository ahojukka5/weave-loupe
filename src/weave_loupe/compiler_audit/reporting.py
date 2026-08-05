"""Assembly and sealing of compiler audit reports."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from .model import (
    COMPILER_AUDIT_FORMAT,
    COMPILER_AUDIT_SEAL_FORMAT,
    CompilerAuditError,
    CompilerAuditPolicy,
    CompilerEvidence,
    ReviewCallback,
)


def build_compiler_audit_report(
    *,
    sources: Sequence[Path],
    baseline: CompilerEvidence,
    candidate: CompilerEvidence,
    policy: CompilerAuditPolicy,
    comparison: Mapping[str, Any],
    failures: list[dict[str, Any]],
    reviewer: ReviewCallback | None,
) -> dict[str, Any]:
    """Assemble and seal a report from already acquired and compared evidence."""
    infrastructure = any(
        failure["category"] == "infrastructure" for failure in failures
    )
    report: dict[str, Any] = {
        "format": COMPILER_AUDIT_FORMAT,
        "status": _status(failures=failures, infrastructure=infrastructure),
        "passed": not failures,
        "sources": source_identities(sources),
        "policy": policy.as_dict(),
        "baseline": dict(baseline.result),
        "candidate": dict(candidate.result),
        "comparison": dict(comparison),
        "failures": failures,
        "review": None,
    }
    if reviewer is not None:
        review = reviewer(report)
        if not isinstance(review, Mapping):
            raise CompilerAuditError("compiler audit reviewer must return a mapping")
        report["review"] = dict(review)
    return seal_compiler_audit(report)


def seal_compiler_audit(document: Mapping[str, Any]) -> dict[str, Any]:
    """Attach a canonical SHA-256 seal without hashing the seal itself."""
    unsealed = dict(document)
    unsealed.pop("seal", None)
    canonical = json.dumps(
        unsealed,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return {
        **unsealed,
        "seal": {
            "format": COMPILER_AUDIT_SEAL_FORMAT,
            "sha256": hashlib.sha256(canonical).hexdigest(),
        },
    }


def source_identities(sources: Sequence[Path]) -> list[dict[str, Any]]:
    """Return deterministic identities for the ordered audit source inputs."""
    result: list[dict[str, Any]] = []
    for index, source in enumerate(sources):
        data = source.expanduser().resolve().read_bytes()
        result.append(
            {
                "index": index,
                "path": str(source),
                "sha256": hashlib.sha256(data).hexdigest(),
                "size": len(data),
            }
        )
    return result


def _status(*, failures: list[dict[str, Any]], infrastructure: bool) -> str:
    if infrastructure:
        return "infrastructure-failure"
    return "regression" if failures else "pass"
