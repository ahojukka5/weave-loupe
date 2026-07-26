# Fibonacci walkthrough

This walkthrough uses [`examples/fibonacci_iterative.weave`](../examples/fibonacci_iterative.weave).
It computes `fib(10)` iteratively and returns `55` as the process exit code.

## 1. Capture compiler evidence

```sh
uv run loupe capture examples/fibonacci_iterative.weave \
  --output build/fibonacci.loupe
```

Expected output:

```text
bundle: <repository>/build/fibonacci.loupe
compiler exit: 0
```

The bundle contains the source, WIR, LLVM with source/WIR provenance comments,
diagnostics, trace, build manifest, and compiler logs. Use
`--include-executable` when the native executable must also be retained.

## 2. Generate a report

```sh
uv run loupe report build/fibonacci.loupe \
  --output build/fibonacci.html \
  --analysis-json build/fibonacci-analysis.json
```

Expected output:

```text
report: <repository>/build/fibonacci.html
analysis: <repository>/build/fibonacci-analysis.json
```

Open `build/fibonacci.html` in a browser. It is one self-contained file with:

- compiler status and trace summary;
- structural LLVM metrics;
- the exact source input;
- emitted WIR;
- LLVM with source and WIR byte ranges;
- diagnostics, trace, and build-manifest JSON;
- normalized analysis JSON.

A normalized report generated from the current compiler is checked in at
[`docs/examples/fibonacci-report.html`](examples/fibonacci-report.html). Its
machine-readable summary is
[`docs/examples/fibonacci-analysis.json`](examples/fibonacci-analysis.json).

## 3. Expected current analysis

For the current pre-optimization LLVM, Loupe reports:

| Metric | Value |
| --- | ---: |
| Functions | 2 |
| Basic blocks | 10 |
| Instructions | 33 |
| Stack allocations | 3 |
| Loads | 4 |
| Stores | 6 |
| Phi nodes | 3 |
| Branches | 7 |
| Identity additions | 2 |
| Source-provenance comments | 14 |
| Anonymous SSA lines | 0 |
| Numeric blocks | 0 |
| `undef` uses | 0 |
| `poison` uses | 0 |

These numbers are observations, not hard-coded expectations inside Loupe. They
make compiler changes comparable. For example, a future direct-SSA or optimized
LLVM path should reduce stack allocations, loads, stores, and identity additions
without losing source provenance.

The compilation trace currently contains zero events for this example because
the implemented stable trace actions concern transformations not exercised by
this program. The trace registry follow-up will make coverage explicit rather
than treating an empty trace as an error.

## 4. Compare compiler versions

Capture the same source with two compiler builds, then run:

```sh
uv run loupe diff old.loupe new.loupe \
  --json-out build/fibonacci-diff.json \
  --html-out build/fibonacci-diff.html
```

The comparison reports deltas for LLVM structure and stable trace actions. A
negative instruction or stack-traffic delta is visible immediately, while added
or removed compiler transformations remain attributable to trace action names.

## 5. Ask for an LLM audit

```sh
export WEAVE_LLM_ENDPOINT=https://integrate.api.nvidia.com/v1
export WEAVE_LLM_API_KEY=...
uv run loupe audit examples/fibonacci_iterative.weave
```

The model receives source, WIR, LLVM, diagnostics, trace summaries, and LLVM
metrics. The prompt requires each finding to identify the stage that introduced
it and to separate algorithmic improvements from compiler-generated overhead.
