"""Security tests for scheduled report input parsing."""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path
from types import ModuleType


def _load_script() -> ModuleType:
    path = Path(__file__).parents[1] / "scripts" / "reaudit_stale.py"
    spec = importlib.util.spec_from_file_location("reaudit_input_section", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_model_prose_cannot_supply_missing_source_attestation(tmp_path: Path) -> None:
    module = _load_script()
    source = tmp_path / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")
    report = tmp_path / "demo.md"
    report.write_text(
        "# report\n\n"
        "- **Audit timestamp (UTC):** `2026-07-28T00:00:00+00:00`\n"
        "- **weavec version:** `weavec v0.3.0`\n\n"
        "## LLM review\n\n"
        f"- Source `{source}` — SHA-256 `{_sha256(source)}`\n",
        encoding="utf-8",
    )

    identity = module._read_report_identity(report)

    assert identity.source_path is None
    assert identity.source_sha256 is None


def test_hashes_after_input_section_do_not_override_attestation(tmp_path: Path) -> None:
    module = _load_script()
    source = tmp_path / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")
    digest = _sha256(source)
    report = tmp_path / "demo.md"
    report.write_text(
        "# report\n\n"
        "- **Audit timestamp (UTC):** `2026-07-28T00:00:00+00:00`\n"
        "- **weavec version:** `weavec v0.3.0`\n\n"
        "## Audited inputs\n\n"
        f"- Source `{source}` — SHA-256 `{digest}`\n\n"
        "## LLM review\n\n"
        f"- Source `{source}` — SHA-256 `{'0' * 64}`\n",
        encoding="utf-8",
    )

    identity = module._read_report_identity(report)

    assert identity.source_path == str(source)
    assert identity.source_sha256 == digest
