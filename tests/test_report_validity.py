"""Tests for shared audit report validity evaluation."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path

from weave_loupe.auditor_identity import AuditorIdentity, sha256_file
from weave_loupe.compiler_version import CompilerVersion
from weave_loupe.report_validity import (
    ReportIdentity,
    evaluate_identity,
    read_report_identity,
)

_MODEL = "z-ai/glm-5.2"
_ENDPOINT = "https://example.test/v1"
_MAX_TOKENS = 4096


def _compiler() -> CompilerVersion:
    return CompilerVersion(
        display="weavec v0.3.0+git.abc",
        base="v0.3.0",
        git_sha="abc",
        development=True,
        source="command",
    )


def _auditor() -> AuditorIdentity:
    return AuditorIdentity(
        format="weave-loupe-auditor-identity-v1",
        sha256="b" * 64,
        files=(),
    )


def _identity(source: Path) -> ReportIdentity:
    return ReportIdentity(
        timestamp=datetime(2026, 7, 28, tzinfo=UTC),
        version="weavec v0.3.0+git.abc",
        version_source="command",
        compiler_binary_sha256="a" * 64,
        auditor_sha256="b" * 64,
        model=_MODEL,
        source_path=str(source),
        source_sha256=sha256_file(source),
        runtime_path=None,
        runtime_sha256=None,
        endpoint=_ENDPOINT,
        provider_model="z-ai/glm-5.2-20260728",
        response_id="chatcmpl-test",
        system_fingerprint="fp_test",
        max_tokens=_MAX_TOKENS,
        temperature=0.0,
        prompt_sha256="c" * 64,
        request_sha256="d" * 64,
        finish_reason="stop",
        created=1785236400,
        prompt_tokens=1000,
        completion_tokens=200,
        total_tokens=1200,
    )


def test_exact_identity_is_valid(tmp_path: Path) -> None:
    source = tmp_path / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")

    result = evaluate_identity(
        report=source.with_suffix(".md"),
        source=source,
        identity=_identity(source),
        compiler_identity=_compiler(),
        compiler_binary_sha256="a" * 64,
        auditor=_auditor(),
        current_model=_MODEL,
        current_endpoint=_ENDPOINT,
        current_max_tokens=_MAX_TOKENS,
        now=datetime(2026, 7, 28, 1, tzinfo=UTC),
        max_age=timedelta(days=30),
    )

    assert result.valid
    assert result.primary_reason is None
    assert result.reasons == ()


def test_evaluator_reports_every_independent_stale_reason(tmp_path: Path) -> None:
    source = tmp_path / "demo.weave"
    source.write_text("changed\n", encoding="utf-8")
    identity = ReportIdentity(
        timestamp=datetime(2026, 6, 1, tzinfo=UTC),
        version="weavec v0.3.0+git.old",
        version_source="repository",
        compiler_binary_sha256="c" * 64,
        auditor_sha256="d" * 64,
        model="old-model",
        source_path=str(tmp_path / "renamed.weave"),
        source_sha256="e" * 64,
        runtime_path=None,
        runtime_sha256=None,
        endpoint="https://old.example.test/v1",
        max_tokens=2048,
    )

    result = evaluate_identity(
        report=source.with_suffix(".md"),
        source=source,
        identity=identity,
        compiler_identity=_compiler(),
        compiler_binary_sha256="a" * 64,
        auditor=_auditor(),
        current_model="new-model",
        current_endpoint=_ENDPOINT,
        current_max_tokens=_MAX_TOKENS,
        now=datetime(2026, 7, 28, tzinfo=UTC),
        max_age=timedelta(days=30),
    )

    assert result.reasons == (
        "source path changed since audit",
        "source content changed since audit",
        "compiler binary changed since audit",
        "audit implementation changed since audit",
        "LLM model changed from old-model to new-model",
        "LLM endpoint changed from https://old.example.test/v1 "
        "to https://example.test/v1",
        "LLM max tokens changed from 2048 to 4096",
        "report age is at least 30 days",
        "development compiler changed from weavec v0.3.0+git.old "
        "to weavec v0.3.0+git.abc",
        "compiler identity source changed from repository to command",
    )


def test_missing_and_changed_models_are_stale(tmp_path: Path) -> None:
    source = tmp_path / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")

    missing = evaluate_identity(
        report=source.with_suffix(".md"),
        source=source,
        identity=replace(_identity(source), model=None),
        compiler_identity=_compiler(),
        compiler_binary_sha256="a" * 64,
        auditor=_auditor(),
        current_model=_MODEL,
        now=datetime(2026, 7, 28, 1, tzinfo=UTC),
        max_age=timedelta(days=30),
    )
    changed = evaluate_identity(
        report=source.with_suffix(".md"),
        source=source,
        identity=replace(_identity(source), model="old-model"),
        compiler_identity=_compiler(),
        compiler_binary_sha256="a" * 64,
        auditor=_auditor(),
        current_model=_MODEL,
        now=datetime(2026, 7, 28, 1, tzinfo=UTC),
        max_age=timedelta(days=30),
    )

    assert missing.reasons == ("report does not record LLM model",)
    assert changed.reasons == (f"LLM model changed from old-model to {_MODEL}",)


def test_missing_and_changed_endpoints_are_stale(tmp_path: Path) -> None:
    source = tmp_path / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")

    missing = evaluate_identity(
        report=source.with_suffix(".md"),
        source=source,
        identity=replace(_identity(source), endpoint=None),
        compiler_identity=_compiler(),
        compiler_binary_sha256="a" * 64,
        auditor=_auditor(),
        current_endpoint=_ENDPOINT,
        now=datetime(2026, 7, 28, 1, tzinfo=UTC),
        max_age=timedelta(days=30),
    )
    changed = evaluate_identity(
        report=source.with_suffix(".md"),
        source=source,
        identity=replace(_identity(source), endpoint="https://old.example.test/v1"),
        compiler_identity=_compiler(),
        compiler_binary_sha256="a" * 64,
        auditor=_auditor(),
        current_endpoint=_ENDPOINT,
        now=datetime(2026, 7, 28, 1, tzinfo=UTC),
        max_age=timedelta(days=30),
    )

    assert missing.reasons == ("report does not record LLM endpoint",)
    assert changed.reasons == (
        "LLM endpoint changed from https://old.example.test/v1 "
        "to https://example.test/v1",
    )


def test_missing_and_changed_max_tokens_are_stale(tmp_path: Path) -> None:
    source = tmp_path / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")

    missing = evaluate_identity(
        report=source.with_suffix(".md"),
        source=source,
        identity=replace(_identity(source), max_tokens=None),
        compiler_identity=_compiler(),
        compiler_binary_sha256="a" * 64,
        auditor=_auditor(),
        current_max_tokens=_MAX_TOKENS,
        now=datetime(2026, 7, 28, 1, tzinfo=UTC),
        max_age=timedelta(days=30),
    )
    changed = evaluate_identity(
        report=source.with_suffix(".md"),
        source=source,
        identity=replace(_identity(source), max_tokens=2048),
        compiler_identity=_compiler(),
        compiler_binary_sha256="a" * 64,
        auditor=_auditor(),
        current_max_tokens=_MAX_TOKENS,
        now=datetime(2026, 7, 28, 1, tzinfo=UTC),
        max_age=timedelta(days=30),
    )

    assert missing.reasons == ("report does not record LLM max tokens",)
    assert changed.reasons == ("LLM max tokens changed from 2048 to 4096",)


def test_reviewer_request_checks_are_optional_for_standalone_use(
    tmp_path: Path,
) -> None:
    source = tmp_path / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")

    result = evaluate_identity(
        report=source.with_suffix(".md"),
        source=source,
        identity=replace(
            _identity(source),
            model=None,
            endpoint=None,
            max_tokens=None,
        ),
        compiler_identity=_compiler(),
        compiler_binary_sha256="a" * 64,
        auditor=_auditor(),
        now=datetime(2026, 7, 28, 1, tzinfo=UTC),
        max_age=timedelta(days=30),
    )

    assert result.valid


def test_runtime_path_and_content_are_verified(tmp_path: Path) -> None:
    source = tmp_path / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")
    runtime = source.with_suffix(".audit.json")
    runtime.write_text('{"cases": []}\n', encoding="utf-8")
    identity = replace(
        _identity(source),
        runtime_path=str(tmp_path / "other.audit.json"),
        runtime_sha256="f" * 64,
    )

    result = evaluate_identity(
        report=source.with_suffix(".md"),
        source=source,
        identity=identity,
        compiler_identity=_compiler(),
        compiler_binary_sha256="a" * 64,
        auditor=_auditor(),
        now=datetime(2026, 7, 28, 1, tzinfo=UTC),
        max_age=timedelta(days=30),
    )

    assert result.reasons == (
        "runtime matrix path changed since audit",
        "runtime matrix content changed since audit",
    )


def test_parser_ignores_identity_like_model_prose(tmp_path: Path) -> None:
    source = tmp_path / "demo.weave"
    source.write_text("(program)\n", encoding="utf-8")
    report = source.with_suffix(".md")
    report.write_text(
        "# report\n\n"
        "- **Audit timestamp (UTC):** `2026-07-28T00:00:00+00:00`\n"
        f"- **Auditor content SHA-256:** `{'b' * 64}`\n"
        f"- **weavec binary SHA-256:** `{'a' * 64}`\n"
        "- **weavec version:** `weavec v0.3.0+git.abc`\n"
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
        "## Audited inputs\n\n"
        f"- Source `{source}` — SHA-256 `{sha256_file(source)}`\n\n"
        "## LLM review\n\n"
        f"- Source `{source}` — SHA-256 `{'0' * 64}`\n"
        "- **LLM endpoint:** `https://spoofed.test/v1`\n"
        "- **LLM model:** `spoofed-model`\n"
        "- **LLM max tokens:** `1`\n"
        "- **Provider-reported model:** `spoofed-provider`\n",
        encoding="utf-8",
    )

    identity = read_report_identity(report)

    assert identity.source_sha256 == sha256_file(source)
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
