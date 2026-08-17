# Complete compiler evidence comparisons

`loupe diff` compares two portable evidence bundles without recompiling either
input. The default output is `weave-loupe-diff-v2`, a deterministic comparison of
the complete stable evidence chain currently understood by Loupe.

```sh
uv run loupe diff before.loupe after.loupe \
  --json-out build/comparison.json \
  --html-out build/comparison.html
```

The JSON and self-contained HTML report use the same normalized comparison. The
HTML view adds summary cards, section navigation, and focused tables without
changing the machine-readable evidence.

## Compared evidence

Version 2 compares:

- compiler exit codes;
- normalized WIR core declarations, functions, structured blocks, edges,
  operations, calls, types, suspicious findings, provenance, and WIR-to-LLVM
  correspondence;
- raw LLVM structural metrics;
- optimized LLVM structural metrics;
- native target support, architecture, reachability, calls, branches, loops,
  padding, dead functions, and per-function metrics;
- diagnostics normalized by code, severity, message, and source location;
- trace action, pass, and category counts, event membership, and stable order;
- source identities and ordering;
- artifact and log presence, size, and SHA-256 identity;
- stable compiler and build-manifest fields;
- optimization-record document identities;
- runtime observations and optimized-LLVM and native contract results when the
  caller supplies those results.

Portable bundles intentionally do not contain post-capture runtime executions or
sidecar contract evaluations. A standalone `loupe diff` therefore marks the
three supplemental sections as unavailable instead of inventing values.
`loupe compiler-audit` already computes both compilers' runtime and contract
results and passes them into the v2 comparison, so those reports contain complete
supplemental differences without running anything twice.

## WIR section

`analysis.wir` appears before raw LLVM and uses the versioned
`weave-loupe-wir-analysis-v1` model. It reports explicit function additions,
removals, and modifications; metric, opcode, type, and call-graph changes; source
provenance; and cross-stage lowering correspondence. Invalid or unavailable WIR
is evidence-classified instead of being converted into zero-valued metrics.

Structured WIR blocks model `do`, `if`, and `while`; they are not asserted to be
identical to LLVM basic blocks. Function-level WIR and LLVM block counts and their
delta are reported as correspondence evidence. See the
[WIR structural analysis guide](wir-analysis.md).

## Change model

Every changed fact also appears in one stable, sorted `changes` list. Each record
contains:

- a deterministic `id`;
- the normalized `section` and `path`;
- a `kind`, such as `added`, `removed`, `hash-changed`, `reordered`, or
  `metric-changed`;
- one classification;
- one severity;
- the normalized `before` and `after` values;
- a numeric `delta` when meaningful.

The classifications are:

- `semantic` — WIR functions/calls/lowering, compilation, diagnostics, or runtime
  behavior changed;
- `quality` — WIR structure, generated-code structure, optimization, reachability,
  or contract quality changed;
- `provenance` — WIR source mapping, source ordering, trace ordering, compiler
  identity, or manifest evidence changed;
- `evidence` — an expected artifact, parser result, validity state, or evidence
  section appeared or disappeared.

Severities are report cues, not a replacement for compiler-audit policy:

- `error` identifies missing or invalid evidence and clear semantic failures;
- `warning` identifies regressions or differences requiring review;
- `info` identifies neutral additions or ordinary metric movement.

`loupe diff` reports facts and exits nonzero only for invalid input or
infrastructure failure. `loupe compiler-audit` remains the policy-enforcing
baseline-versus-candidate gate.

## Determinism and volatile fields

The comparison sorts section names, paths, function names, diagnostic identities,
and change records. WIR blocks use local deterministic identifiers and provenance
uses source indices and byte spans. Diagnostic identities use canonical JSON.
Trace identities remove timing, process, and workspace fields before hashing.
Runtime comparisons remove elapsed time, sandbox details, limits, sidecar paths,
and executable hashes that do not describe observable behavior.

Identical stable evidence produces an empty change set. Repeating the comparison
with the same inputs produces byte-equivalent normalized JSON when serialized
with sorted keys.

## Version 1 compatibility

`weave-loupe-diff-v1` contained only raw LLVM metric deltas plus trace action and
pass counters. Consumers that still require that exact compact shape can request
it explicitly:

```sh
uv run loupe diff before.loupe after.loupe \
  --format-version v1 \
  --json-out build/comparison-v1.json
```

Python callers can use either:

```python
from weave_loupe.bundle_diffing import compare_bundles, compare_bundles_v1

compare_bundles(before, after, format_version="v1")
compare_bundles_v1(before, after)
```

Version 2 also embeds a `compatibility.legacy_projection` so transition tooling
can inspect both shapes from one default comparison. New consumers should read
the top-level `format` and reject unknown versions rather than guessing fields.
