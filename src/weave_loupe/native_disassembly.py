"""Architecture-aware normalization of linked executable disassembly."""

from __future__ import annotations

import re
from collections import deque
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import PurePath
from typing import Any

from weave_loupe.native_architectures import ArchitectureParser, parser_for

NATIVE_DISASSEMBLY_PARSER_FORMAT = "weave-loupe-native-disassembly-v1"

_FUNCTION_HEADER = re.compile(r"^\s*([0-9a-fA-F]+)\s+<([^>]+)>:\s*$")
_INSTRUCTION_LINE = re.compile(r"^\s*([0-9a-fA-F]+):\s*(.*?)\s*$")
_TARGET_SYMBOL = re.compile(r"<([^>]+)>")
_TARGET_TRIPLE = re.compile(
    r'^\s*target\s+triple\s*=\s*"([^"]+)"',
    re.MULTILINE,
)
_FILE_FORMAT = re.compile(
    r"\bfile\s+format\s+([^\s]+(?:\s+arm64)?)",
    re.IGNORECASE,
)
_ARCHITECTURE_HEADER = re.compile(
    r"\barchitecture:\s*([^,\s]+)",
    re.IGNORECASE,
)
_SYMBOL_OFFSET = re.compile(r"(?P<name>.*?)(?:[+-]0x[0-9a-fA-F]+)$")
_VERSION = re.compile(r"\b(\d+(?:\.\d+)+(?:[-+._A-Za-z0-9]*)?)\b")
_HEX_ENCODING_LENGTHS = frozenset({2, 4, 8, 16})
_X86_PREFIXES = frozenset(
    {
        "addr16",
        "data16",
        "lock",
        "rep",
        "repe",
        "repne",
        "repnz",
        "repz",
        "rex64",
    }
)


@dataclass(frozen=True)
class NormalizedInstruction:
    """One parsed instruction with normalized control-flow fields."""

    address: int
    mnemonic: str
    operands: str
    kind: str
    conditional: bool
    direct: bool | None
    target_address: int | None
    target_symbol: str | None


@dataclass(frozen=True)
class NormalizedFunction:
    """One disassembled function before metric aggregation."""

    name: str
    raw_name: str
    address: int
    instructions: tuple[NormalizedInstruction, ...]


@dataclass(frozen=True)
class DisassemblyMetadata:
    """Evidence describing how native parsing was selected."""

    architecture: str
    object_format: str
    disassembler: str
    disassembler_version: str | None
    parser_format: str = NATIVE_DISASSEMBLY_PARSER_FORMAT

    def as_dict(self) -> dict[str, str | None]:
        return {
            "architecture": self.architecture,
            "object_format": self.object_format,
            "disassembler": self.disassembler,
            "disassembler_version": self.disassembler_version,
            "parser_format": self.parser_format,
        }


@dataclass(frozen=True)
class ParsedDisassembly:
    """Normalized disassembly plus fail-closed parser status."""

    available: bool
    supported: bool
    metadata: DisassemblyMetadata
    functions: tuple[NormalizedFunction, ...]
    failure_reason: str | None = None


def parse_disassembly(
    disassembly: str,
    *,
    optimized_llvm: str = "",
    build_manifest: object | None = None,
    architecture: str | None = None,
) -> ParsedDisassembly:
    """Parse linked disassembly using a fail-closed architecture selection."""
    available = bool(disassembly.strip())
    object_format = _detect_object_format(disassembly)
    tool, tool_version = _detect_disassembler(disassembly, build_manifest)
    detected, architecture_error = _detect_architecture(
        explicit=architecture,
        optimized_llvm=optimized_llvm,
        disassembly=disassembly,
    )
    metadata = DisassemblyMetadata(
        architecture=detected,
        object_format=object_format,
        disassembler=tool,
        disassembler_version=tool_version,
    )
    if not available:
        return ParsedDisassembly(
            available=False,
            supported=False,
            metadata=metadata,
            functions=(),
            failure_reason="linked executable disassembly is unavailable",
        )
    if architecture_error is not None:
        return ParsedDisassembly(
            available=True,
            supported=False,
            metadata=metadata,
            functions=(),
            failure_reason=architecture_error,
        )
    parser = parser_for(detected)
    if parser is None:
        return ParsedDisassembly(
            available=True,
            supported=False,
            metadata=metadata,
            functions=(),
            failure_reason=(
                f"unsupported native architecture {detected!r}; supported "
                "architectures are aarch64 and x86_64"
            ),
        )
    functions, parsing_error = _parse_functions(
        disassembly,
        parser=parser,
        object_format=object_format,
    )
    if parsing_error is not None:
        return ParsedDisassembly(
            available=True,
            supported=False,
            metadata=metadata,
            functions=functions,
            failure_reason=parsing_error,
        )
    if not functions:
        return ParsedDisassembly(
            available=True,
            supported=False,
            metadata=metadata,
            functions=(),
            failure_reason=(
                f"no functions could be parsed from {detected} disassembly"
            ),
        )
    return ParsedDisassembly(
        available=True,
        supported=True,
        metadata=metadata,
        functions=functions,
    )


def analyze_native_disassembly(
    disassembly: str,
    optimized_llvm: str,
    *,
    build_manifest: object | None = None,
    architecture: str | None = None,
) -> dict[str, Any]:
    """Return stable native metrics from normalized disassembly."""
    parsed = parse_disassembly(
        disassembly,
        optimized_llvm=optimized_llvm,
        build_manifest=build_manifest,
        architecture=architecture,
    )
    result: dict[str, Any] = {
        "available": parsed.available,
        "supported": parsed.supported,
        **parsed.metadata.as_dict(),
        "failure_reason": parsed.failure_reason,
    }
    if not parsed.supported:
        result.update(_empty_analysis())
        return result

    llvm_functions = _llvm_function_names(optimized_llvm)
    functions = _aggregate_functions(parsed.functions)
    runtime_functions = {name for name in functions if name.startswith("weave_")}
    program_owned = llvm_functions | runtime_functions
    present_owned = program_owned & functions.keys()
    reachable = _reachable_functions(functions, present_owned, root="main")
    indirect_calls = sum(
        int(functions[name]["indirect_calls"])
        for name in reachable
        if name in functions
    )
    complete = "main" in present_owned and indirect_calls == 0
    unreachable = sorted(present_owned - reachable) if complete else []

    result.update(
        {
            "entry_point": "main" if "main" in present_owned else None,
            "llvm_functions": sorted(llvm_functions),
            "runtime_functions": sorted(runtime_functions),
            "program_owned_functions": sorted(present_owned),
            "reachable_program_functions": sorted(reachable),
            "unreachable_program_functions": unreachable,
            "unreachable_program_instructions": sum(
                int(functions[name]["instructions"]) for name in unreachable
            ),
            "reachable_indirect_calls": indirect_calls,
            "reachability_complete": complete,
            "functions": _serialize_functions(functions),
        }
    )
    return result


def normalize_symbol(symbol: str, *, object_format: str = "unknown") -> str:
    """Remove display-only decorations without merging generated symbols."""
    value = symbol.strip()
    offset = _SYMBOL_OFFSET.fullmatch(value)
    if offset is not None:
        value = offset.group("name")
    value = re.sub(r"@plt$", "@plt", value, flags=re.IGNORECASE)
    is_macho_public = (
        object_format == "macho"
        and value.startswith("_")
        and not value.startswith("__")
    )
    return value[1:] if is_macho_public else value


def _parse_functions(
    disassembly: str,
    *,
    parser: ArchitectureParser,
    object_format: str,
) -> tuple[tuple[NormalizedFunction, ...], str | None]:
    raw_functions: list[tuple[int, str, list[NormalizedInstruction]]] = []
    current: tuple[int, str, list[NormalizedInstruction]] | None = None
    for line in disassembly.splitlines():
        header = _FUNCTION_HEADER.match(line)
        if header is not None:
            current = (int(header.group(1), 16), header.group(2), [])
            raw_functions.append(current)
            continue
        if current is None:
            continue
        instruction = _parse_instruction_line(line)
        if instruction is None:
            continue
        address, mnemonic, operands = instruction
        semantics = parser.semantics(mnemonic, operands)
        target_address = None
        target_symbol = None
        if semantics.target_operand is not None:
            target_address = _target_address(semantics.target_operand)
            target_symbol = _target_symbol(
                semantics.target_operand,
                object_format,
            )
        current[2].append(
            NormalizedInstruction(
                address=address,
                mnemonic=mnemonic,
                operands=operands,
                kind=semantics.kind,
                conditional=semantics.conditional,
                direct=semantics.direct,
                target_address=target_address,
                target_symbol=target_symbol,
            )
        )
    return _normalize_functions(raw_functions, object_format=object_format)


def _normalize_functions(
    raw_functions: list[tuple[int, str, list[NormalizedInstruction]]],
    *,
    object_format: str,
) -> tuple[tuple[NormalizedFunction, ...], str | None]:
    address_names: dict[int, str] = {}
    normalized: list[NormalizedFunction] = []
    identities: dict[str, tuple[str, int]] = {}
    for address, raw_name, instructions in raw_functions:
        name = normalize_symbol(raw_name, object_format=object_format)
        prior = identities.get(name)
        if prior is not None and prior != (raw_name, address):
            reason = (
                "symbol normalization collision for "
                f"{prior[0]!r} and {raw_name!r} as {name!r}"
            )
            return tuple(normalized), reason
        identities[name] = (raw_name, address)
        address_names[address] = name
        normalized.append(
            NormalizedFunction(
                name=name,
                raw_name=raw_name,
                address=address,
                instructions=tuple(instructions),
            )
        )

    resolved = tuple(
        _resolve_function_targets(function, address_names) for function in normalized
    )
    return resolved, None


def _resolve_function_targets(
    function: NormalizedFunction,
    address_names: dict[int, str],
) -> NormalizedFunction:
    instructions: list[NormalizedInstruction] = []
    for instruction in function.instructions:
        target_symbol = instruction.target_symbol
        if target_symbol is None and instruction.target_address is not None:
            target_symbol = address_names.get(instruction.target_address)
        instructions.append(
            NormalizedInstruction(
                address=instruction.address,
                mnemonic=instruction.mnemonic,
                operands=instruction.operands,
                kind=instruction.kind,
                conditional=instruction.conditional,
                direct=instruction.direct,
                target_address=instruction.target_address,
                target_symbol=target_symbol,
            )
        )
    return NormalizedFunction(
        name=function.name,
        raw_name=function.raw_name,
        address=function.address,
        instructions=tuple(instructions),
    )


def _parse_instruction_line(line: str) -> tuple[int, str, str] | None:
    match = _INSTRUCTION_LINE.match(line)
    if match is None:
        return None
    tokens = match.group(2).split()
    while tokens and _is_encoding_token(tokens[0]):
        tokens.pop(0)
    while len(tokens) > 1 and tokens[0].lower() in _X86_PREFIXES:
        tokens.pop(0)
    if not tokens:
        return None
    mnemonic = tokens.pop(0).lower()
    return int(match.group(1), 16), mnemonic, " ".join(tokens)


def _is_encoding_token(token: str) -> bool:
    return len(token) in _HEX_ENCODING_LENGTHS and all(
        character in "0123456789abcdefABCDEF" for character in token
    )


def _aggregate_functions(
    parsed_functions: tuple[NormalizedFunction, ...],
) -> dict[str, dict[str, Any]]:
    functions: dict[str, dict[str, Any]] = {}
    for function in parsed_functions:
        details = _empty_function_metrics()
        for instruction in function.instructions:
            _accumulate_instruction(details, instruction)
        functions[function.name] = details
    return functions


def _empty_function_metrics() -> dict[str, Any]:
    return {
        "instructions": 0,
        "padding_instructions": 0,
        "direct_calls": set(),
        "indirect_calls": 0,
        "conditional_branches": 0,
        "unconditional_branches": 0,
        "direct_branches": 0,
        "indirect_branches": 0,
        "backward_branches": 0,
        "backward_conditional_branches": 0,
        "returns": 0,
    }


def _accumulate_instruction(
    details: dict[str, Any],
    instruction: NormalizedInstruction,
) -> None:
    if instruction.kind == "padding":
        details["padding_instructions"] += 1
        return
    details["instructions"] += 1
    if instruction.kind == "return":
        details["returns"] += 1
    if instruction.kind == "call":
        if instruction.direct is True:
            if instruction.target_symbol is not None:
                details["direct_calls"].add(instruction.target_symbol)
        else:
            details["indirect_calls"] += 1
    if instruction.kind != "branch":
        return
    branch_key = (
        "conditional_branches" if instruction.conditional else "unconditional_branches"
    )
    details[branch_key] += 1
    direct_key = (
        "direct_branches" if instruction.direct is True else "indirect_branches"
    )
    details[direct_key] += 1
    is_backward = (
        instruction.target_address is not None
        and instruction.target_address < instruction.address
    )
    if is_backward:
        details["backward_branches"] += 1
        if instruction.conditional:
            details["backward_conditional_branches"] += 1


def _serialize_functions(
    functions: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    serialized: dict[str, dict[str, Any]] = {}
    for name in sorted(functions):
        details = functions[name]
        serialized[name] = {
            "instructions": details["instructions"],
            "padding_instructions": details["padding_instructions"],
            "direct_calls": sorted(details["direct_calls"]),
            "indirect_calls": details["indirect_calls"],
            "conditional_branches": details["conditional_branches"],
            "unconditional_branches": details["unconditional_branches"],
            "direct_branches": details["direct_branches"],
            "indirect_branches": details["indirect_branches"],
            "backward_branches": details["backward_branches"],
            "backward_conditional_branches": details["backward_conditional_branches"],
            "returns": details["returns"],
        }
    return serialized


def _empty_analysis() -> dict[str, Any]:
    return {
        "entry_point": None,
        "llvm_functions": [],
        "runtime_functions": [],
        "program_owned_functions": [],
        "reachable_program_functions": [],
        "unreachable_program_functions": [],
        "unreachable_program_instructions": None,
        "reachable_indirect_calls": None,
        "reachability_complete": False,
        "functions": {},
    }


def _llvm_function_names(llvm_ir: str) -> set[str]:
    pattern = re.compile(r'^\s*define\b.*?@(?:"([^"]+)"|([-A-Za-z$._0-9]+))\(')
    names: set[str] = set()
    for line in llvm_ir.splitlines():
        match = pattern.match(line)
        if match is not None:
            names.add(match.group(1) or match.group(2))
    return names


def _target_symbol(operands: str, object_format: str) -> str | None:
    match = _TARGET_SYMBOL.search(operands)
    if match is None:
        return None
    return normalize_symbol(match.group(1), object_format=object_format)


def _target_address(operands: str) -> int | None:
    without_symbol = operands.split("<", 1)[0]
    pattern = r"(?<![A-Za-z0-9_])(?:#)?(?:0x)?([0-9a-fA-F]+)\b"
    candidates = re.findall(pattern, without_symbol)
    return int(candidates[-1], 16) if candidates else None


def _detect_architecture(
    *,
    explicit: str | None,
    optimized_llvm: str,
    disassembly: str,
) -> tuple[str, str | None]:
    candidates: list[tuple[str, str]] = []
    if explicit is not None:
        candidates.append(("explicit", _normalize_architecture(explicit)))
    triple = _TARGET_TRIPLE.search(optimized_llvm)
    if triple is not None:
        candidates.append(
            (
                "LLVM target triple",
                _normalize_architecture(triple.group(1)),
            )
        )
    file_architecture = _architecture_from_file_header(disassembly)
    if file_architecture is not None:
        candidates.append(("disassembly header", file_architecture))
    heuristic = _architecture_from_instructions(disassembly)
    if heuristic is not None:
        candidates.append(("instruction syntax", heuristic))

    known = [(source, value) for source, value in candidates if value != "unknown"]
    values = {value for _, value in known}
    if len(values) > 1:
        description = ", ".join(f"{source}={value}" for source, value in known)
        return (
            "unknown",
            f"conflicting native architecture evidence: {description}",
        )
    if values:
        return next(iter(values)), None
    return "unknown", None


def _architecture_from_file_header(disassembly: str) -> str | None:
    format_match = _FILE_FORMAT.search(disassembly)
    if format_match is not None:
        architecture = _normalize_architecture(format_match.group(1))
        if architecture != "unknown":
            return architecture
    header_match = _ARCHITECTURE_HEADER.search(disassembly)
    if header_match is not None:
        architecture = _normalize_architecture(header_match.group(1))
        if architecture != "unknown":
            return architecture
    return None


def _architecture_from_instructions(disassembly: str) -> str | None:
    x86_score = 0
    aarch64_score = 0
    for line in disassembly.splitlines():
        parsed = _parse_instruction_line(line)
        if parsed is None:
            continue
        _, mnemonic, operands = parsed
        lowered = operands.lower()
        if mnemonic in {"bl", "blr", "br", "cbz", "cbnz", "tbz", "tbnz"}:
            aarch64_score += 3
        if mnemonic.startswith("b.") or re.search(
            r"\b[wx][0-9]+\b",
            lowered,
        ):
            aarch64_score += 2
        if mnemonic.startswith("call") or mnemonic.startswith("jmp"):
            x86_score += 3
        if mnemonic.endswith("q") or "%" in operands:
            x86_score += 1
    if aarch64_score > x86_score and aarch64_score > 0:
        return "aarch64"
    if x86_score > aarch64_score and x86_score > 0:
        return "x86_64"
    return None


def _normalize_architecture(value: str) -> str:
    lowered = value.strip().lower().replace("_", "-")
    if "aarch64" in lowered or "arm64" in lowered:
        return "aarch64"
    x86_tokens = ("x86-64", "amd64", "i386:x86-64")
    if any(token in lowered for token in x86_tokens):
        return "x86_64"
    return "unknown"


def _detect_object_format(disassembly: str) -> str:
    lowered = disassembly.lower()
    if "file format mach-o" in lowered or "file format macho" in lowered:
        return "macho"
    if "file format elf" in lowered:
        return "elf"
    if "file format coff" in lowered or "file format pei" in lowered:
        return "coff"
    return "unknown"


def _detect_disassembler(
    disassembly: str,
    build_manifest: object | None,
) -> tuple[str, str | None]:
    manifest_result = _disassembler_from_manifest(build_manifest)
    if manifest_result is not None:
        return manifest_result
    for line in disassembly.splitlines()[:20]:
        lowered = line.lower()
        if "llvm-objdump" in lowered:
            return "llvm-objdump", _version_from_text(line)
        if "gnu objdump" in lowered:
            return "gnu-objdump", _version_from_text(line)
    return "unknown", None


def _disassembler_from_manifest(
    document: object | None,
) -> tuple[str, str | None] | None:
    if isinstance(document, Mapping):
        for key, value in document.items():
            normalized = str(key).lower().replace("_", "-")
            if normalized in {"disassembler", "objdump", "llvm-objdump"}:
                parsed = _tool_value(value)
                if parsed is not None:
                    return parsed
        for value in document.values():
            nested = _disassembler_from_manifest(value)
            if nested is not None:
                return nested
    elif isinstance(document, list):
        for value in document:
            nested = _disassembler_from_manifest(value)
            if nested is not None:
                return nested
    elif isinstance(document, str) and "objdump" in document.lower():
        return _tool_value(document)
    return None


def _tool_value(value: object) -> tuple[str, str | None] | None:
    if isinstance(value, Mapping):
        raw_name: str | None = None
        for key in ("name", "tool", "path", "command", "executable"):
            item = value.get(key)
            if isinstance(item, str) and item:
                raw_name = item
                break
        raw_version = value.get("version")
        version = raw_version if isinstance(raw_version, str) and raw_version else None
        if raw_name is None:
            return None
        return _tool_name(raw_name), version or _version_from_text(raw_name)
    if isinstance(value, str):
        return _tool_name(value), _version_from_text(value)
    return None


def _tool_name(value: str) -> str:
    lowered = value.lower()
    if "llvm-objdump" in lowered:
        return "llvm-objdump"
    if "objdump" in lowered:
        return "gnu-objdump"
    return PurePath(value.split()[0]).name


def _version_from_text(value: str) -> str | None:
    match = _VERSION.search(value)
    return match.group(1) if match is not None else None


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
        calls = functions.get(name, {}).get("direct_calls", set())
        if isinstance(calls, set):
            queue.extend(sorted(calls & program_owned - reachable))
    return reachable
