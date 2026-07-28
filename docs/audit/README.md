# Audit corpus

This directory contains small, reviewable Weave programs and the reports generated
for them by the pull-request audit gate.

Each source, runtime matrix, and report are kept together:

- `fibonacci.weave` — auditable source
- `fibonacci.audit.json` — versioned native execution expectations
- `fibonacci.md` — generated report, created only after an `OK` verdict

The runtime sidecar is optional. When present, Loupe executes the exact linked
artifact with every declared argument, environment, input, and expected result.
Observed mismatches deterministically fail the gate even when the model returns
`OK`.

Generated reports are workflow-owned evidence, not hand-maintained prose. Change
the `.weave` source, its optional `.audit.json` matrix, or the audit implementation
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
8. native runtime execution matrix
9. diagnostics and deterministic analysis
10. build manifest and compiler trace

The report also records the exact source, Loupe, and weavec commits, compiler and
artifact hashes, runtime sidecar and executable hashes, model, timestamp,
operating system, CPU, memory, Python, and libc. This makes the LLM verdict
independently inspectable rather than treating it as an opaque approval.

Check an existing report without compiling or contacting the model:

```sh
uv run loupe verify-report docs/audit/fibonacci.md \
  --weavec /path/to/weavec
```

A valid report returns `0`; a stale report returns `2` and lists every changed
input, compiler, auditor, identity, or age condition.
