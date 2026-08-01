"""Golden tests for architecture-aware native disassembly analysis."""

from __future__ import annotations

from pathlib import Path

import pytest

from weave_loupe.native_disassembly import (
    NATIVE_DISASSEMBLY_PARSER_FORMAT,
    analyze_native_disassembly,
    normalize_symbol,
    parse_disassembly,
)

_FIXTURES = Path(__file__).parent / "fixtures" / "disassembly"
_OPTIMIZED_X86 = """target triple = "x86_64-unknown-linux-gnu"
define i32 @main() {
  ret i32 0
}
define i32 @fib(i32 %n) {
  ret i32 %n
}
"""
_OPTIMIZED_ARM = """target triple = "aarch64-unknown-linux-gnu"
define i32 @main() {
  ret i32 0
}
define i32 @fib(i32 %n) {
  ret i32 %n
}
"""


def _fixture(name: str) -> str:
    return (_FIXTURES / name).read_text(encoding="utf-8")


def _stable_metrics(result: dict[str, object]) -> dict[str, object]:
    functions = result["functions"]
    assert isinstance(functions, dict)
    return {
        "entry_point": result["entry_point"],
        "program_owned_functions": result["program_owned_functions"],
        "reachable_program_functions": result["reachable_program_functions"],
        "unreachable_program_functions": result["unreachable_program_functions"],
        "reachability_complete": result["reachability_complete"],
        "main": functions["main"],
        "fib": functions["fib"],
    }


@pytest.mark.parametrize(
    ("fixture", "optimized_llvm", "architecture", "object_format", "tool"),
    [
        (
            "x86_64-linux-gnu.txt",
            _OPTIMIZED_X86,
            "x86_64",
            "elf",
            "gnu-objdump",
        ),
        (
            "aarch64-linux-gnu.txt",
            _OPTIMIZED_ARM,
            "aarch64",
            "elf",
            "gnu-objdump",
        ),
        (
            "aarch64-macos-llvm.txt",
            _OPTIMIZED_ARM,
            "aarch64",
            "macho",
            "llvm-objdump",
        ),
    ],
)
def test_golden_disassembly_records_parser_evidence(
    fixture: str,
    optimized_llvm: str,
    architecture: str,
    object_format: str,
    tool: str,
) -> None:
    result = analyze_native_disassembly(_fixture(fixture), optimized_llvm)

    assert result["available"] is True
    assert result["supported"] is True
    assert result["failure_reason"] is None
    assert result["architecture"] == architecture
    assert result["object_format"] == object_format
    assert result["disassembler"] == tool
    assert result["disassembler_version"] in {"2.42", "19.1.7"}
    assert result["parser_format"] == NATIVE_DISASSEMBLY_PARSER_FORMAT


def test_golden_architectures_produce_equivalent_normalized_metrics() -> None:
    x86 = analyze_native_disassembly(
        _fixture("x86_64-linux-gnu.txt"),
        _OPTIMIZED_X86,
    )
    arm_linux = analyze_native_disassembly(
        _fixture("aarch64-linux-gnu.txt"),
        _OPTIMIZED_ARM,
    )
    arm_macos = analyze_native_disassembly(
        _fixture("aarch64-macos-llvm.txt"),
        _OPTIMIZED_ARM,
    )

    assert _stable_metrics(x86) == _stable_metrics(arm_linux)
    assert _stable_metrics(arm_linux) == _stable_metrics(arm_macos)
    main = x86["functions"]["main"]
    assert main == {
        "instructions": 4,
        "padding_instructions": 1,
        "direct_calls": ["fib"],
        "indirect_calls": 1,
        "conditional_branches": 1,
        "unconditional_branches": 0,
        "direct_branches": 1,
        "indirect_branches": 0,
        "backward_branches": 1,
        "backward_conditional_branches": 1,
        "returns": 1,
    }


def test_aarch64_classifies_cbz_and_tbz_target_operands() -> None:
    disassembly = """demo: file format elf64-littleaarch64
0000000000000100 <main>:
 100: b4000080 cbz x0, 110 <main+0x10>
 104: 3607ffe0 tbz w0, #0, 100 <main>
 108: d65f03c0 ret
"""
    llvm = """target triple = "aarch64-unknown-linux-gnu"
define i32 @main() {
  ret i32 0
}
"""

    result = analyze_native_disassembly(disassembly, llvm)
    main = result["functions"]["main"]

    assert main["conditional_branches"] == 2
    assert main["direct_branches"] == 2
    assert main["backward_branches"] == 1
    assert main["backward_conditional_branches"] == 1


def test_numeric_direct_call_resolves_through_function_address() -> None:
    disassembly = """demo: file format elf64-x86-64
0000000000000000 <main>:
 0: e8 0b 00 00 00 callq 10
 5: c3 retq
0000000000000010 <helper>:
 10: c3 retq
"""
    llvm = """target triple = "x86_64-unknown-linux-gnu"
define i32 @main() {
  ret i32 0
}
define i32 @helper() {
  ret i32 0
}
"""

    result = analyze_native_disassembly(disassembly, llvm)

    assert result["functions"]["main"]["direct_calls"] == ["helper"]
    assert result["reachable_program_functions"] == ["helper", "main"]


def test_unknown_architecture_is_explicitly_unsupported() -> None:
    disassembly = """demo: file format elf64-littleriscv
0000000000000100 <main>:
 100: 00008067 ret
"""

    result = analyze_native_disassembly(disassembly, "", architecture="riscv64")

    assert result["available"] is True
    assert result["supported"] is False
    assert result["architecture"] == "unknown"
    assert "unsupported native architecture" in result["failure_reason"]
    assert result["unreachable_program_instructions"] is None
    assert result["reachable_indirect_calls"] is None
    assert result["functions"] == {}


def test_conflicting_architecture_evidence_fails_closed() -> None:
    parsed = parse_disassembly(
        _fixture("aarch64-linux-gnu.txt"),
        optimized_llvm=_OPTIMIZED_X86,
    )

    assert parsed.supported is False
    assert parsed.metadata.architecture == "unknown"
    assert parsed.failure_reason is not None
    assert "conflicting native architecture evidence" in parsed.failure_reason


def test_manifest_disassembler_metadata_takes_precedence() -> None:
    result = analyze_native_disassembly(
        _fixture("x86_64-linux-gnu.txt"),
        _OPTIMIZED_X86,
        build_manifest={
            "toolchain": {
                "disassembler": {
                    "name": "/opt/llvm/bin/llvm-objdump",
                    "version": "20.0.1",
                }
            }
        },
    )

    assert result["disassembler"] == "llvm-objdump"
    assert result["disassembler_version"] == "20.0.1"


def test_symbol_normalization_preserves_distinct_compiler_symbols() -> None:
    assert normalize_symbol("foo+0x18") == "foo"
    assert normalize_symbol("foo@PLT") == "foo@plt"
    assert normalize_symbol("_main", object_format="macho") == "main"
    assert normalize_symbol("foo.llvm.123") == "foo.llvm.123"
    assert normalize_symbol("foo.cold") == "foo.cold"


def test_symbol_normalization_collision_fails_closed() -> None:
    disassembly = """demo: file format mach-o arm64
0000000100000000 <_main>:
100000000: ret
0000000100000010 <main>:
100000010: ret
"""

    parsed = parse_disassembly(disassembly, optimized_llvm=_OPTIMIZED_ARM)

    assert parsed.supported is False
    assert parsed.failure_reason is not None
    assert "symbol normalization collision" in parsed.failure_reason
