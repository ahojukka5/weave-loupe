# Deterministic WIR structural analysis

Weave Loupe treats WIR as a first-class compiler stage between source parsing
and LLVM lowering, and reads every published core version -- currently 2 and 3
(`SUPPORTED_CORE_VERSIONS` in `wir_syntax.py`). The normalized analysis format is
`weave-loupe-wir-analysis-v1`.

Loupe never rewrites the WIR stored in a `.loupe` bundle. The exact compiler
artifact and SHA-256 identity remain authoritative. Structural analysis is a
derived, reproducible view that can be regenerated from those bytes.

## Accepted module envelope

The analyzer expects the public core envelope, with `core-version` naming any
supported version (2 or 3):

```lisp
(core-module
  (core-version 2)
  (decls
    ...))
```

Malformed S-expressions, unsupported core versions, multiple top-level forms,
or missing/duplicate envelope forms produce an explicit invalid analysis with a
stable failure reason. Missing WIR is reported separately from malformed WIR.

The positional parser preserves quoted atoms, source offsets, and semicolon
comments. The human-readable audit projection and structural analyzer use this
same parser so formatting and analysis cannot drift.

## Normalized declarations and functions

The model records functions, extern declarations, parameter names and types,
return types, typed operations, operands, calls, local bindings, and deterministic
call graphs. It reports added and removed functions explicitly in v2 bundle
diffs instead of relying on aggregate count changes.

For each function Loupe derives structured blocks from `do`, `if`, and
`while` forms. Blocks receive stable local identifiers (`b0`, `b1`, ...), roles,
reachability, ordered opcode lists, and normalized control-flow edges. Loop edges
are identified as backedges.

WIR blocks are a deterministic analysis projection, not LLVM basic blocks. A
structured `if` or `while` may lower into a different LLVM block count. Loupe
therefore reports the two counts and their delta rather than requiring equality.

## Stable metrics

The analysis publishes stable counts for:

- declarations, functions, externs, and unknown declarations;
- structured blocks, reachable and unreachable blocks, edges, and backedges;
- semantic instructions, operands, calls, branches, loops, returns, and locals;
- opcode and type frequencies;
- anonymous identifiers, duplicate declarations, and unresolved symbols;
- source files, source spans, functions with provenance, and mapped operations;
- missing, unexpected, or duplicate WIR-to-LLVM function correspondence.

Structural wrappers such as `do`, `condition`, `then`, and `else` are not counted
as semantic instructions. This keeps metrics tied to compiler operations rather
than presentation nesting.

## Findings

Loupe reports suspicious WIR facts without guessing repairs:

- duplicate declarations and duplicate local bindings;
- unresolved call targets, parameters, or local references;
- anonymous or generated-looking identifiers;
- blocks and operations made unreachable by structured termination;
- malformed, reversed, duplicate, unknown-source, or unmatched provenance
  records;
- WIR functions missing from raw LLVM, unexpected LLVM definitions, missing
  extern declarations, and duplicate LLVM symbols.

These findings are deterministic facts. `loupe diff` remains observational and
shows classified changes. `loupe compiler-audit` applies policy and can fail the
candidate.

## Source provenance

The analyzer consumes the public comments emitted by `weavec`:

```text
; weavec-source-file-v1 <source-index> "<path>"
; weavec-source-span-v1 <source-index> <start-byte> <end-byte>
```

File records and byte spans are normalized in source order. A span is associated
with the next WIR form following its comment. Function summaries include unique
source spans and a mapped-operation count. Malformed or unassignable records are
retained as explicit evidence findings.

## Diff and HTML behavior

The default `weave-loupe-diff-v2` output places `analysis.wir` before raw LLVM.
WIR changes enter the same globally sorted change list used by the rest of the
compiler evidence chain. They use the existing classifications:

- `semantic` for function, call-graph, and lowering-correspondence changes;
- `quality` for structural metrics and suspicious findings;
- `provenance` for source mapping changes;
- `evidence` for validity, availability, and malformed-provenance changes.

HTML reports add WIR navigation, metric tables, function additions/removals,
provenance, and WIR-to-LLVM correspondence. The v1 comparison format remains
unchanged and contains no WIR section.

## Compiler-audit defaults

Unless a versioned policy overrides a path, compiler-audit permits decreases but
rejects positive deltas for:

```text
analysis.wir.metrics.unreachable_blocks
analysis.wir.metrics.unresolved_symbols
analysis.wir.metrics.anonymous_identifiers
analysis.wir.metrics.malformed_provenance
analysis.wir.cross_stage.metrics.missing_definitions
analysis.wir.cross_stage.metrics.unexpected_definitions
analysis.wir.cross_stage.metrics.missing_externs
analysis.wir.cross_stage.metrics.duplicate_llvm_definitions
analysis.wir.cross_stage.metrics.duplicate_llvm_declarations
```

An invalid baseline WIR is an infrastructure failure because no trustworthy
reference exists. A valid baseline followed by an invalid candidate WIR is a
semantic regression. Optional model review runs only after these deterministic
facts and failures have been assembled and cannot waive them.

Projects may loosen a numeric limit through the normal versioned compiler-audit
policy when a reviewed transformation intentionally changes one of these metrics.
The explicit WIR validity gate cannot be converted into a model-only decision.
