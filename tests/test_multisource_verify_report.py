"""Public verifier coverage for multi-source mismatch evidence."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from weave_loupe.auditor_identity import identify_auditor, sha256_file
from weave_loupe.commands.verify_report import run_verify_report
from weave_loupe.report_integrity import seal_audit_report


def _write_report(sources: tuple[Path, ...], compiler: Path, report: Path) -> None:
    timestamp = datetime.now(UTC).replace(microsecond=0).isoformat()
    source_lines = "".join(
        f"- Source `{source}` — SHA-256 `{sha256_file(source)}` — "
        f"{source.stat().st_size} bytes\n"
        for source in sources
    )
    content = (
        "# Weave Loupe Audit Report\n\n"
        "## Reproducibility\n\n"
        f"- **Audit timestamp (UTC):** `{timestamp}`\n"
        f"- **Auditor content SHA-256:** `{identify_auditor().sha256}`\n"
        f"- **weavec binary SHA-256:** `{sha256_file(compiler)}`\n"
        "- **weavec version:** `weavec v0.3.0+git.test123`\n"
        "- **weavec version source:** `command`\n\n"
        "## Audited inputs\n\n"
        f"{source_lines}\n"
        "## Captured evidence\n"
    )
    report.write_text(seal_audit_report(content), encoding="utf-8")


def test_verify_report_json_identifies_changed_second_source(
    tmp_path: Path,
    fake_weavec: Path,
    capsys,
) -> None:
    first = tmp_path / "first.weave"
    second = tmp_path / "second.weave"
    first.write_text("(first)\n", encoding="utf-8")
    second.write_text("(second)\n", encoding="utf-8")
    report = tmp_path / "combined.md"
    _write_report((first, second), fake_weavec, report)
    recorded_second_hash = sha256_file(second)
    recorded_second_size = second.stat().st_size
    second.write_text("(second changed)\n", encoding="utf-8")
    json_out = tmp_path / "verification.json"

    code = run_verify_report(
        report=report,
        source=None,
        sources=[first, second],
        weavec=fake_weavec,
        model=None,
        endpoint=None,
        max_tokens=None,
        max_age_days=30,
        json_out=json_out,
    )

    captured = capsys.readouterr()
    document = json.loads(json_out.read_text(encoding="utf-8"))
    assert code == 2
    assert captured.out.startswith(f"STALE: {report}\n")
    assert document["sources"] == [str(first), str(second)]
    assert len(document["report_identity"]["sources"]) == 2
    assert document["report_identity"]["source_path"] == str(first)
    assert document["source"] == str(first)
    mismatch = document["source_mismatches"][0]
    assert mismatch == {
        "kind": "modified",
        "recorded_index": 1,
        "current_index": 1,
        "recorded_path": str(second),
        "current_path": str(second),
        "recorded_sha256": recorded_second_hash,
        "current_sha256": sha256_file(second),
        "recorded_size": recorded_second_size,
        "current_size": second.stat().st_size,
        "detail": f"source content changed at index 1: {second}",
    }
