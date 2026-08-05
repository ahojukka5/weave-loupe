"""Tests for compiler invocation helpers."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from tests.capability_fixtures import capability_document
from weave_loupe.bounded_process import ProcessLimits
from weave_loupe.weavec import (
    BuildRequest,
    WeavecError,
    build_command,
    normalize_sources,
    resolve_weavec,
    run_build,
)


def _request(tmp_path: Path, source: Path) -> BuildRequest:
    return BuildRequest(
        sources=(source,),
        executable=tmp_path / "program",
        wir=tmp_path / "program.wir",
        llvm=tmp_path / "program.ll",
        optimized_llvm=tmp_path / "program.optimized.ll",
        assembly=tmp_path / "program.s",
        disassembly=tmp_path / "program.disasm",
        optimization_record=tmp_path / "program.opt.yaml",
        diagnostics=tmp_path / "diagnostics.json",
        trace=tmp_path / "trace.json",
        build_manifest=tmp_path / "build.json",
    )


def _limits(*, timeout: float = 2.0, output: int = 4096) -> ProcessLimits:
    return ProcessLimits(
        timeout_seconds=timeout,
        output_bytes=output,
        excerpt_bytes=min(output, 1024),
        cpu_seconds=max(2.0, timeout + 1.0),
        address_space_bytes=1024 * 1024 * 1024,
        file_size_bytes=16 * 1024 * 1024,
        process_count=32,
    )


def _script(tmp_path: Path, body: str) -> Path:
    script = tmp_path / "weavec-hostile"
    registry = repr(capability_document())
    script.write_text(
        "#!/usr/bin/env python3\n"
        "import json\n"
        "import sys\n"
        f"CAPABILITIES = {registry}\n"
        "if sys.argv[1:] == ['capabilities', '--json']:\n"
        "    print(json.dumps(CAPABILITIES, sort_keys=True, separators=(',', ':')))\n"
        "    raise SystemExit(0)\n"
        f"{body}\n",
        encoding="utf-8",
    )
    script.chmod(0o755)
    return script


def test_resolve_weavec_explicit(fake_weavec: Path) -> None:
    assert resolve_weavec(fake_weavec) == fake_weavec.resolve()


def test_resolve_weavec_env(fake_weavec: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WEAVEC_BIN", str(fake_weavec))
    assert resolve_weavec() == fake_weavec.resolve()


def test_resolve_weavec_path(
    fake_weavec: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("WEAVEC_BIN", raising=False)
    with patch("weave_loupe.weavec.shutil.which", return_value=str(fake_weavec)):
        assert resolve_weavec() == fake_weavec.resolve()


def test_resolve_weavec_missing(tmp_path: Path) -> None:
    with pytest.raises(WeavecError, match="binary not found"):
        resolve_weavec(tmp_path / "missing")


def test_normalize_sources_requires_input() -> None:
    with pytest.raises(WeavecError, match="at least one"):
        normalize_sources([])


def test_normalize_sources_preserves_order(tmp_path: Path) -> None:
    left = tmp_path / "a.weave"
    right = tmp_path / "b.weave"
    left.write_text("a")
    right.write_text("b")
    assert normalize_sources([right, left]) == (right.resolve(), left.resolve())


def test_build_command_uses_public_artifact_flags(
    tmp_path: Path, source_file: Path, fake_weavec: Path
) -> None:
    command = build_command(fake_weavec, _request(tmp_path, source_file))
    assert command[1] == "build"
    assert "--emit-wir" in command
    assert "--emit-llvm" in command
    assert "--emit-optimized-llvm" in command
    assert "--emit-assembly" in command
    assert "--emit-disassembly" in command
    assert "--optimization-record" in command
    assert "-O3" in command
    assert "--native" in command
    assert "--diagnostics-json" in command
    assert "--trace-json" in command
    assert "--manifest-json" in command
    assert command[-1] == "--llvm-provenance"


def test_run_build_retains_outputs_and_execution_evidence(
    tmp_path: Path, source_file: Path, fake_weavec: Path
) -> None:
    request = _request(tmp_path, source_file)
    result = run_build(request, weavec=fake_weavec)
    assert result.returncode == 0
    assert result.stdout == "compiled\n"
    assert result.execution.succeeded is True
    assert result.execution.stdout.observed_bytes == len(b"compiled\n")
    assert len(result.execution.stdout.sha256) == 64
    assert result.execution.limits.timeout_seconds == 120.0
    assert result.capabilities.identity["registry_format"] == "weavec-capabilities-v1"
    assert result.capabilities.identity["compiler_version"] == "0.1.0"
    assert result.capabilities.identity["capture_profile"]["command"] == "build"
    assert request.wir.is_file()
    assert request.llvm.is_file()
    assert request.optimized_llvm.is_file()
    assert request.assembly.is_file()
    assert request.disassembly.is_file()
    assert request.optimization_record.is_file()


def test_run_build_rejects_incompatible_compiler_before_build(
    tmp_path: Path,
    source_file: Path,
) -> None:
    compiler = tmp_path / "incompatible-weavec"
    compiler.write_text("#!/bin/sh\nexit 9\n", encoding="utf-8")
    compiler.chmod(0o755)

    with pytest.raises(WeavecError, match="WEAVEC_CAPABILITIES_FAILED"):
        run_build(_request(tmp_path, source_file), weavec=compiler)

    assert not (tmp_path / "program").exists()


def test_run_build_terminates_infinite_compiler(
    tmp_path: Path, source_file: Path
) -> None:
    compiler = _script(tmp_path, "while True:\n    pass")

    result = run_build(
        _request(tmp_path, source_file),
        weavec=compiler,
        limits=_limits(timeout=0.2),
    )

    assert result.returncode == 124
    assert result.execution.termination_reason == "timed_out"
    assert result.execution.exit_code is None


def test_run_build_terminates_compiler_output_overflow(
    tmp_path: Path, source_file: Path
) -> None:
    compiler = _script(
        tmp_path,
        "import time\n"
        "sys.stdout.buffer.write(b'x' * 100000)\n"
        "sys.stdout.buffer.flush()\n"
        "time.sleep(10)",
    )

    result = run_build(
        _request(tmp_path, source_file),
        weavec=compiler,
        limits=_limits(output=1024),
    )

    assert result.returncode == 125
    assert result.execution.termination_reason == "output_limit"
    assert result.execution.overflow_streams == ("stdout",)
    assert result.execution.stdout.observed_bytes > 1024
