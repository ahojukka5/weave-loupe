# weave-loupe documentation

`weave-loupe` is the analysis and presentation companion to `weavec`.

The repository boundary is intentional:

```text
weavec
  emits deterministic compiler facts
    source → WIR → LLVM → executable
    diagnostics, trace, provenance, build manifest

weave-loupe
  consumes and presents those facts
    portable bundles, metrics, diffs, HTML, LLM review
```

Loupe retains raw compiler artifacts unchanged inside each bundle. Structural
metrics, comparisons, HTML, normalized JSON, and model reviews are derived
outputs that can be regenerated without asking the compiler to understand a
presentation format.

## Guides

- [Fibonacci walkthrough](fibonacci.md) — capture a real compilation, inspect
  expected output, and open the generated report.
- [Bundle format](bundle-format.md) — layout and stability rules for
  `weave-loupe-bundle-v1`.

## Commands

- `loupe capture` builds one portable evidence bundle.
- `loupe report` creates deterministic self-contained HTML and optional analysis
  JSON.
- `loupe diff` compares structural LLVM metrics and stable trace actions.
- `loupe audit` sends the complete evidence to an OpenAI-compatible model.

- [Pull-request audit gate](audit-gate.md)
