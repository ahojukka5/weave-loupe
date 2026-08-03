# Audit corpus

This directory contains small, reviewable Weave programs and the reports generated
for them by the pull-request audit gate.

Each source, audit sidecar, and report are kept together:

- `fibonacci.weave` — constant-folding and minimal native output
- `fibonacci_runtime.weave` — input-dependent loops and external calls
- `function_chain.weave` — multi-function calls and integer arithmetic
- `memory_flow.weave` — heap allocation, pointer arithmetic, loads, and stores
- `module_import.weave` plus `module_math.weave` — explicit module linking
- adjacent `*.audit.json` files — versioned deterministic expectations
- adjacent `*.audit.sources` files — ordered multi-source compiler inputs
- adjacent `*.md` files — workflow-generated reports after passing verdicts

## Coverage matrix

| Case | Primary coverage | Deterministic assertions |
|---|---|---|
| `fibonacci` | constant folding, function calls, optimized/native minima | exit 55 plus exact LLVM and native budgets |
| `fibonacci_runtime` | environment input, comparisons, loop phis, extern ABI | nine runtime cases plus LLVM and native budgets |
| `function_chain` | three-function call graph, parameters, add and multiply | linked executable exits 35 with empty output |
| `memory_flow` | malloc/free ABI, pointer offsets, i32 loads and stores, loops | linked executable exits 100 with empty output |
| `module_import` | two source modules, explicit export/import, linking | ordered two-source build exits 42 with empty output |

The audit sidecar is optional. It may contain runtime cases, an optimized LLVM
contract, a native optimization contract, or any combination. Runtime cases
execute the exact linked artifact with declared inputs and expected results. The
LLVM contract bounds the exact post-optimization module and can require functions
and call targets. Native contracts bound linked function counts, instructions,
padding, calls, and loop backedges.

A multi-source case adds an adjacent `NAME.audit.sources` manifest. It contains
one relative `.weave` path per line in compiler input order, with `NAME.weave`
first. Empty lines and lines beginning with `#` are ignored. Paths must remain
inside the manifest directory. Changing any listed source, the runtime sidecar,
the source-set manifest, or the generated report re-audits the complete set and
publishes one report beside the primary source.

Observed runtime mismatches, optimized-IR contract violations, exceeded native
limits, unmet structural minima, or missing required dependencies deterministically
fail the gate even when the model returns `OK`. Evaluation fails closed when a
required artifact or complete native reachability is unavailable.

Generated reports are workflow-owned evidence, not hand-maintained prose. Change
the `.weave` source, its optional `.audit.json` sidecar or `.audit.sources`
manifest, or the audit implementation instead of editing the adjacent report
directly. A pull request that changes or deletes `foo.md` automatically re-audits
the complete source set and replaces the report with fresh evidence after a
passing verdict. Ordinary corpus documentation such as this README has no
adjacent source and skips compiler and LLM setup.

The workflow runs `loupe audit --verbose`, so every generated report includes the
complete source-to-native evidence chain:

1. Weave source
2. readable WIR with provenance comments hidden
3. raw LLVM IR
4. optimized LLVM IR
5. optimized LLVM contract and observed metrics
6. target assembly
7. linked executable disassembly
8. LLVM optimization remarks
9. native optimization contract and observed metrics
10. native runtime execution matrix
11. diagnostics and deterministic analysis
12. build manifest and compiler trace

The constant Fibonacci optimized module must be exactly one defined `main`, one
basic block, and one return instruction with no memory traffic, calls, branches,
phi nodes, identity additions, undef, or poison. Its linked native contract then
requires one two-instruction `main`, no calls, no dead code, and no loop backedges.

The runtime-input optimized module must remain a memory-free SSA loop in one
`main`, with bounded blocks and instructions, phi nodes, branches, recurrence
arithmetic, and exactly two calls to `getenv` and `atoi`. Its native contract
requires exactly one backward conditional branch and direct calls to
`getenv@plt` and `atoi@plt`, forbids indirect calls and dead program functions,
and bounds instructions and padding. Nine runtime cases independently verify
observable behavior.

The function-chain case keeps three source functions reviewable before
optimization and verifies their assembled behavior with an exact process result.
It intentionally avoids a brittle post-optimization instruction budget because
whole-program inlining and constant folding may erase the helper boundaries.

The memory-flow case exercises both writes and reads through computed byte
offsets. Its exact runtime result catches pointer scaling, loop, load/store, call,
and allocation-lifetime regressions without depending on target-specific
instruction counts.

The module-import case places the application before its dependency in compiler
input order. The compiler must collect both module interfaces, resolve the
explicit import and export, link the call, and produce the exact result without
depending on filenames or ambient symbol visibility.

The report also records the exact source, Loupe, and weavec commits, compiler and
artifact hashes, sidecar and executable hashes, model request and provider
provenance, timestamp, operating system, CPU, memory, Python, and libc. This makes
the verdict independently inspectable rather than treating it as an opaque
approval.

Check an existing report without compiling or contacting the model:

```sh
uv run loupe verify-report docs/audit/fibonacci.md \
  --weavec /path/to/weavec
```

A valid report returns `0`; a stale report returns `2` and lists every changed
input, compiler, auditor, identity, or age condition.
