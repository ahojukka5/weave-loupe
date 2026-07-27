"""Deterministic structural analysis of compiler artifacts."""

from __future__ import annotations

import re
from collections import Counter, deque
from typing import Any

from weave_loupe.bundle import Bundle

_FUNCTION = re.compile(r"^\s*define\b")
_LLVM_FUNCTION_NAME = re.compile(r'^\s*define\b.*?@(?:"([^"]+)"|([-A-Za-z$._0-9]+))\(')
_LABEL = re.compile(r"^\s*[-A-Za-z$._][-A-Za-z$._0-9]*:\s*(?:;.*)?$")
_NUMERIC_LABEL = re.compile(r"^\s*\d+:\s*(?:;.*)?$")
_ANON_SSA = re.compile(r"%\d+\b")
_IDENTITY_ADD = re.compile(r"\badd\b[^;]*,\s*0\b")
_DISASSEMBLY_FUNCTION = re.compile(r"^\s*[0-9a-fA-F]+ <([^>]+)>:\s*$")
_DISASSEMBLY_INSTRUCTION = re.compile(
    r"^\s*[0-9a-fA-F]+:\s+"
    r"(?:(?:[0-9a-fA-F]{2})\s+)+"
    r"\s*([A-Za-z][A-Za-z0-9_.]*)\s*(.*)$"
)
_DISASSEMBLY_TARGET = re.compile(r"<([^>]+)>")


def analyze_bundle(bundle: Bundle) -> dict[str, Any]:
    """Return a stable machine-readable summary for reports and audits."""
    optimized_llvm = bundle.artifact_text("optimized_llvm") or ""
    disassembly = bundle.artifact_text("disassembly") or ""
    return {
        "format": "weave-loupe-analysis-v1",
        "compiler_exit_code": _compiler_exit_code(bundle),
        "llvm": analyze_llvm(bundle.artifact_text("llvm") or ""),
        "optimized_llvm": analyze_llvm(optimized_llvm),
        "native": analyze_native(disassembly, optimized_llvm),
        "evidence": {
            name: bundle.artifact_path(name) is not None
            for name in (
                "wir",
                "llvm",
                "optimized_llvm",
                "assembly",
                "disassembly",
                "optimization_record",
                "diagnostics",
                "trace",
                "build_manifest",
            )
        },
        "trace": analyze_trace(bundle.artifact_json("trace")),
        "diagnostics": analyze_diagnostics(bundle.artifact_json("diagnostics")),
    }


def analyze_llvm(llvm_ir: str) -> dict[str, Any]:
    """Count structural LLVM patterns without requiring LLVM bindings."""
    metrics: Counter[str] = Counter()
    inside_function = False
    for raw in llvm_ir.splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith(";"):
            continue
        if _FUNCTION.match(raw):
            inside_function = True
            metrics["functions"] += 1
            continue
        if inside_function and stripped == "}":
            inside_function = False
            continue
        if not inside_function:
            continue
        if _LABEL.match(raw) or _NUMERIC_LABEL.match(raw):
            metrics["basic_blocks"] += 1
            if _NUMERIC_LABEL.match(raw):
                metrics["numeric_blocks"] += 1
            continue
        metrics["instructions"] += 1
        if _ANON_SSA.search(raw):
            metrics["anonymous_ssa_lines"] += 1
        opcode = _opcode(stripped)
        if opcode:
            metrics[opcode] += 1
        if _IDENTITY_ADD.search(stripped):
            metrics["identity_adds"] += 1
        if " undef" in f" {stripped}":
            metrics["undef_uses"] += 1
        if " poison" in f" {stripped}":
            metrics["poison_uses"] += 1

    provenance = sum(
        1 for line in llvm_ir.splitlines() if line.startswith("; weave.source ")
    )
    result = {key: metrics.get(key, 0) for key in _metric_keys()}
    result["provenance_comments"] = provenance
    return result


def analyze_native(disassembly: str, optimized_llvm: str) -> dict[str, Any]:
    """Analyze program-owned native functions and their direct reachability."""
    llvm_functions = _llvm_function_names(optimized_llvm)
    functions: dict[str, dict[str, Any]] = {}
    current: str | None = None

    for line in disassembly.splitlines():
        header = _DISASSEMBLY_FUNCTION.match(line)
        if header is not None:
            current = _normalize_symbol(header.group(1))
            functions.setdefault(
                current,
                {
                    "instructions": 0,
                    "padding_instructions": 0,
                    "direct_calls": set(),
                    "indirect_calls": 0,
                },
            )
            continue
        if current is None:
            continue
        instruction = _DISASSEMBLY_INSTRUCTION.match(line)
        if instruction is None:
            continue
        mnemonic = instruction.group(1).lower()
        operands = instruction.group(2)
        details = functions[current]
        if mnemonic.startswith("nop"):
            details["padding_instructions"] += 1
        else:
            details["instructions"] += 1
        if mnemonic.startswith("call"):
            target = _direct_call_target(operands)
            if target is None:
                details["indirect_calls"] += 1
            else:
                details["direct_calls"].add(target)

    runtime_functions = {name for name in functions if name.startswith("weave_")}
    program_owned = llvm_functions | runtime_functions
    present_owned = program_owned & functions.keys()
    reachable = _reachable_functions(functions, present_owned, root="main")
    reachable_indirect_calls = sum(
        int(functions[name]["indirect_calls"])
        for name in reachable
        if name in functions
    )
    reachability_complete = "main" in present_owned and reachable_indirect_calls == 0
    unreachable = sorted(present_owned - reachable) if reachability_complete else []

    serialized_functions: dict[str, dict[str, Any]] = {}
    for name in sorted(functions):
        details = functions[name]
        serialized_functions[name] = {
            "instructions": details["instructions"],
            "padding_instructions": details["padding_instructions"],
            "direct_calls": sorted(details["direct_calls"]),
            "indirect_calls": details["indirect_calls"],
        }

    return {
        "available": bool(disassembly.strip()),
        "entry_point": "main" if "main" in present_owned else None,
        "llvm_functions": sorted(llvm_functions),
        "runtime_functions": sorted(runtime_functions),
        "program_owned_functions": sorted(present_owned),
        "reachable_program_functions": sorted(reachable),
        "unreachable_program_functions": unreachable,
        "unreachable_program_instructions": sum(
            int(functions[name]["instructions"]) for name in unreachable
        ),
        "reachable_indirect_calls": reachable_indirect_calls,
        "reachability_complete": reachability_complete,
        "functions": serialized_functions,
    }


def analyze_trace(document: Any | None) -> dict[str, Any]:
    """Summarize trace events by stable action, pass, and category."""
    events: list[Any] = []
    if isinstance(document, dict) and isinstance(document.get("events"), list):
        events = document["events"]
    actions: Counter[str] = Counter()
    passes: Counter[str] = Counter()
    categories: Counter[str] = Counter()
    for event in events:
        if not isinstance(event, dict):
            continue
        _count_text(actions, event.get("action"))
        _count_text(passes, event.get("pass"))
        _count_text(categories, event.get("category") or event.get("kind"))
    return {
        "events": len(events),
        "actions": dict(sorted(actions.items())),
        "passes": dict(sorted(passes.items())),
        "categories": dict(sorted(categories.items())),
    }


def analyze_diagnostics(document: Any | None) -> dict[str, Any]:
    """Summarize the public diagnostics document conservatively."""
    if not isinstance(document, dict):
        return {"available": False, "items": 0}
    raw_items = document.get("diagnostics")
    items = raw_items if isinstance(raw_items, list) else []
    severities: Counter[str] = Counter()
    for item in items:
        if isinstance(item, dict):
            _count_text(severities, item.get("severity") or item.get("level"))
    return {
        "available": True,
        "items": len(items),
        "severities": dict(sorted(severities.items())),
    }


def _llvm_function_names(llvm_ir: str) -> set[str]:
    names: set[str] = set()
    for line in llvm_ir.splitlines():
        match = _LLVM_FUNCTION_NAME.match(line)
        if match is not None:
            names.add(match.group(1) or match.group(2))
    return names


def _direct_call_target(operands: str) -> str | None:
    if operands.lstrip().startswith("*"):
        return None
    target = _DISASSEMBLY_TARGET.search(operands)
    if target is None:
        return None
    return _normalize_symbol(target.group(1))


def _normalize_symbol(symbol: str) -> str:
    return symbol.split("+", 1)[0]


def _reachable_functions(
    functions: dict[str, dict[str, Any]],
    program_owned: set[str],
    *,
    root: str,
) -> set[str]:
    if root not in program_owned:
        return set()
    reachable: set[str] = set()
    queue = deque([root])
    while queue:
        name = queue.popleft()
        if name in reachable:
            continue
        reachable.add(name)
        details = functions.get(name, {})
        calls = details.get("direct_calls", set())
        if isinstance(calls, set):
            queue.extend(sorted(calls & program_owned - reachable))
    return reachable


def _compiler_exit_code(bundle: Bundle) -> int:
    compiler = bundle.manifest.get("compiler", {})
    if isinstance(compiler, dict):
        exit_code = compiler.get("exit_code")
        if isinstance(exit_code, int):
            return exit_code
    return -1


def _count_text(counter: Counter[str], value: object) -> None:
    if isinstance(value, str) and value:
        counter[value] += 1


def _opcode(instruction: str) -> str | None:
    body = instruction.split("=", 1)[-1].strip() if "=" in instruction else instruction
    words = body.split()
    if not words:
        return None
    opcode = words[0]
    if opcode in {"tail", "musttail", "notail"} and len(words) > 1:
        opcode = words[1]
    tracked = {
        "alloca",
        "load",
        "store",
        "call",
        "invoke",
        "phi",
        "br",
        "switch",
        "ret",
        "add",
        "sub",
        "mul",
        "sdiv",
        "udiv",
        "icmp",
        "select",
    }
    return opcode if opcode in tracked else None


def _metric_keys() -> tuple[str, ...]:
    return (
        "functions",
        "basic_blocks",
        "instructions",
        "alloca",
        "load",
        "store",
        "call",
        "invoke",
        "phi",
        "br",
        "switch",
        "ret",
        "add",
        "sub",
        "mul",
        "sdiv",
        "udiv",
        "icmp",
        "select",
        "identity_adds",
        "anonymous_ssa_lines",
        "numeric_blocks",
        "undef_uses",
        "poison_uses",
    )
