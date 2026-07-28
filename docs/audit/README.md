# Audit corpus

This directory contains small, reviewable Weave programs and the reports generated
for them by the pull-request audit gate.

Each source, audit sidecar, and report are kept together:

- `fibonacci.weave` — auditable source
- `fibonacci.audit.json` — versioned runtime and native-code expectations
- `fibonacci.md` — generated report, created only after a passing final verdict

The audit sidecar is optional. It may contain runtime cases, a native optimization
budget, or both. Runtime cases execute the exact linked artifact with every
declared argument, environment, input, and expected result. Native contracts bound
program-owned function counts and per-function instructions, padding, direct and
indirect calls, and may require specific call targets and loop backedges.

Observed runtime mismatches, exceeded final-code limits, unmet structural minima,
or missing required calls deterministically fail the gate even when the model
returns `OK`. Contract evaluation also fails closed when linked disassembly or
complete program-owned reachability is unavailable.

Generated reports are workflow-owned evidence, not hand-maintained prose. Change
the `.weave` source, its optional `.audit.json` sidecar, or the audit implementation
instead of editing the adjacent report directly. A pull request that changes or
deletes `foo.md` automatically re-audits `foo.weave` and replaces the report with
fresh evidence after a passing verdict. Ordinary corpus documentation such as
this README has no adjacent source and skips compiler and LLM setup.

The workflow runs `loupe audit --verbose`, so every generated report includes the
complete source-to-native evidence chain:

1. Weave source
2. readable WIR with provenance comments hidden
3. raw LLVM IR
4. optimized LLVM IR
5. target assembly
6. linked executable disassembly
7. LLVM optimization remarks
8. native optimization contract and observed metrics
9. native runtime execution matrix
10. diagnostics and deterministic analysis
11. build manifest and compiler trace

The constant Fibonacci contract requires exactly one program-owned `main`, two
non-padding instructions, no calls, no dead code, and no backward conditional
branches.

The runtime-input contract requires exactly one backward conditional branch in
`main`, proving the scalar recurrence loop remains in the linked executable. It
also requires direct calls to `getenv@plt` and `atoi@plt`, forbids indirect calls
and dead program functions, and bounds instructions and padding. Nine runtime
cases independently verify observable behavior. A compiler cannot satisfy the
gate merely by producing some small program that happens to return the checked
values.

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
