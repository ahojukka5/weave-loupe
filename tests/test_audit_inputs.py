"""Tests for stable audited source and runtime input identities."""

from __future__ import annotations

from weave_loupe.audit_result import (
    AuditVerdict,
    _runtime_input_metadata,
    render_audit_report,
)


def _metadata() -> dict[str, object]:
    return {
        "timestamp_utc": "2026-07-28T00:00:00+00:00",
        "validity": {
            "revalidate_after_utc": "2026-08-27T00:00:00+00:00",
            "max_age_days": 30,
        },
        "model": "model",
        "source_repository": {"sha": "source-commit", "state": "clean"},
        "loupe_repository": {"sha": "loupe-commit"},
        "weavec": {
            "sha256": "binary-hash",
            "version": "weavec v0.3.0+git.abc",
            "development": True,
            "version_source": "command",
            "repository": {"sha": "compiler-commit"},
        },
        "machine": {},
        "bundle": {"artifacts": {}},
        "github": {},
        "sources": [
            {
                "path": "docs/audit/demo.weave",
                "sha256": "a" * 64,
            }
        ],
        "runtime_input": {
            "path": "docs/audit/demo.audit.json",
            "sha256": "b" * 64,
        },
    }


def test_report_labels_source_and_runtime_matrix_hashes() -> None:
    report = render_audit_report(
        verdict=AuditVerdict(
            status="OK",
            code=None,
            reason=None,
            body="No defect.",
        ),
        metadata=_metadata(),
        model_response="OK\nNo defect.",
    )

    assert f"- Source `docs/audit/demo.weave` — SHA-256 `{'a' * 64}`" in report
    assert (
        f"- Runtime matrix `docs/audit/demo.audit.json` — SHA-256 `{'b' * 64}`"
        in report
    )


def test_runtime_input_metadata_uses_executed_sidecar_hash() -> None:
    metadata = _runtime_input_metadata(
        {
            "format": "weave-loupe-runtime-matrix-v1",
            "configured": True,
            "sidecar": "docs/audit/demo.audit.json",
            "sidecar_sha256": "c" * 64,
            "case_count": 4,
        }
    )

    assert metadata == {
        "format": "weave-loupe-runtime-matrix-v1",
        "path": "docs/audit/demo.audit.json",
        "sha256": "c" * 64,
        "case_count": 4,
    }


def test_runtime_input_metadata_omits_unconfigured_matrix() -> None:
    assert _runtime_input_metadata({"configured": False}) is None
