# Canonical compiler audit coverage matrix

This matrix records the complete issue #45 corpus against the stable Weave
surface available when the corpus was completed. Each case has one primary
purpose and an adjacent deterministic runtime or failure contract.

| Required area | Canonical source(s) | Deterministic assertion |
|---|---|---|
| Integer arithmetic, comparison, narrowing, and overflow | `integer_edges.weave` | exits 42 and rejects optimized LLVM `undef` or `poison` |
| Floating arithmetic, comparison, and conversion | `floating_arithmetic.weave` | exits 42 and rejects optimized LLVM `undef` or `poison` |
| Branches, nested loops, early returns, Boolean conjunction, and loop-carried phis | `nested_control_flow.weave` | six input-dependent cases distinguish first/last hits, absent cells, and rejected bounds |
| Function calls and parameter passing | `function_chain.weave` | linked three-function call graph exits 35 |
| Input-dependent loops and external ABI calls | `fibonacci_runtime.weave` | nine environment-driven executions plus LLVM and native budgets |
| Recursion and call/return behavior | `recursive_factorial.weave` | eight base, recursive, and fallback executions |
| Multi-source compilation, explicit visibility, and linking | `module_import.weave`, `module_math.weave` | ordered two-source build exits 42 |
| Pointer indexing, loads, stores, and allocation lifetime | `memory_flow.weave` | heap-backed five-element write/read sum exits 100 |
| Nominal aggregates, named fields, and alias-sensitive mutation | `struct_alias_flow.weave` | mutation through an alias is observed through the original value and exits 22 |
| Arguments, environment, standard input, stdout, and stderr | `process_inputs.weave` | six exact process-level input/output cases |
| Stable failed-compilation diagnostics and source locations | `../negative-audit/missing_module.weave` | exact diagnostic code/span with no executable, assembly, or disassembly |
| Optimization-sensitive native and LLVM budgets | `fibonacci.weave`, `fibonacci_runtime.weave` | exact or bounded optimized structure, calls, instructions, and loop backedges |

The current stable surface exposes eager Boolean `and`/`or` operations, not a
separate short-circuit control-flow form. `nested_control_flow.weave` therefore
audits the supported Boolean conjunction semantics without claiming an
unimplemented short-circuit language feature.

Pull-request and scheduled workflows discover the complete positive and negative
corpora, record per-case duration and failure class, publish reports only after
passing deterministic and model gates, and verify report freshness against
sources, sidecars, compiler identity, auditor identity, endpoint identity, and
age.
