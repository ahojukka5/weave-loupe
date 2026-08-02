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

- [Audit corpus](audit/README.md) — source programs beside verbose, generated
  source-to-native audit reports.
- [Pull-request audit gate](audit-gate.md) — strict verdict protocol, report
  publication, secrets, and merge behavior.
- [Token-aware scalable review](scalable-review.md) — conservative budgets,
  deterministic chunking, complete byte coverage, staged synthesis, and request
  provenance.
- [Deterministic WIR structural analysis](wir-analysis.md) — core-v2 declarations,
  functions, structured control flow, provenance, suspicious findings,
  WIR-to-LLVM correspondence, diffs, HTML, and compiler policy.
- [Complete compiler evidence comparisons](diff-format.md) — versioned v2 bundle
  diffs, classifications, deterministic ordering, HTML navigation, supplemental
  compiler-audit context, and v1 compatibility.
- [Compiler regression audits](compiler-audits.md) — baseline-versus-candidate
  compilation, differential policies, sealed evidence, and stable exit codes.
- [LLM endpoint transport and identity](llm-endpoints.md) — HTTPS defaults,
  loopback HTTP, explicit unsafe overrides, public identities, and redaction.
- [Compiler and runtime process limits](process-limits.md) — bounded output,
  timeouts, process-tree cleanup, POSIX resources, configuration, and evidence.
- [Optimized LLVM contracts](optimized-llvm-contracts.md) — versioned
  post-optimization metric and dependency requirements.
- [Architecture-aware native analysis](native-analysis.md) — x86-64 and AArch64
  parsing, normalized control flow, tool evidence, and fail-closed targets.
- [Native optimization budgets](native-budgets.md) — versioned linked-executable
  limits and structural requirements that make final-code regressions blocking.
- [Audit report validity](report-validity.md) — deterministic freshness checks,
  complete stale reasons, exit codes, and machine-readable verification evidence.
- [Reviewer model and provider identity](model-identity.md) — requested model,
  normalized endpoint, provider response provenance, and reviewer drift handling.
- [Fibonacci walkthrough](fibonacci.md) — capture a real compilation, inspect
  expected output, and open the generated HTML report.
- [Bundle format](bundle-format.md) — layout and stability rules for
  `weave-loupe-bundle-v1`.

## Commands

- `loupe capture` builds one portable evidence bundle.
- `loupe report` creates deterministic self-contained HTML and optional analysis
  JSON with focused WIR, LLVM, and native sections.
- `loupe diff` compares the complete stable compiler evidence chain with
  `weave-loupe-diff-v2`, including WIR structure and lowering correspondence,
  emits classified changes and navigable HTML, and offers `--format-version v1`
  for the original compact projection.
- `loupe compiler-audit` compiles the same ordered inputs with baseline and
  candidate compilers, supplies runtime and contract results to the complete v2
  diff, applies deterministic WIR, LLVM, native, and runtime policy, and publishes
  sealed JSON and Markdown evidence.
- `loupe audit` reviews complete evidence in one request when it fits or through
  deterministic artifact ranges plus final synthesis when it does not. It records
  full coverage and request provenance, applies runtime, optimized-LLVM, and native
  deterministic gates, and with `--verbose` embeds the evidence in Markdown.
- `loupe verify-bundle` verifies bundle structure, paths, sizes, hashes, and
  closed-bundle contents before evidence is consumed.
- `loupe verify-report` verifies that a generated report still matches the current
  source, audit sidecar, compiler, auditor, configured endpoint and model, and
  validity period without compiling or calling an LLM.
