"""End-to-end tests for baseline-versus-candidate compiler audits."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from weave_loupe.compiler_audit import (
    COMPILER_AUDIT_FORMAT,
    COMPILER_AUDIT_POLICY_FORMAT,
    COMPILER_AUDIT_SEAL_FORMAT,
    audit_compilers,
)


def _write_compiler(
    directory: Path,
    name: str,
    *,
    extra_instructions: int = 1,
    runtime_bias: int = 0,
    compile_exit: int = 0,
) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    path.write_text(
        f"""#!/usr/bin/env python3
import json
import pathlib
import sys

args = sys.argv[1:]
if args == ["--version"]:
    print("weavec v0.3.0+git.{name}")
    raise SystemExit(0)
if {compile_exit}:
    print("configured compiler failure", file=sys.stderr)
    raise SystemExit({compile_exit})


def value(flag):
    return pathlib.Path(args[args.index(flag) + 1])


source = pathlib.Path(args[1])
value("--emit-wir").write_text(
    "(core-module (core-version 2) "
    "(decls (fn main (params) (returns i32) (do (return (const_i32 7))))))\\n"
)
value("--emit-llvm").write_text(
    "define i32 @main() {{\\n"
    "entry:\\n"
    "  ret i32 7\\n"
    "}}\\n"
)
extra = "".join(
    f"  %x{{index}} = mul i32 {{index + 2}}, 3\\n"
    for index in range({extra_instructions})
)
value("--emit-optimized-llvm").write_text(
    'target triple = "x86_64-unknown-linux-gnu"\\n'
    "define i32 @main() {{\\n"
    "entry:\\n"
    + extra
    + "  ret i32 7\\n"
    "}}\\n"
)
value("--emit-assembly").write_text("main:\\n  mov $7, %eax\\n  ret\\n")
value("--emit-disassembly").write_text(
    "demo: file format elf64-x86-64\\n"
    "0000000000000000 <main>:\\n"
    "   0: b8 07 00 00 00 mov $0x7,%eax\\n"
    "   5: c3 retq\\n"
)
value("--optimization-record").write_text("--- !Passed\\nPass: instcombine\\n...\\n")
value("--diagnostics-json").write_text(
    json.dumps({{"format": "weavec-diagnostics-v1", "diagnostics": []}}) + "\\n"
)
value("--trace-json").write_text(
    json.dumps(
        {{
            "format": "weavec-compilation-trace-v1",
            "events": [
                {{
                    "action": "lower",
                    "pass": "lowering",
                    "category": "lowering",
                }}
            ],
        }}
    )
    + "\\n"
)
value("--manifest-json").write_text(
    json.dumps(
        {{
            "format": "weavec-build-manifest-v1",
            "sources": [str(source)],
            "toolchain": {{
                "disassembler": {{"name": "llvm-objdump", "version": "19.1.7"}}
            }},
        }}
    )
    + "\\n"
)
program = value("-o")
program.write_text(
    "#!" + sys.executable + "\\n"
    "import os\\n"
    "raise SystemExit(int(os.environ.get('LOUPE_EXIT', '0')) + {runtime_bias})\\n"
)
program.chmod(0o755)
print("compiled")
""",
        encoding="utf-8",
    )
    path.chmod(0o755)
    return path


def _source(tmp_path: Path) -> Path:
    source = tmp_path / "demo.weave"
    source.write_text("(program (entry main))\n", encoding="utf-8")
    return source


def _write_runtime_case(source: Path, *, exit_code: int) -> None:
    source.with_suffix(".audit.json").write_text(
        json.dumps(
            {
                "format": "weave-loupe-runtime-cases-v1",
                "cases": [
                    {
                        "name": "result",
                        "env": {"LOUPE_EXIT": str(exit_code)},
                        "expect": {
                            "exit_code": exit_code,
                            "stdout": "",
                            "stderr": "",
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def _failure_codes(report: dict[str, object]) -> set[str]:
    failures = report["failures"]
    assert isinstance(failures, list)
    return {
        str(item["code"])
        for item in failures
        if isinstance(item, dict) and "code" in item
    }


def test_identical_compiler_produces_sealed_pass(tmp_path: Path) -> None:
    source = _source(tmp_path)
    _write_runtime_case(source, exit_code=0)
    compiler = _write_compiler(tmp_path, "weavec-same")

    report = audit_compilers(
        sources=[source],
        baseline_weavec=compiler,
        candidate_weavec=compiler,
        work_dir=tmp_path / "audit",
    )

    assert report["format"] == COMPILER_AUDIT_FORMAT
    assert report["status"] == "pass"
    assert report["passed"] is True
    assert report["comparison"]["runtime_equal"] is True
    bundle_diff = report["comparison"]["bundle_diff"]
    assert bundle_diff["format"] == "weave-loupe-diff-v2"
    supplemental = bundle_diff["supplemental"]
    assert supplemental["runtime"]["available"] is True
    assert supplemental["runtime"]["changed"] is False
    assert supplemental["native_budget"]["available"] is True
    assert supplemental["optimized_llvm_budget"]["available"] is True
    assert report["failures"] == []
    assert (
        report["baseline"]["compiler"]["sha256"]
        == report["candidate"]["compiler"]["sha256"]
    )
    seal = report["seal"]
    assert seal["format"] == COMPILER_AUDIT_SEAL_FORMAT
    unsealed = dict(report)
    unsealed.pop("seal")
    canonical = json.dumps(
        unsealed,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode()
    assert seal["sha256"] == hashlib.sha256(canonical).hexdigest()


def test_built_checkout_resolves_compiler(tmp_path: Path) -> None:
    source = _source(tmp_path)
    checkout = tmp_path / "weavec-checkout"
    _write_compiler(checkout / "build", "weavec")

    report = audit_compilers(
        sources=[source],
        baseline_weavec=checkout,
        candidate_weavec=checkout,
        work_dir=tmp_path / "audit",
    )

    assert report["passed"] is True
    assert report["baseline"]["compiler"]["path"].endswith("build/weavec")


def test_instruction_count_improvement_passes(tmp_path: Path) -> None:
    source = _source(tmp_path)
    baseline = _write_compiler(tmp_path, "weavec-base", extra_instructions=2)
    candidate = _write_compiler(tmp_path, "weavec-candidate", extra_instructions=1)

    report = audit_compilers(
        sources=[source],
        baseline_weavec=baseline,
        candidate_weavec=candidate,
        work_dir=tmp_path / "audit",
    )

    assert report["passed"] is True
    deltas = report["comparison"]["metric_deltas"]
    instructions = next(
        item
        for item in deltas
        if item["path"] == "analysis.optimized_llvm.instructions"
    )
    assert instructions["delta"] == -1
    assert instructions["passed"] is True


def test_policy_can_allow_reviewed_instruction_increase(tmp_path: Path) -> None:
    source = _source(tmp_path)
    baseline = _write_compiler(tmp_path, "weavec-base", extra_instructions=1)
    candidate = _write_compiler(tmp_path, "weavec-candidate", extra_instructions=2)
    policy = tmp_path / "policy.json"
    policy.write_text(
        json.dumps(
            {
                "format": COMPILER_AUDIT_POLICY_FORMAT,
                "metric_deltas": {
                    "analysis.optimized_llvm.instructions": {"maximum": 1}
                },
            }
        ),
        encoding="utf-8",
    )

    report = audit_compilers(
        sources=[source],
        baseline_weavec=baseline,
        candidate_weavec=candidate,
        work_dir=tmp_path / "audit",
        policy_path=policy,
    )

    assert report["passed"] is True


def test_runtime_regression_overrides_ok_reviewer(tmp_path: Path) -> None:
    source = _source(tmp_path)
    _write_runtime_case(source, exit_code=7)
    baseline = _write_compiler(tmp_path, "weavec-base", runtime_bias=0)
    candidate = _write_compiler(tmp_path, "weavec-candidate", runtime_bias=1)
    reviewed: list[dict[str, object]] = []

    def reviewer(evidence):
        reviewed.append(dict(evidence))
        return {"status": "OK", "body": "No model finding."}

    report = audit_compilers(
        sources=[source],
        baseline_weavec=baseline,
        candidate_weavec=candidate,
        work_dir=tmp_path / "audit",
        reviewer=reviewer,
    )

    assert reviewed
    assert report["review"]["status"] == "OK"
    assert report["passed"] is False
    assert "candidate-runtime-failed" in _failure_codes(report)
    assert "runtime-observations-changed" in _failure_codes(report)


def test_candidate_compilation_failure_is_regression(tmp_path: Path) -> None:
    source = _source(tmp_path)
    baseline = _write_compiler(tmp_path, "weavec-base")
    candidate = _write_compiler(tmp_path, "weavec-candidate", compile_exit=9)

    report = audit_compilers(
        sources=[source],
        baseline_weavec=baseline,
        candidate_weavec=candidate,
        work_dir=tmp_path / "audit",
    )

    assert report["status"] == "regression"
    assert "candidate-compilation-failed" in _failure_codes(report)
    assert report["candidate"]["runtime"]["skipped"] is True


def test_baseline_compilation_failure_is_infrastructure(tmp_path: Path) -> None:
    source = _source(tmp_path)
    baseline = _write_compiler(tmp_path, "weavec-base", compile_exit=8)
    candidate = _write_compiler(tmp_path, "weavec-candidate")

    report = audit_compilers(
        sources=[source],
        baseline_weavec=baseline,
        candidate_weavec=candidate,
        work_dir=tmp_path / "audit",
    )

    assert report["status"] == "infrastructure-failure"
    assert "baseline-compilation-failed" in _failure_codes(report)
