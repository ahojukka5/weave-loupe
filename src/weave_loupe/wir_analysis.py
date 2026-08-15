"""Deterministic structural analysis for every supported WIR core version.

The analysis is form-generic: it counts opcodes without an allowlist and
interprets only the envelope, the declaration and contract roles, the
control-flow and operand forms it builds a control-flow graph from, and call
operators. A version that adds expression forms is therefore analysable without
a change here, and the version it declares is reported rather than assumed.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from weave_loupe.wir_syntax import (
    SUPPORTED_CORE_VERSIONS,
    WirAtom,
    WirComment,
    WirDocument,
    WirList,
    WirSyntaxError,
    atom_text,
    describe_supported_core_versions,
    head,
    parse_wir,
    walk,
)

WIR_ANALYSIS_FORMAT = "weave-loupe-wir-analysis-v1"

_FILE_COMMENT = re.compile(r'^weavec-source-file-v1\s+(\d+)\s+("(?:[^"\\]|\\.)*")\s*$')
_SPAN_COMMENT = re.compile(r"^weavec-source-span-v1\s+(\d+)\s+(\d+)\s+(\d+)\s*$")
_LLVM_FUNCTION = re.compile(
    r'^\s*(define|declare)\b.*?@("(?:[^"\\]|\\.)*"|[-A-Za-z$._][-A-Za-z$._0-9]*)\s*\('
)
_LLVM_LABEL = re.compile(r"^\s*(?:[-A-Za-z$._][-A-Za-z$._0-9]*|\d+):")
_ANONYMOUS_NAME = re.compile(r"^(?:%?\d+|_+|anon(?:ymous)?(?:[._-]\d+)?)$")
_CALL_HEAD = re.compile(r"^call(?:_|$)")
_KNOWN_TYPES = frozenset(
    {"bool", "f32", "f64", "i8", "i16", "i32", "i64", "ptr", "void"}
)
_WRAPPERS = frozenset(
    {
        "condition",
        "decls",
        "do",
        "else",
        "ensures",
        "params",
        "requires",
        "returns",
        "then",
    }
)
_METRIC_KEYS = (
    "declarations",
    "functions",
    "externs",
    "unknown_declarations",
    "blocks",
    "reachable_blocks",
    "unreachable_blocks",
    "control_flow_edges",
    "backedges",
    "instructions",
    "operands",
    "calls",
    "branches",
    "loops",
    "returns",
    "locals",
    "anonymous_identifiers",
    "unresolved_symbols",
    "duplicate_declarations",
    "malformed_provenance",
    "provenance_files",
    "provenance_spans",
    "mapped_functions",
    "mapped_instructions",
)


@dataclass
class _Block:
    identifier: str
    role: str
    reachable: bool
    opcodes: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.identifier,
            "role": self.role,
            "reachable": self.reachable,
            "instructions": len(self.opcodes),
            "opcodes": list(self.opcodes),
        }


@dataclass
class _Cfg:
    blocks: list[_Block] = field(default_factory=list)
    edges: list[dict[str, str]] = field(default_factory=list)

    def new_block(self, role: str, *, reachable: bool) -> str:
        identifier = f"b{len(self.blocks)}"
        self.blocks.append(_Block(identifier, role, reachable))
        return identifier

    def block(self, identifier: str) -> _Block:
        return self.blocks[int(identifier[1:])]

    def edge(self, source: str, target: str, kind: str) -> None:
        self.edges.append({"source": source, "target": target, "kind": kind})


@dataclass(frozen=True)
class _Span:
    source_index: int
    start_byte: int
    end_byte: int
    comment_offset: int

    def as_dict(self, files: dict[int, str]) -> dict[str, Any]:
        return {
            "source_index": self.source_index,
            "source_path": files.get(self.source_index),
            "start_byte": self.start_byte,
            "end_byte": self.end_byte,
        }


def analyze_wir(wir: str, llvm_ir: str = "") -> dict[str, Any]:
    """Return a stable normalized analysis of WIR and its LLVM correspondence."""
    if not wir:
        return _failure("WIR artifact is unavailable", available=False, llvm_ir=llvm_ir)
    try:
        document = parse_wir(wir)
    except WirSyntaxError as exc:
        return _failure(str(exc), available=True, llvm_ir=llvm_ir)

    module, core_version, envelope_failure = _module(document)
    if module is None or core_version is None:
        return _failure(
            envelope_failure or "invalid WIR module envelope",
            available=True,
            llvm_ir=llvm_ir,
            comments=document.comments,
        )

    files, spans, malformed = _provenance(document.comments)
    span_assignments, unmatched = _assign_spans(module, spans)
    malformed.extend(unmatched)
    declarations_form = _unique_child(module, "decls")
    assert declarations_form is not None
    declarations = [
        item for item in declarations_form.items[1:] if isinstance(item, WirList)
    ]
    declaration_records = [_declaration_record(item) for item in declarations]
    names = [
        str(record["name"])
        for record in declaration_records
        if isinstance(record.get("name"), str)
    ]
    duplicates = sorted(name for name, count in Counter(names).items() if count > 1)
    declared_names = set(names)
    functions: dict[str, dict[str, Any]] = {}
    all_unresolved: set[str] = set()
    all_anonymous: set[str] = set()
    aggregate_opcodes: Counter[str] = Counter()
    aggregate_types: Counter[str] = Counter()
    metrics: Counter[str] = Counter()
    metrics["declarations"] = len(declaration_records)
    metrics["duplicate_declarations"] = len(duplicates)
    metrics["malformed_provenance"] = len(malformed)
    metrics["provenance_files"] = len(files)
    metrics["provenance_spans"] = len(spans)

    for declaration, record in zip(declarations, declaration_records, strict=True):
        kind = record.get("kind")
        if kind == "extern":
            metrics["externs"] += 1
        elif kind == "fn":
            metrics["functions"] += 1
            name = record.get("name")
            if isinstance(name, str) and name not in functions:
                function = _analyze_function(
                    declaration,
                    declared_names=declared_names,
                    files=files,
                    span_assignments=span_assignments,
                )
                functions[name] = function
                _merge_function_metrics(metrics, function)
                aggregate_opcodes.update(_int_mapping(function.get("opcodes")))
                aggregate_types.update(_int_mapping(function.get("types")))
                all_unresolved.update(_string_list(function.get("unresolved_symbols")))
                all_anonymous.update(
                    _string_list(function.get("anonymous_identifiers"))
                )
        else:
            metrics["unknown_declarations"] += 1

        name = record.get("name")
        if not isinstance(name, str) or _is_anonymous(name):
            all_anonymous.add(
                name if isinstance(name, str) else "<missing-declaration-name>"
            )

    metrics["anonymous_identifiers"] = len(all_anonymous)
    metrics["unresolved_symbols"] = len(all_unresolved)
    metrics["mapped_functions"] = sum(
        1 for function in functions.values() if function["provenance"]["spans"]
    )
    metrics["mapped_instructions"] = sum(
        int(function["provenance"]["mapped_instructions"])
        for function in functions.values()
    )
    cross_stage = _cross_stage(functions, declaration_records, llvm_ir)
    return {
        "format": WIR_ANALYSIS_FORMAT,
        "available": True,
        "valid": True,
        "failure_reason": None,
        "core_version": core_version,
        "metrics": {key: metrics.get(key, 0) for key in _METRIC_KEYS},
        "opcodes": dict(sorted(aggregate_opcodes.items())),
        "types": dict(sorted(aggregate_types.items())),
        "declarations": declaration_records,
        "duplicate_declarations": duplicates,
        "anonymous_identifiers": sorted(all_anonymous),
        "unresolved_symbols": sorted(all_unresolved),
        "functions": dict(sorted(functions.items())),
        "call_graph": {
            name: list(function["calls"])
            for name, function in sorted(functions.items())
        },
        "provenance": {
            "files": [
                {"index": index, "path": path} for index, path in sorted(files.items())
            ],
            "spans": [span.as_dict(files) for span in spans],
            "malformed": sorted(malformed),
        },
        "cross_stage": cross_stage,
    }


def _failure(
    reason: str,
    *,
    available: bool,
    llvm_ir: str,
    comments: tuple[WirComment, ...] = (),
) -> dict[str, Any]:
    files, spans, malformed = _provenance(comments)
    cross_stage = _cross_stage({}, [], llvm_ir)
    return {
        "format": WIR_ANALYSIS_FORMAT,
        "available": available,
        "valid": False,
        "failure_reason": reason,
        "core_version": None,
        "metrics": {
            key: (
                len(files)
                if key == "provenance_files"
                else len(spans)
                if key == "provenance_spans"
                else len(malformed)
                if key == "malformed_provenance"
                else 0
            )
            for key in _METRIC_KEYS
        },
        "opcodes": {},
        "types": {},
        "declarations": [],
        "duplicate_declarations": [],
        "anonymous_identifiers": [],
        "unresolved_symbols": [],
        "functions": {},
        "call_graph": {},
        "provenance": {
            "files": [
                {"index": index, "path": path} for index, path in sorted(files.items())
            ],
            "spans": [span.as_dict(files) for span in spans],
            "malformed": sorted(malformed),
        },
        "cross_stage": cross_stage,
    }


def _module(document: WirDocument) -> tuple[WirList | None, int | None, str | None]:
    if len(document.expressions) != 1:
        return None, None, "WIR must contain exactly one top-level expression"
    root = document.expressions[0]
    if not isinstance(root, WirList) or head(root) != "core-module":
        return None, None, "WIR root must be core-module"
    versions = _children(root, "core-version")
    if len(versions) != 1:
        return None, None, "WIR must contain exactly one core-version declaration"
    values = [atom_text(item) for item in versions[0].items[1:]]
    supported = describe_supported_core_versions()
    if len(values) != 1 or values[0] is None or not values[0].isdigit():
        return (
            None,
            None,
            f"WIR core-version must contain a single integer token, one of {supported}",
        )
    version = int(values[0])
    if version not in SUPPORTED_CORE_VERSIONS:
        return (
            None,
            None,
            f"WIR core version {version} is unsupported, expected {supported}",
        )
    declarations = _children(root, "decls")
    if len(declarations) != 1:
        return None, None, "WIR must contain exactly one decls form"
    return root, version, None


def _children(expression: WirList, name: str) -> list[WirList]:
    return [
        child
        for child in expression.items[1:]
        if isinstance(child, WirList) and head(child) == name
    ]


def _unique_child(expression: WirList, name: str) -> WirList | None:
    children = _children(expression, name)
    return children[0] if len(children) == 1 else None


def _declaration_record(declaration: WirList) -> dict[str, Any]:
    kind = head(declaration) or "<missing>"
    name = atom_text(declaration.items[1]) if len(declaration.items) > 1 else None
    params = _parameters(_unique_child(declaration, "params"))
    returns = _returns(_unique_child(declaration, "returns"))
    return {
        "kind": kind,
        "name": name,
        "params": params,
        "returns": returns,
    }


def _parameters(expression: WirList | None) -> list[dict[str, str | None]]:
    if expression is None:
        return []
    result: list[dict[str, str | None]] = []
    for item in expression.items[1:]:
        if not isinstance(item, WirList):
            continue
        name = atom_text(item.items[0]) if item.items else None
        type_name = atom_text(item.items[1]) if len(item.items) > 1 else None
        result.append({"name": name, "type": type_name})
    return result


def _returns(expression: WirList | None) -> list[str]:
    if expression is None:
        return []
    return [
        value for item in expression.items[1:] if (value := atom_text(item)) is not None
    ]


def _analyze_function(
    declaration: WirList,
    *,
    declared_names: set[str],
    files: dict[int, str],
    span_assignments: dict[int, _Span],
) -> dict[str, Any]:
    params = _parameters(_unique_child(declaration, "params"))
    returns = _returns(_unique_child(declaration, "returns"))
    param_names = {
        str(item["name"]) for item in params if isinstance(item.get("name"), str)
    }
    body = _unique_child(declaration, "do")
    cfg = _Cfg()
    entry = cfg.new_block("entry", reachable=True)
    if body is not None:
        _build_do(body, cfg, entry)
    opcodes: Counter[str] = Counter()
    types = Counter(type_name for type_name in returns if type_name)
    calls: list[str] = []
    locals_found: list[str] = []
    unresolved: set[str] = set()
    anonymous: set[str] = set()
    operands = 0
    returns_count = 0
    branches = 0
    loops = 0
    semantic_nodes = _semantic_nodes(body) if body is not None else []
    for node in semantic_nodes:
        opcode = head(node)
        if opcode is None:
            continue
        opcodes[opcode] += 1
        operands += max(0, len(node.items) - 1)
        types.update(_types_from_node(node))
        if _CALL_HEAD.match(opcode):
            target = atom_text(node.items[1]) if len(node.items) > 1 else None
            if target is None:
                unresolved.add("call:<missing-target>")
            else:
                calls.append(target)
                if target not in declared_names:
                    unresolved.add(f"call:{target}")
        if opcode == "let":
            local_name = atom_text(node.items[1]) if len(node.items) > 1 else None
            if local_name is None:
                anonymous.add("<missing-local-name>")
            else:
                locals_found.append(local_name)
                if _is_anonymous(local_name):
                    anonymous.add(local_name)
        if opcode in {"local_get", "set"}:
            local_name = atom_text(node.items[1]) if len(node.items) > 1 else None
            if local_name is None or local_name not in set(locals_found):
                unresolved.add(f"local:{local_name or '<missing>'}")
        if opcode == "param_get":
            param_name = atom_text(node.items[1]) if len(node.items) > 1 else None
            if param_name is None or param_name not in param_names:
                unresolved.add(f"param:{param_name or '<missing>'}")
        if opcode in {"return", "return_void"}:
            returns_count += 1
        if opcode == "if":
            branches += 1
        if opcode == "while":
            branches += 1
            loops += 1

    for parameter in params:
        parameter_name = parameter.get("name")
        type_name = parameter.get("type")
        if isinstance(parameter_name, str) and _is_anonymous(parameter_name):
            anonymous.add(parameter_name)
        if isinstance(type_name, str):
            types[type_name] += 1
    duplicate_locals = sorted(
        local for local, count in Counter(locals_found).items() if count > 1
    )
    unresolved.update(f"duplicate-local:{name}" for name in duplicate_locals)
    function_spans = [
        span
        for node in _lists_within(declaration)
        if (span := span_assignments.get(id(node))) is not None
    ]
    mapped_instructions = sum(
        1 for node in semantic_nodes if id(node) in span_assignments
    )
    unreachable_blocks = sum(1 for block in cfg.blocks if not block.reachable)
    unreachable_instructions = sum(
        len(block.opcodes) for block in cfg.blocks if not block.reachable
    )
    return {
        "params": params,
        "returns": returns,
        "metrics": {
            "blocks": len(cfg.blocks),
            "reachable_blocks": len(cfg.blocks) - unreachable_blocks,
            "unreachable_blocks": unreachable_blocks,
            "unreachable_instructions": unreachable_instructions,
            "control_flow_edges": len(cfg.edges),
            "backedges": sum(1 for edge in cfg.edges if edge["kind"] == "backedge"),
            "instructions": len(semantic_nodes),
            "operands": operands,
            "calls": len(calls),
            "branches": branches,
            "loops": loops,
            "returns": returns_count,
            "locals": len(locals_found),
        },
        "opcodes": dict(sorted(opcodes.items())),
        "types": dict(sorted(types.items())),
        "calls": sorted(calls),
        "locals": sorted(locals_found),
        "duplicate_locals": duplicate_locals,
        "anonymous_identifiers": sorted(anonymous),
        "unresolved_symbols": sorted(unresolved),
        "blocks": [block.as_dict() for block in cfg.blocks],
        "edges": sorted(
            cfg.edges,
            key=lambda edge: (edge["source"], edge["target"], edge["kind"]),
        ),
        "provenance": {
            "spans": _unique_spans(function_spans, files),
            "mapped_instructions": mapped_instructions,
        },
    }


def _build_do(expression: WirList, cfg: _Cfg, start: str | None) -> str | None:
    current = start
    for statement in expression.items[1:]:
        if not isinstance(statement, WirList):
            continue
        if current is None:
            current = cfg.new_block("unreachable", reachable=False)
        opcode = head(statement)
        if opcode == "if":
            current = _build_if(statement, cfg, current)
            continue
        if opcode == "while":
            current = _build_while(statement, cfg, current)
            continue
        if opcode == "do":
            current = _build_do(statement, cfg, current)
            continue
        cfg.block(current).opcodes.extend(_statement_opcodes(statement))
        if _guaranteed_terminates(statement):
            current = None
    return current


def _build_if(expression: WirList, cfg: _Cfg, source: str) -> str | None:
    cfg.block(source).opcodes.extend(_control_opcodes(expression, "if"))
    then_body = _nested_do(expression, "then")
    else_body = _nested_do(expression, "else")
    then_block = cfg.new_block("if-then", reachable=cfg.block(source).reachable)
    else_block = cfg.new_block("if-else", reachable=cfg.block(source).reachable)
    cfg.edge(source, then_block, "if-true")
    cfg.edge(source, else_block, "if-false")
    then_exit = _build_do(then_body, cfg, then_block) if then_body else then_block
    else_exit = _build_do(else_body, cfg, else_block) if else_body else else_block
    fallthrough = [value for value in (then_exit, else_exit) if value is not None]
    if not fallthrough:
        return None
    merge = cfg.new_block(
        "if-merge",
        reachable=any(cfg.block(value).reachable for value in fallthrough),
    )
    for value in fallthrough:
        cfg.edge(value, merge, "fallthrough")
    return merge


def _build_while(expression: WirList, cfg: _Cfg, source: str) -> str:
    condition = cfg.new_block("while-condition", reachable=cfg.block(source).reachable)
    cfg.edge(source, condition, "fallthrough")
    cfg.block(condition).opcodes.extend(_control_opcodes(expression, "while"))
    body = cfg.new_block("while-body", reachable=cfg.block(condition).reachable)
    after = cfg.new_block("while-exit", reachable=cfg.block(condition).reachable)
    cfg.edge(condition, body, "while-true")
    cfg.edge(condition, after, "while-false")
    body_expression = _unique_child(expression, "do")
    body_exit = _build_do(body_expression, cfg, body) if body_expression else body
    if body_exit is not None:
        cfg.edge(body_exit, condition, "backedge")
    return after


def _nested_do(expression: WirList, wrapper: str) -> WirList | None:
    container = _unique_child(expression, wrapper)
    return _unique_child(container, "do") if container is not None else None


def _statement_opcodes(expression: WirList) -> list[str]:
    result: list[str] = []
    for node in _lists_within(expression):
        opcode = head(node)
        if opcode is not None and opcode not in _WRAPPERS:
            result.append(opcode)
    return result


def _control_opcodes(expression: WirList, opcode: str) -> list[str]:
    result = [opcode]
    condition = _unique_child(expression, "condition")
    if condition is not None:
        for node in _lists_within(condition):
            nested = head(node)
            if nested is not None and nested not in _WRAPPERS:
                result.append(nested)
    return result


def _guaranteed_terminates(expression: WirList) -> bool:
    opcode = head(expression)
    if opcode in {"return", "return_void"}:
        return True
    if opcode == "do":
        return any(
            _guaranteed_terminates(item)
            for item in expression.items[1:]
            if isinstance(item, WirList)
        )
    if opcode != "if":
        return False
    then_body = _nested_do(expression, "then")
    else_body = _nested_do(expression, "else")
    return (
        then_body is not None
        and else_body is not None
        and _guaranteed_terminates(then_body)
        and _guaranteed_terminates(else_body)
    )


def _semantic_nodes(expression: WirList | None) -> list[WirList]:
    if expression is None:
        return []
    return [
        node
        for node in _lists_within(expression)
        if (opcode := head(node)) is not None and opcode not in _WRAPPERS
    ]


def _lists_within(expression: WirList) -> list[WirList]:
    return [node for node in walk(expression) if isinstance(node, WirList)]


def _types_from_node(expression: WirList) -> Counter[str]:
    values: Counter[str] = Counter()
    opcode = head(expression) or ""
    for part in opcode.split("_"):
        if part in _KNOWN_TYPES:
            values[part] += 1
    if opcode == "let" and len(expression.items) > 2:
        type_name = atom_text(expression.items[2])
        if type_name:
            values[type_name] += 1
    return values


def _merge_function_metrics(metrics: Counter[str], function: dict[str, Any]) -> None:
    function_metrics = _int_mapping(function.get("metrics"))
    for name in (
        "blocks",
        "reachable_blocks",
        "unreachable_blocks",
        "control_flow_edges",
        "backedges",
        "instructions",
        "operands",
        "calls",
        "branches",
        "loops",
        "returns",
        "locals",
    ):
        metrics[name] += function_metrics.get(name, 0)


def _provenance(
    comments: tuple[WirComment, ...],
) -> tuple[dict[int, str], list[_Span], list[str]]:
    files: dict[int, str] = {}
    spans: list[_Span] = []
    malformed: list[str] = []
    for comment in comments:
        if comment.text.startswith("weavec-source-file-v1"):
            match = _FILE_COMMENT.fullmatch(comment.text)
            if match is None:
                malformed.append(f"line {comment.line}: malformed source-file record")
                continue
            index = int(match.group(1))
            try:
                path = json.loads(match.group(2))
            except json.JSONDecodeError:
                malformed.append(f"line {comment.line}: invalid source-file string")
                continue
            if index in files:
                malformed.append(f"line {comment.line}: duplicate source index {index}")
            elif isinstance(path, str):
                files[index] = path
            continue
        if comment.text.startswith("weavec-source-span-v1"):
            match = _SPAN_COMMENT.fullmatch(comment.text)
            if match is None:
                malformed.append(f"line {comment.line}: malformed source-span record")
                continue
            source_index, start_byte, end_byte = map(int, match.groups())
            if end_byte < start_byte:
                malformed.append(f"line {comment.line}: reversed source span")
                continue
            spans.append(_Span(source_index, start_byte, end_byte, comment.end))
    for span in spans:
        if span.source_index not in files:
            malformed.append(
                f"span {span.start_byte}..{span.end_byte}: unknown source index "
                f"{span.source_index}"
            )
    return files, spans, malformed


def _assign_spans(
    module: WirList,
    spans: list[_Span],
) -> tuple[dict[int, _Span], list[str]]:
    semantic = sorted(
        (
            node
            for node in _lists_within(module)
            if (opcode := head(node)) is not None
            and opcode not in {"core-module", "core-version", "decls"}
        ),
        key=_head_offset,
    )
    assignments: dict[int, _Span] = {}
    unmatched: list[str] = []
    cursor = 0
    for span in sorted(spans, key=lambda item: item.comment_offset):
        while (
            cursor < len(semantic)
            and _head_offset(semantic[cursor]) < span.comment_offset
        ):
            cursor += 1
        if cursor >= len(semantic):
            unmatched.append(
                f"span {span.start_byte}..{span.end_byte}: no following WIR form"
            )
            continue
        assignments[id(semantic[cursor])] = span
        cursor += 1
    return assignments, unmatched


def _head_offset(expression: WirList) -> int:
    if expression.items and isinstance(expression.items[0], WirAtom):
        return expression.items[0].start
    return expression.start


def _unique_spans(spans: list[_Span], files: dict[int, str]) -> list[dict[str, Any]]:
    unique = {
        (span.source_index, span.start_byte, span.end_byte): span for span in spans
    }
    return [
        unique[key].as_dict(files)
        for key in sorted(unique, key=lambda item: (item[0], item[1], item[2]))
    ]


def _cross_stage(
    functions: dict[str, dict[str, Any]],
    declarations: list[dict[str, Any]],
    llvm_ir: str,
) -> dict[str, Any]:
    llvm = _llvm_functions(llvm_ir)
    wir_functions = set(functions)
    wir_externs = {
        str(item["name"])
        for item in declarations
        if item.get("kind") == "extern" and isinstance(item.get("name"), str)
    }
    llvm_definitions = set(llvm["definitions"])
    llvm_declarations = set(llvm["declarations"])
    missing_definitions = sorted(wir_functions - llvm_definitions)
    unexpected_definitions = sorted(llvm_definitions - wir_functions)
    missing_externs = sorted(wir_externs - llvm_declarations - llvm_definitions)
    correspondence: dict[str, dict[str, Any]] = {}
    llvm_blocks = _int_mapping(llvm.get("blocks"))
    for name, function in sorted(functions.items()):
        wir_blocks = int(_int_mapping(function.get("metrics")).get("blocks", 0))
        lowered_blocks = llvm_blocks.get(name)
        correspondence[name] = {
            "wir_blocks": wir_blocks,
            "llvm_blocks": lowered_blocks,
            "block_delta": (
                lowered_blocks - wir_blocks if lowered_blocks is not None else None
            ),
        }
    return {
        "wir_functions": sorted(wir_functions),
        "wir_externs": sorted(wir_externs),
        "llvm_definitions": sorted(llvm_definitions),
        "llvm_declarations": sorted(llvm_declarations),
        "missing_definitions": missing_definitions,
        "unexpected_definitions": unexpected_definitions,
        "missing_externs": missing_externs,
        "duplicate_llvm_definitions": llvm["duplicate_definitions"],
        "duplicate_llvm_declarations": llvm["duplicate_declarations"],
        "metrics": {
            "missing_definitions": len(missing_definitions),
            "unexpected_definitions": len(unexpected_definitions),
            "missing_externs": len(missing_externs),
            "duplicate_llvm_definitions": len(llvm["duplicate_definitions"]),
            "duplicate_llvm_declarations": len(llvm["duplicate_declarations"]),
        },
        "functions": correspondence,
    }


def _llvm_functions(llvm_ir: str) -> dict[str, Any]:
    definitions: list[str] = []
    declarations: list[str] = []
    blocks: Counter[str] = Counter()
    current: str | None = None
    current_blocks = 0
    current_has_content = False
    for line in llvm_ir.splitlines():
        match = _LLVM_FUNCTION.match(line)
        if match is not None:
            kind, raw_name = match.groups()
            name = _llvm_name(raw_name)
            if kind == "declare":
                declarations.append(name)
            else:
                definitions.append(name)
                current = name
                current_blocks = 0
                current_has_content = False
            continue
        if current is None:
            continue
        stripped = line.strip()
        if stripped == "}":
            blocks[current] = max(1 if current_has_content else 0, current_blocks)
            current = None
            continue
        if not stripped or stripped.startswith(";"):
            continue
        current_has_content = True
        if _LLVM_LABEL.match(line):
            current_blocks += 1
    definition_counts = Counter(definitions)
    declaration_counts = Counter(declarations)
    return {
        "definitions": sorted(definition_counts),
        "declarations": sorted(declaration_counts),
        "duplicate_definitions": sorted(
            name for name, count in definition_counts.items() if count > 1
        ),
        "duplicate_declarations": sorted(
            name for name, count in declaration_counts.items() if count > 1
        ),
        "blocks": dict(sorted(blocks.items())),
    }


def _llvm_name(value: str) -> str:
    if value.startswith('"'):
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError:
            return value
        return decoded if isinstance(decoded, str) else value
    return value


def _is_anonymous(name: str) -> bool:
    return bool(_ANONYMOUS_NAME.fullmatch(name))


def _int_mapping(value: object) -> dict[str, int]:
    if not isinstance(value, dict):
        return {}
    return {
        str(key): item
        for key, item in value.items()
        if isinstance(item, int) and not isinstance(item, bool)
    }


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]
