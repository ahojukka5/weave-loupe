from __future__ import annotations

import json
import stat
from pathlib import Path

import pytest

from tests.capability_fixtures import capability_document_copy
from weave_loupe.compiler_capabilities import (
    CompilerCapabilityError,
    capability_identity_from_document,
    clear_capability_cache,
    load_compiler_capabilities,
    main,
    require_capture_capabilities,
    validate_capability_document,
)


@pytest.fixture(autouse=True)
def clear_registry_cache() -> None:
    clear_capability_cache()


def _write_compiler(
    path: Path,
    document: dict[str, object],
    *,
    calls: Path | None = None,
    exit_code: int = 0,
) -> None:
    call_path = str(calls) if calls is not None else ""
    path.write_text(
        "#!/usr/bin/env python3\n"
        "from pathlib import Path\n"
        "import json\n"
        "import sys\n"
        f"DOCUMENT = {document!r}\n"
        f"CALLS = {call_path!r}\n"
        f"EXIT_CODE = {exit_code}\n"
        "if CALLS:\n"
        "    with Path(CALLS).open('a', encoding='utf-8') as stream:\n"
        "        stream.write(json.dumps(sys.argv[1:]) + '\\n')\n"
        "if sys.argv[1:] == ['capabilities', '--json']:\n"
        "    print(json.dumps(DOCUMENT, sort_keys=True, separators=(',', ':')))\n"
        "    raise SystemExit(EXIT_CODE)\n"
        "raise SystemExit(2)\n",
        encoding="utf-8",
    )
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def test_offline_validation_accepts_additive_fields() -> None:
    document = capability_document_copy()
    document["future"] = {"additive": True}
    document["compiler"]["build_metadata"] = "local"  # type: ignore[index]

    validated = validate_capability_document(document)
    profile = require_capture_capabilities(validated)

    assert validated["future"] == {"additive": True}
    assert profile["format"] == "weave-loupe-capture-profile-v1"
    assert profile["target"]["triple"] == "x86_64-unknown-linux-gnu"
    assert profile["optimization_level"] == "O3"
    assert "llvm_provenance" in profile["outputs"]


def test_offline_validation_rejects_missing_required_protocol() -> None:
    document = capability_document_copy()
    document["protocols"] = [
        item for item in document["protocols"] if item["id"] != "weavec-diagnostics-v1"
    ]

    with pytest.raises(CompilerCapabilityError) as captured:
        validate_capability_document(document)

    assert captured.value.code == "WEAVEC_PROTOCOL_UNSUPPORTED"


def test_capture_requirement_rejects_missing_build_protocol() -> None:
    document = capability_document_copy()
    build = next(item for item in document["commands"] if item["name"] == "build")
    build["protocols"].remove("weavec-compilation-trace-v1")
    validated = validate_capability_document(document)

    with pytest.raises(CompilerCapabilityError) as captured:
        require_capture_capabilities(validated)

    assert captured.value.code == "WEAVEC_PROTOCOL_UNSUPPORTED"


def test_capture_requirement_rejects_unsupported_target_controls() -> None:
    document = capability_document_copy()
    document["targets"]["installed"][0]["optimization_levels"] = ["O0"]
    validated = validate_capability_document(document)

    with pytest.raises(CompilerCapabilityError) as captured:
        require_capture_capabilities(validated)

    assert captured.value.code == "WEAVEC_OPTIMIZATION_UNSUPPORTED"


def test_registry_is_cached_by_exact_binary_hash(tmp_path: Path) -> None:
    compiler = tmp_path / "weavec"
    calls = tmp_path / "calls.jsonl"
    _write_compiler(compiler, capability_document_copy(), calls=calls)

    first = load_compiler_capabilities(compiler)
    second = load_compiler_capabilities(compiler)

    assert first is second
    assert first.identity["compiler_version"] == "0.1.0"
    assert calls.read_text(encoding="utf-8").splitlines() == [
        '["capabilities", "--json"]'
    ]


def test_replacing_binary_invalidates_cached_registry(tmp_path: Path) -> None:
    compiler = tmp_path / "weavec"
    calls = tmp_path / "calls.jsonl"
    _write_compiler(
        compiler,
        capability_document_copy(version="0.1.0"),
        calls=calls,
    )
    first = load_compiler_capabilities(compiler)
    _write_compiler(
        compiler,
        capability_document_copy(version="0.2.0"),
        calls=calls,
    )
    second = load_compiler_capabilities(compiler)

    assert first.identity["compiler_sha256"] != second.identity["compiler_sha256"]
    assert first.identity["compiler_version"] == "0.1.0"
    assert second.identity["compiler_version"] == "0.2.0"
    assert len(calls.read_text(encoding="utf-8").splitlines()) == 2


def test_nonzero_capability_command_fails_before_build(tmp_path: Path) -> None:
    compiler = tmp_path / "weavec"
    _write_compiler(compiler, capability_document_copy(), exit_code=7)

    with pytest.raises(CompilerCapabilityError) as captured:
        load_compiler_capabilities(compiler)

    assert captured.value.code == "WEAVEC_CAPABILITIES_FAILED"


def test_retained_document_identity_is_offline_and_path_free() -> None:
    document = capability_document_copy()
    raw = (json.dumps(document, sort_keys=True) + "\n").encode()

    identity = capability_identity_from_document(
        document,
        registry_sha256="a" * 64,
        registry_bytes=len(raw),
    )

    assert identity["registry_sha256"] == "a" * 64
    assert identity["compiler_version"] == "0.1.0"
    assert identity["wir_core_version"] == 2
    assert "path" not in identity


def test_module_main_validates_saved_document_offline(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    document = tmp_path / "capabilities.json"
    document.write_text(
        json.dumps(capability_document_copy(), sort_keys=True) + "\n",
        encoding="utf-8",
    )

    assert main([str(document)]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["format"] == "weave-loupe-weavec-capability-identity-v1"
    assert output["capture_profile"]["command"] == "build"
