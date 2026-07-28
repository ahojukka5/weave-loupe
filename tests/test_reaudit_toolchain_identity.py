"""Tests for compiler, auditor, and reviewer request revalidation."""

from __future__ import annotations

import importlib.util
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import ModuleType

from weave_loupe.auditor_identity import AuditorIdentity, sha256_file
from weave_loupe.compiler_version import CompilerVersion

_MODEL = "z-ai/glm-5.2"
_ENDPOINT = "https://example.test/v1"
_MAX_TOKENS = 4096


def _load_script() -> ModuleType:
    path = Path(__file__).parents[1] / "scripts" / "reaudit_stale.py"
    spec = importlib.util.spec_from_file_location("reaudit_toolchain_identity", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _compiler() -> CompilerVersion:
    return CompilerVersion(
        display="weavec v0.3.0",
        base="v0.3.0",
        git_sha=None,
        development=False,
        source="command",
    )


def _auditor(digest: str = "b" * 64) -> AuditorIdentity:
    return AuditorIdentity(
        format="weave-loupe-auditor-identity-v1",
        sha256=digest,
        files=(),
    )


def _report_identity(
    module: ModuleType,
    source: Path,
    *,
    compiler_sha256: str | None = "a" * 64,
    auditor_sha256: str | None = "b" * 64,
    model: str | None = _MODEL,
    endpoint: str | None = _ENDPOINT,
    max_tokens: int | None = _MAX_TOKENS,
) -> object:
    return module.ReportIdentity(
        timestamp=datetime(2026, 7, 28, tzinfo=UTC),
        version="weavec v0.3.0",
        version_source="command",
        compiler_binary_sha256=compiler_sha256,
        auditor_sha256=auditor_sha256,
        model=model,
        source_path=str(source),
        source_sha256=sha256_file(source),
        runtime_path=None,
        runtime_sha256=None,
        endpoint=endpoint,
        max_tokens=max_tokens,
    )


def _reason(
    module: ModuleType,
    source: Path,
    report_identity: object,
    *,
    compiler_sha256: str = "a" * 64,
    auditor: AuditorIdentity | None = None,
    current_model: str | None = _MODEL,
    current_endpoint: str | None = _ENDPOINT,
    current_max_tokens: int | None = _MAX_TOKENS,
) -> str | None:
    return module._reaudit_reason(
        source=source,
        report_identity=report_identity,
        identity=_compiler(),
        compiler_binary_sha256=compiler_sha256,
        auditor=auditor or _auditor(),
        current_model=current_model,
        current_endpoint=current_endpoint,
        current_max_tokens=current_max_tokens,
        now=datetime(2026, 7, 28, 1, tzinfo=UTC),
        max_age=timedelta(days=30),
        force=False,
    )


def test_exact_toolchain_identity_keeps_fresh_report_valid(tmp_path: Path) -> None:
    module = _load_script()
    source = tmp_path / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")

    assert _reason(module, source, _report_identity(module, source)) is None


def test_missing_compiler_binary_hash_requires_reaudit(tmp_path: Path) -> None:
    module = _load_script()
    source = tmp_path / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")

    reason = _reason(
        module,
        source,
        _report_identity(module, source, compiler_sha256=None),
    )

    assert reason == "report does not record compiler binary hash"


def test_changed_compiler_binary_requires_reaudit(tmp_path: Path) -> None:
    module = _load_script()
    source = tmp_path / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")

    reason = _reason(
        module,
        source,
        _report_identity(module, source),
        compiler_sha256="c" * 64,
    )

    assert reason == "compiler binary changed since audit"


def test_missing_auditor_fingerprint_requires_reaudit(tmp_path: Path) -> None:
    module = _load_script()
    source = tmp_path / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")

    reason = _reason(
        module,
        source,
        _report_identity(module, source, auditor_sha256=None),
    )

    assert reason == "report does not record auditor fingerprint"


def test_changed_auditor_fingerprint_requires_reaudit(tmp_path: Path) -> None:
    module = _load_script()
    source = tmp_path / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")

    reason = _reason(
        module,
        source,
        _report_identity(module, source),
        auditor=_auditor("d" * 64),
    )

    assert reason == "audit implementation changed since audit"


def test_missing_model_requires_reaudit(tmp_path: Path) -> None:
    module = _load_script()
    source = tmp_path / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")

    reason = _reason(module, source, _report_identity(module, source, model=None))

    assert reason == "report does not record LLM model"


def test_changed_model_requires_reaudit(tmp_path: Path) -> None:
    module = _load_script()
    source = tmp_path / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")

    reason = _reason(
        module,
        source,
        _report_identity(module, source, model="old-model"),
    )

    assert reason == f"LLM model changed from old-model to {_MODEL}"


def test_missing_endpoint_requires_reaudit(tmp_path: Path) -> None:
    module = _load_script()
    source = tmp_path / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")

    reason = _reason(module, source, _report_identity(module, source, endpoint=None))

    assert reason == "report does not record LLM endpoint"


def test_changed_endpoint_requires_reaudit(tmp_path: Path) -> None:
    module = _load_script()
    source = tmp_path / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")

    reason = _reason(
        module,
        source,
        _report_identity(
            module,
            source,
            endpoint="https://old.example.test/v1",
        ),
    )

    assert reason == (
        "LLM endpoint changed from https://old.example.test/v1 "
        "to https://example.test/v1"
    )


def test_missing_max_tokens_requires_reaudit(tmp_path: Path) -> None:
    module = _load_script()
    source = tmp_path / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")

    reason = _reason(module, source, _report_identity(module, source, max_tokens=None))

    assert reason == "report does not record LLM max tokens"


def test_changed_max_tokens_requires_reaudit(tmp_path: Path) -> None:
    module = _load_script()
    source = tmp_path / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")

    reason = _reason(
        module,
        source,
        _report_identity(module, source, max_tokens=2048),
    )

    assert reason == "LLM max tokens changed from 2048 to 4096"


def test_report_parser_reads_toolchain_and_request_identity(tmp_path: Path) -> None:
    module = _load_script()
    report = tmp_path / "demo.md"
    report.write_text(
        "# report\n\n"
        "- **Audit timestamp (UTC):** `2026-07-28T00:00:00+00:00`\n"
        f"- **Auditor content SHA-256:** `{'b' * 64}`\n"
        f"- **weavec binary SHA-256:** `{'a' * 64}`\n"
        "- **weavec version:** `weavec v0.3.0`\n"
        "- **weavec version source:** `command`\n"
        f"- **LLM endpoint:** `{_ENDPOINT}`\n"
        f"- **LLM model:** `{_MODEL}`\n"
        f"- **LLM max tokens:** `{_MAX_TOKENS}`\n"
        "- **LLM temperature:** `0.0`\n"
        f"- **LLM prompt SHA-256:** `{'c' * 64}`\n"
        f"- **LLM request SHA-256:** `{'d' * 64}`\n"
        "- **Provider-reported model:** `z-ai/glm-5.2-20260728`\n"
        "- **Provider response ID:** `chatcmpl-test`\n"
        "- **Provider system fingerprint:** `fp_test`\n"
        "- **Provider finish reason:** `stop`\n"
        "- **Provider created (Unix):** `1785236400`\n"
        "- **Provider prompt tokens:** `1000`\n"
        "- **Provider completion tokens:** `200`\n"
        "- **Provider total tokens:** `1200`\n\n"
        "## Audited inputs\n",
        encoding="utf-8",
    )

    identity = module._read_report_identity(report)

    assert identity.compiler_binary_sha256 == "a" * 64
    assert identity.auditor_sha256 == "b" * 64
    assert identity.endpoint == _ENDPOINT
    assert identity.model == _MODEL
    assert identity.max_tokens == _MAX_TOKENS
    assert identity.temperature == 0.0
    assert identity.prompt_sha256 == "c" * 64
    assert identity.request_sha256 == "d" * 64
    assert identity.provider_model == "z-ai/glm-5.2-20260728"
    assert identity.response_id == "chatcmpl-test"
    assert identity.system_fingerprint == "fp_test"
    assert identity.finish_reason == "stop"
    assert identity.created == 1785236400
    assert identity.prompt_tokens == 1000
    assert identity.completion_tokens == 200
    assert identity.total_tokens == 1200
