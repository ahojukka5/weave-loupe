# Architecture-aware native analysis

Loupe analyzes the linked executable rather than assuming optimized LLVM predicts
the final machine code. Disassembly syntax and instruction meaning vary by target,
so native analysis first normalizes each supported architecture into one stable
control-flow model.

## Supported architectures

The `weave-loupe-native-disassembly-v1` parser supports:

- x86-64; and
- AArch64, including Linux and macOS arm64 output.

The parser accepts common GNU `objdump` and LLVM `llvm-objdump` layouts. Raw
instruction bytes may be rendered as separated byte pairs, one encoded instruction
word, or omitted entirely. Function headers and instruction addresses remain the
required structural anchors.

An architecture is selected from available evidence in this order without blindly
trusting only one source:

- an explicit library argument;
- the optimized LLVM target triple;
- the disassembly object or architecture header; and
- characteristic instruction syntax as a fallback.

Independent evidence must agree. A conflicting LLVM triple and disassembly header
produce an unsupported result rather than metrics for the wrong instruction set.
An unknown architecture also produces an explicit unsupported result; Loupe never
substitutes zero-valued native metrics.

## Normalized instruction semantics

Architecture-specific classifiers map instructions to stable categories:

- direct and indirect calls;
- conditional and unconditional branches;
- direct and indirect branches;
- returns;
- padding; and
- ordinary non-control instructions.

A direct branch whose destination address is lower than its own address is counted
as a backward edge. Conditional backward edges are reported separately because
native budgets use them to preserve required loops.

For x86-64, the parser recognizes `call*`, direct and indirect `jmp*`, conditional
`j*` and `loop*` families, return variants, and common NOP or trap padding. For
AArch64 it recognizes `bl` and `blr` call families, `b`, `br`, `b.<cond>`, `cbz`,
`cbnz`, `tbz`, and `tbnz` branches, authenticated branch and return forms, `ret`,
and `nop`.

Numeric direct-call destinations are resolved through parsed function addresses.
This preserves the call graph when a disassembler omits the symbolic `<target>`
annotation.

## Symbol identities

Loupe removes display-only function offsets such as `+0x20` and normalizes the
case of the `@plt` suffix. On Mach-O, one ABI leading underscore is removed from
public C symbols, so `_main` and `_fib` correspond to LLVM `main` and `fib`.

Compiler-created suffixes such as `.cold` and `.llvm.123` are retained because they
may identify distinct functions. If two raw symbols would collapse to one public
identity, parsing fails closed with a normalization-collision error instead of
merging their instructions.

## Analysis evidence

The native section of `weave-loupe-analysis-v1` records:

- `supported` and `failure_reason`;
- normalized `architecture`;
- `object_format` (`elf`, `macho`, `coff`, or `unknown`);
- `disassembler` and `disassembler_version` when available;
- `parser_format`;
- program-owned, reachable, and unreachable functions;
- indirect-call and reachability completeness;
- per-function instruction, padding, call, branch, backedge, and return metrics.

Disassembler identity is read from the compiler build manifest when present. A
recognizable header in the disassembly is used as a fallback. Missing tool identity
does not invalidate otherwise unambiguous instructions, but it remains visible as
`unknown` in the evidence.

## Fail-closed budgets

A configured native budget requires supported disassembly and complete
program-function reachability. Missing disassembly, an unsupported or conflicting
architecture, a symbol collision, an unparseable function layout, or reachable
indirect calls prevents the budget from passing.

This distinction matters for new systems: a RISC-V or other unknown target is not
reported as having zero instructions or zero loops. It is reported as unsupported
until a target-specific classifier and verified golden fixtures are added.

## Golden portability fixtures

The test corpus contains equivalent programs represented as:

- GNU x86-64 ELF disassembly;
- GNU AArch64 ELF disassembly; and
- LLVM arm64 Mach-O disassembly.

All three must produce the same normalized call graph, direct and indirect call
counts, loop backedge, return count, padding count, and reachability result. Extra
fixtures cover AArch64 multi-operand conditional branches, numeric call targets,
metadata precedence, unknown architectures, conflicting evidence, and symbol
normalization collisions.
