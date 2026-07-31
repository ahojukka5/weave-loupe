# Optimized LLVM contracts

The optimized LLVM module is the exact IR handed to target code generation. A
compact final executable can hide an optimizer regression—for example, stack
traffic that the backend happens to remove—or a changed dependency graph. Loupe
therefore supports a deterministic contract for the post-optimization module in
the source's adjacent `.audit.json` sidecar.

```json
{
  "format": "weave-loupe-runtime-cases-v1",
  "optimized_llvm_budget": {
    "format": "weave-loupe-optimized-llvm-budget-v1",
    "min_functions": 1,
    "max_functions": 1,
    "max_instructions": 20,
    "max_alloca": 0,
    "max_load": 0,
    "max_store": 0,
    "min_call": 2,
    "max_call": 2,
    "min_phi": 2,
    "max_phi": 5,
    "required_defined_functions": ["main"],
    "required_call_targets": ["atoi", "getenv"]
  }
}
```

The top-level sidecar format remains `weave-loupe-runtime-cases-v1`. Runtime
cases, an optimized LLVM contract, and a native optimization contract may be used
together. Any one of these contracts is sufficient for a sidecar with no runtime
cases.

## Metric contracts

Every integer metric produced by Loupe's LLVM structural analysis may be bounded
with `min_<metric>` and `max_<metric>`:

- module shape: `functions`, `basic_blocks`, `instructions`;
- memory and calls: `alloca`, `load`, `store`, `call`, `invoke`;
- control flow: `phi`, `br`, `switch`, `ret`, `icmp`, `select`;
- arithmetic: `add`, `sub`, `mul`, `sdiv`, `udiv`;
- hygiene: `identity_adds`, `anonymous_ssa_lines`, `numeric_blocks`,
  `undef_uses`, and `poison_uses`.

All values are non-negative integers. A minimum cannot exceed its corresponding
maximum. Unknown fields and empty contracts are rejected rather than ignored.

Maximums prevent optimizer regressions while allowing improvements. Minimums
preserve necessary structure such as a dynamic loop's SSA phi nodes, branches,
and arithmetic.

## Required symbols

`required_defined_functions` requires exact function definitions in the optimized
module. Combining `required_defined_functions: ["main"]` with
`max_functions: 1` proves that no helper definition survives optimization.

`required_call_targets` requires exact direct LLVM call or invoke targets. With a
call-count maximum equal to the number of required targets, it also proves that no
additional direct call remains.

The names use LLVM symbols, not platform-specific linker spellings. The canonical
dynamic fixture therefore requires `getenv` and `atoi` in optimized LLVM, while
its native contract requires `getenv@plt` and `atoi@plt` on Linux x86-64.

## Gate behavior

Loupe evaluates the exact captured `optimized_llvm` artifact before accepting the
model verdict. An unavailable module, exceeded maximum, unmet minimum, missing
defined function, or missing call target makes the contract fail.

When the model returns `OK`, Loupe replaces it with:

```text
FAILED: optimized-llvm-budget-exceeded: ...
```

Every violated condition is included in the report evidence. The failed report is
not published. Model prose cannot waive the deterministic result.

The sidecar SHA-256 already participates in report validity. Adding, removing, or
changing the contract invalidates the adjacent report and triggers a complete
source-to-native re-audit.

## Canonical contracts

The constant Fibonacci fixture requires optimized LLVM to contain exactly one
function, one basic block, and one instruction: `main` returning the constant
`55`. It forbids memory traffic, calls, branches, phi nodes, switch instructions,
identity additions, undef, and poison.

The runtime-input fixture requires one defined `main`, no alloca/load/store
traffic, exactly two calls to `getenv` and `atoi`, bounded instruction and block
counts, SSA phi nodes and branches for the dynamic loop, recurrence arithmetic,
and no undef, poison, or identity additions.

These IR contracts complement the native contracts and runtime matrix:

- optimized LLVM proves the compiler delivered clean SSA to the backend;
- native analysis proves the expected loop and external dependencies survived
  target code generation and linking; and
- runtime cases prove observable behavior over representative inputs.

A passing contract is still not a mathematical proof of global optimality. It is
a precise, versioned upper and lower envelope for reviewed IR. The full optimized
module, optimization remarks, native disassembly, deterministic metrics, runtime
observations, and adversarial review remain available for tightening the contract
when a better result is found.
