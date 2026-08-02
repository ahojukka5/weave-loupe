# Baseline-versus-candidate compiler audits

`loupe compiler-audit` evaluates the same ordered Weave inputs with a baseline
and candidate compiler. It is intended for `weavec` pull-request gates where a
candidate must preserve semantics and evidence while avoiding unreviewed compiler
quality regressions.

Both compiler inputs may name an executable directly or a repository checkout
containing a built `build/weavec` binary. Loupe does not build a checkout itself:
a missing binary is an infrastructure error with an instruction to build first.

## Command

```sh
uv run loupe compiler-audit \
  docs/audit/fibonacci.weave \
  --baseline-weavec /path/to/baseline/weavec \
  --candidate-weavec /path/to/candidate/weavec \
  --work-dir build/compiler-audit \
  --json-out build/compiler-audit.json \
  --report-out build/compiler-audit.md
```

Loupe captures two independent portable bundles under `--work-dir`. Both builds
receive the same ordered source files, adjacent audit sidecar, process environment,
compiler limits, runtime limits, and sandbox policy.

The comparison records:

- baseline and candidate compiler versions, Git identities, binary hashes, and
  artifact hashes;
- compiler exit status and captured evidence availability;
- WIR core-v2 validity, declarations, structured blocks, calls, findings, source
  provenance, and WIR-to-LLVM correspondence;
- raw and optimized LLVM analysis;
- architecture-aware native analysis and call-graph reachability;
- diagnostics and compilation traces;
- runtime-case observations;
- optimized LLVM and native budget results; and
- deterministic metric deltas plus the complete v2 bundle diff.

A baseline compilation failure is an infrastructure failure because there is no
valid reference result. A candidate compilation failure is a semantic regression
when the baseline succeeds. Failed compiler bundles remain available for diagnosis,
but runtime and budget execution are explicitly marked skipped.

WIR validity is also fail closed. An invalid baseline WIR analysis is an
infrastructure failure because there is no trustworthy structural reference. A
valid baseline followed by an invalid candidate WIR is a semantic regression.
Malformed WIR never becomes an empty or zero-valued metric set.

## Default policy

The built-in policy is deliberately fail closed:

- candidate WIR must remain valid;
- candidate runtime cases must pass and normalized observations must equal the
  baseline;
- candidate optimized LLVM and native budgets must pass and their stable evidence
  must equal the baseline;
- diagnostics and artifact availability must not change; and
- selected WIR, optimized LLVM, and native metrics may decrease but may not
  increase.

The default WIR rules allow decreases but reject positive deltas for:

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

These paths protect structured reachability, symbol resolution, stable naming,
source provenance, and function-level lowering correspondence. Existing findings
may remain unchanged during a self-comparison, but a candidate cannot introduce
more without an explicit reviewed policy override.

The remaining default non-increasing metrics include optimized function,
instruction, allocation, load, store, call, identity-operation, poison, and undef
counts, plus native unreachable instructions and reachable indirect calls.

A negative delta is an optimization improvement and passes. A positive delta is a
regression unless an explicit reviewed policy permits it.

## Versioned policy overrides

Use `--policy` with a `weave-loupe-compiler-audit-policy-v1` document:

```json
{
  "format": "weave-loupe-compiler-audit-policy-v1",
  "metric_deltas": {
    "analysis.optimized_llvm.instructions": {
      "minimum": -20,
      "maximum": 1
    },
    "analysis.wir.metrics.unreachable_blocks": {
      "maximum": 1
    }
  },
  "forbid_changes": [
    "diagnostics",
    "evidence"
  ]
}
```

Each metric rule defines an inclusive allowed delta interval where delta is
`candidate - baseline`. A supplied rule replaces the default rule for the same
path. Missing or non-numeric configured evidence fails rather than becoming zero.

Runtime observations and both deterministic budget results are always protected.
A policy cannot allow a runtime mismatch, waive invalid WIR, or waive a failed
optimized LLVM or native budget.

## Outputs and exit codes

JSON output uses `weave-loupe-compiler-audit-v1` and includes a canonical SHA-256
seal over the complete document excluding the seal field. Markdown output includes
the compiler identities, failure list, metric table, optional model review, and the
normal audit-report content seal.

The embedded `comparison.bundle_diff` uses `weave-loupe-diff-v2`, including the
focused `analysis.wir` section and runtime and contract context already computed by
the audit. The candidate is not executed a second time to populate that view.

Exit codes are stable:

- `0`: deterministic pass;
- `2`: candidate regression; and
- `1`: invalid configuration or infrastructure failure.

A report is published for all three outcomes when execution reaches report
assembly. This keeps regression and failure evidence available to CI users.

## Optional model review

`--review-model` adds an advisory OpenAI-compatible review after deterministic
comparison evidence has been assembled:

```sh
uv run loupe compiler-audit docs/audit/fibonacci.weave \
  --baseline-weavec baseline/build/weavec \
  --candidate-weavec candidate/build/weavec \
  --review-model "$WEAVE_LLM_MODEL" \
  --json-out build/compiler-audit.json
```

The model receives the completed deterministic evidence, including WIR validity,
structural metrics, classified changes, and lowering correspondence. Its response
is recorded, but an `OK` model verdict cannot override WIR, runtime, budget, metric,
diagnostic, or evidence failures.

## Pull-request use

A `weavec` workflow can build the base and pull-request revisions, then invoke one
Loupe command with those two binaries. The canonical `weave-loupe` workflow also
runs a real self-comparison with the built compiler. This proves that unchanged
baseline and candidate inputs produce a deterministic pass on the checked-in audit
corpus, in addition to the fake-compiler regression matrix in unit tests.

See the [WIR structural analysis guide](wir-analysis.md) for the normalized model,
source provenance rules, structured block derivation, and diff classifications.
