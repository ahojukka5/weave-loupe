# weave-loupe

`weave-loupe` captures and analyzes evidence produced by the Weave compiler.
It keeps reporting, JSON processing, comparisons, and LLM-assisted review out of
`weavec` while using the compiler's stable artifact interfaces.

## Setup

```sh
uv sync --group dev
```

Ensure `weavec` is on `PATH`, or pass `--weavec` / set `WEAVEC_BIN`.

## Core workflow

```sh
uv run loupe capture docs/audit/fibonacci.weave \
  --output build/fibonacci.loupe

uv run loupe report build/fibonacci.loupe \
  --output build/fibonacci.html \
  --analysis-json build/fibonacci-analysis.json
```

The bundle retains ordered source copies, exact WIR, provenance-rich LLVM,
diagnostics, compilation trace, build manifest, stdout, stderr, hashes, and the
compiler exit code. Derived analysis treats WIR core version 2 as a first-class
stage: declarations, typed operations, structured control flow, source spans,
suspicious findings, and WIR-to-LLVM correspondence are normalized without
rewriting the stored artifact. A failed compiler run is still captured with every
artifact that reached publication.

Compiler builds and configured native runtime cases execute through one bounded
process supervisor. It applies wall-clock and POSIX resource limits, stores only
bounded output, hashes every observed byte, and terminates complete process groups
on timeout or output overflow. Compiler evidence is recorded in `bundle.json`;
runtime evidence records the effective sandbox and limits for every case.

Explicit command options override environment variables and conservative
defaults:

```sh
uv run loupe capture docs/audit/fibonacci.weave \
  --output build/fibonacci.loupe \
  --compiler-timeout-seconds 90 \
  --compiler-output-bytes 4194304
```

Compare two existing compiler results:

```sh
uv run loupe diff before.loupe after.loupe \
  --json-out comparison.json \
  --html-out comparison.html
```

The default `weave-loupe-diff-v2` output compares the complete stable evidence
chain: WIR structure and lowering correspondence, raw and optimized LLVM, native
functions and reachability, diagnostics, trace membership and order, source and
artifact identities, manifests, and optimization records. Added, removed, and
modified WIR functions are explicit, and every changed fact is classified as
semantic, quality, provenance, or evidence. Standalone bundle comparisons mark
post-capture runtime and contract results unavailable; compiler audits supply
those already-computed results. Legacy consumers can request the original compact
shape with `--format-version v1`.

Gate a candidate compiler against a baseline by compiling the same ordered inputs
with both binaries:

```sh
uv run loupe compiler-audit docs/audit/fibonacci.weave \
  --baseline-weavec /path/to/baseline/weavec \
  --candidate-weavec /path/to/candidate/weavec \
  --json-out build/compiler-audit.json \
  --report-out build/compiler-audit.md
```

The differential audit compares compilation, WIR validity and structure, lowering
correspondence, runtime observations, diagnostics, evidence availability,
optimized LLVM contracts, native budgets, and policy-bounded metric deltas. By
default it rejects increases in unresolved or anonymous WIR names, unreachable
blocks, malformed provenance, and missing, unexpected, or duplicate LLVM
correspondence. It returns `0` for a pass, `2` for a candidate regression, and `1`
for infrastructure or configuration failure. An optional `--review-model` runs
only after deterministic evidence is assembled and cannot waive a failed gate.

Ask an OpenAI-compatible model to review the complete evidence:

```sh
export WEAVE_LLM_ENDPOINT=https://integrate.api.nvidia.com/v1
export WEAVE_LLM_API_KEY=...
export WEAVE_LLM_MODEL=z-ai/glm-5.2
export WEAVE_LLM_MAX_TOKENS=4096
uv run loupe audit docs/audit/fibonacci.weave \
  --model "$WEAVE_LLM_MODEL" \
  --max-tokens "$WEAVE_LLM_MAX_TOKENS" \
  --verbose \
  --report-out docs/audit/fibonacci.md
```

Small audits use one complete request. When evidence does not fit, Loupe reviews
every deterministic, hash-addressed artifact byte range and then synthesizes one
strict final verdict. Configure conservative review admission and chunking budgets
explicitly when needed:

```sh
uv run loupe audit program.weave \
  --model "$WEAVE_LLM_MODEL" \
  --max-tokens 4096 \
  --review-total-tokens 524288 \
  --review-request-tokens 98304 \
  --review-artifact-tokens 262144 \
  --report-out build/program.md
```

The report records review mode, request count, conservative estimates, artifact
hashes and complete UTF-8 byte ranges, prompt and request hashes, request
dependencies, provider finish reasons, and provider token usage. Loupe fails rather
than silently omitting evidence when complete coverage, a partial request, or final
synthesis cannot satisfy policy.

Local OpenAI-compatible servers may use plain HTTP on loopback without an unsafe
flag:

```sh
export WEAVE_LLM_ENDPOINT=http://localhost:8000/v1
export WEAVE_LLM_API_KEY=local
uv run loupe audit docs/audit/fibonacci.weave \
  --model local-model \
  --report-out build/fibonacci-local.md
```

Non-loopback HTTP is rejected by default. Use `--allow-unsafe-http`, or set
`WEAVE_LLM_ALLOW_UNSAFE_HTTP=1`, only when an insecure remote transport is an
intentional requirement.

The first model line must be `OK` or
`FAILED: <lowercase-kebab-code>: <reason>`. Loupe returns non-zero for failed or
malformed audits and writes the report only after an `OK` verdict. Verbose reports
include the complete source, readable WIR, normalized WIR declarations and control
flow, WIR-to-LLVM correspondence, raw LLVM, optimized LLVM, the optimized LLVM
contract, assembly, linked native disassembly, optimization remarks, native
optimization contract, direct runtime observations, diagnostics, deterministic
analysis, build manifest, and compiler trace, together with timestamps, Git SHAs,
hashes, and machine specifications.

Linked-disassembly analysis uses architecture-specific x86-64 and AArch64
classifiers behind one normalized control-flow model. Analysis evidence records
the architecture, object format, disassembler identity and version when known,
parser format, call graph, branches, backedges, returns, padding, and explicit
support status. Unknown or contradictory targets fail closed rather than
publishing synthetic zero-valued native metrics.

The report also records the normalized public LLM endpoint identity, requested
model, maximum tokens, temperature, exact prompt SHA-256, canonical request
SHA-256, and any provider-returned model, response ID, system fingerprint, finish
reason, creation time, and token usage. The private transport URL remains available
only to the network client. URL credentials, query parameters, fragments, and API
keys are never published.

Verify later that a report still covers the current source, audit sidecar,
compiler executable, audit implementation, reviewer request, complete published
Markdown, and validity period without compiling or calling an LLM:

```sh
uv run loupe verify-report docs/audit/fibonacci.md \
  --weavec /path/to/weavec \
  --model "$WEAVE_LLM_MODEL" \
  --llm-endpoint "$WEAVE_LLM_ENDPOINT" \
  --max-tokens "$WEAVE_LLM_MAX_TOKENS" \
  --json-out build/fibonacci-validity.json
```

Model and endpoint options default to their matching environment variables.
Maximum-token comparison is explicit. The verifier exits `0` for a valid report,
`2` for a stale report, and `1` for an invalid invocation or infrastructure
failure. A stale result lists every detected reason instead of hiding later
mismatches behind the first one. Verification compares the sanitized public
endpoint identity. Add `--allow-unsafe-http` when intentionally verifying a report
against a non-loopback HTTP endpoint.

Generated reports contain a portable SHA-256 content seal covering the exact
Markdown, including request and provider provenance, model review, and verbose
compiler evidence. This detects accidental or unsealed manual edits; it is not a
digital signature and does not prove who produced a report.

An adjacent `foo.audit.json` file may define exact native executions, a versioned
optimized LLVM contract, and a versioned native optimization contract. The LLVM
contract bounds post-optimization structure and can require defined functions and
direct call targets while forbidding stack and memory traffic. Native contracts
bound linked-executable functions, instructions, padding, calls, and loop
backedges. Runtime cases describe arguments, environment, input, and expected
observable results. Loupe deterministically rejects any violated contract even
when the reviewing model returns `OK`.

See the [LLM endpoint transport guide](docs/llm-endpoints.md), the
[scalable review guide](docs/scalable-review.md), the
[WIR structural analysis guide](docs/wir-analysis.md), the
[complete comparison format guide](docs/diff-format.md), the
[process limit guide](docs/process-limits.md), the
[compiler regression audit guide](docs/compiler-audits.md), the
[optimized LLVM contract guide](docs/optimized-llvm-contracts.md), the
[architecture-aware native analysis guide](docs/native-analysis.md), the
[native optimization budget guide](docs/native-budgets.md), the
[audit corpus](docs/audit/README.md), and the
[pull-request audit gate](docs/audit-gate.md).

See the [documentation index](docs/index.md) and the complete
[Fibonacci walkthrough](docs/fibonacci.md), including expected terminal output,
LLVM metrics, analysis JSON, and a checked-in HTML report.

## Quality checks

```sh
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution and commit rules.
