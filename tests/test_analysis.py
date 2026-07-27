"""Tests for deterministic artifact analysis."""

from __future__ import annotations

from pathlib import Path

from weave_loupe.analysis import (
    analyze_bundle,
    analyze_llvm,
    analyze_native,
    analyze_trace,
)
from weave_loupe.bundle import capture_bundle, load_bundle


def test_analyze_llvm_counts_structure() -> None:
    llvm = """define i32 @f() {
entry:
  %0 = alloca i32
  store i32 1, ptr %0
  %x = load i32, ptr %0
  %y = add i32 %x, 0
  br label %1
1:
  ret i32 %y
}
"""
    metrics = analyze_llvm(llvm)
    assert metrics["functions"] == 1
    assert metrics["basic_blocks"] == 2
    assert metrics["instructions"] == 6
    assert metrics["alloca"] == 1
    assert metrics["identity_adds"] == 1
    assert metrics["anonymous_ssa_lines"] == 4
    assert metrics["numeric_blocks"] == 1


def test_analyze_llvm_counts_provenance() -> None:
    metrics = analyze_llvm(
        "; weave.source kind=statement index=0 bytes=0..1 "
        'wir-bytes=0..2 path="x.weave"\n'
    )
    assert metrics["provenance_comments"] == 1


def test_analyze_native_finds_unreachable_program_code() -> None:
    optimized_llvm = """define i32 @main() {
  ret i32 55
}
define i32 @fib(i32 %n) {
  ret i32 %n
}
"""
    disassembly = """0000000000001150 <main>:
    1150: b8 37 00 00 00 movl $0x37, %eax
    1155: c3 retq
0000000000001160 <fib>:
    1160: 89 f8 movl %edi, %eax
    1162: c3 retq
0000000000001170 <weave_rt_contract_fail>:
    1170: 55 pushq %rbp
    1171: e8 00 00 00 00 callq 0x1040 <write@plt>
    1176: c3 retq
"""

    native = analyze_native(disassembly, optimized_llvm)

    assert native["reachability_complete"] is True
    assert native["reachable_program_functions"] == ["main"]
    assert native["unreachable_program_functions"] == [
        "fib",
        "weave_rt_contract_fail",
    ]
    assert native["unreachable_program_instructions"] == 5


def test_analyze_native_follows_direct_program_calls() -> None:
    optimized_llvm = """define i32 @main() {
  %value = call i32 @fib(i32 10)
  ret i32 %value
}
define i32 @fib(i32 %n) {
  ret i32 %n
}
"""
    disassembly = """0000000000000000 <main>:
   0: e8 05 00 00 00 callq 0xa <fib>
   5: c3 retq
000000000000000a <fib>:
   a: 89 f8 movl %edi, %eax
   c: c3 retq
"""

    native = analyze_native(disassembly, optimized_llvm)

    assert native["reachable_program_functions"] == ["fib", "main"]
    assert native["unreachable_program_functions"] == []


def test_analyze_trace_groups_actions() -> None:
    summary = analyze_trace(
        {
            "events": [
                {"action": "x", "pass": "lower", "category": "lowering"},
                {"action": "x", "pass": "lower", "category": "lowering"},
            ]
        }
    )
    assert summary["events"] == 2
    assert summary["actions"] == {"x": 2}


def test_analyze_bundle_uses_captured_artifacts(
    tmp_path: Path, source_file: Path, fake_weavec: Path
) -> None:
    output = tmp_path / "demo.loupe"
    capture_bundle(sources=[source_file], output=output, weavec=fake_weavec)
    analysis = analyze_bundle(load_bundle(output))
    assert analysis["format"] == "weave-loupe-analysis-v1"
    assert analysis["compiler_exit_code"] == 0
    assert analysis["trace"]["events"] == 1
    assert analysis["llvm"]["identity_adds"] == 1
    assert analysis["native"]["unreachable_program_functions"] == []
