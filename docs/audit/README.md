# Audit corpus

This directory contains small, reviewable Weave programs and the reports generated
for them by the pull-request audit gate.

Each source and report are kept together:

- `fibonacci.weave` — auditable source
- `fibonacci.md` — generated report, created only after an `OK` verdict

The workflow runs `loupe audit --verbose`, so every generated report includes the
complete source-to-native evidence chain:

1. Weave source
2. WIR
3. raw LLVM IR
4. optimized LLVM IR
5. target assembly
6. linked executable disassembly
7. LLVM optimization remarks
8. diagnostics and deterministic analysis
9. build manifest and compiler trace

The report also records the exact source, Loupe, and weavec commits, artifact
hashes, model, timestamp, operating system, CPU, memory, Python, and libc. This
makes the LLM verdict independently inspectable rather than treating it as an
opaque approval.
