# Token-aware scalable audit review

`loupe audit` always prepares the complete compiler-evidence inventory before it
contacts a model. Small audits use one request. Larger audits use deterministic
artifact requests followed by one final synthesis request, without silently
omitting evidence.

Deterministic runtime, optimized LLVM, and native-code gates remain independent of
model context size and model verdicts. A model cannot waive a failed deterministic
contract.

## Conservative token estimation

Loupe uses `utf8-byte-upper-bound-v1`: the UTF-8 byte count plus a small fixed
envelope allowance. Byte-level tokenizers cannot produce more tokens than input
bytes, so this is intentionally conservative and does not require a provider
specific tokenizer or a network lookup.

The estimate is used for admission and planning. Provider-reported token usage is
recorded separately after every successful request.

## Review budgets

The audit command accepts three policy limits:

```sh
uv run loupe audit program.weave \
  --model "$WEAVE_LLM_MODEL" \
  --max-tokens 4096 \
  --review-total-tokens 524288 \
  --review-request-tokens 98304 \
  --review-artifact-tokens 262144 \
  --report-out build/program.md
```

- `--review-total-tokens` bounds all estimated request inputs plus every reserved
  completion in the complete review.
- `--review-request-tokens` bounds one request plus its reserved completion.
- `--review-artifact-tokens` rejects a single unexpectedly large artifact before
  any model request is sent.
- `--max-tokens` remains the final review completion limit. Artifact-level reviews
  use a smaller internal completion allowance.

All limits must be positive. The per-request limit cannot exceed the total limit.
A review fails before sending requests when complete coverage or final synthesis
cannot fit the configured policy.

## Single-request path

When the full adversarial audit prompt and reserved completion fit both the
per-request and total budgets, Loupe retains the original single-request protocol:

```text
OK
FAILED: <lowercase-kebab-code>: <one-line reason>
```

The resulting review plan records one request and full coverage of every artifact.

## Staged path

When complete evidence does not fit one request, Loupe performs three phases:

1. Build a compact deterministic summary of compiler status, evidence
   availability, native support, and deterministic gate results.
2. Review every exact artifact byte range with an artifact-level protocol.
3. Send all range findings, the deterministic summary, and the complete coverage
   map to one final synthesis request using the strict audit verdict protocol.

Artifact-level responses begin with either:

```text
REVIEWED
FAILED: <lowercase-kebab-code>: <one-line reason>
```

`FAILED` marks a candidate blocking finding for synthesis. The final request must
resolve every such finding explicitly and returns the only model verdict consumed
by the audit gate.

A malformed response, empty response, provider truncation, connection failure, or
partial staged failure aborts the audit. Loupe does not continue with incomplete
coverage.

## Structural chunking

Chunk boundaries are deterministic and prefer stable textual structure:

- LLVM definitions, declarations, and attribute groups;
- assembly and disassembly function labels;
- LLVM optimization-record document boundaries;
- source-file headers and source or WIR function boundaries; and
- line boundaries for JSON, manifests, diagnostics, traces, and other text.

An oversized single function or line is split at the largest UTF-8-safe byte
boundary that fits. Unicode code points are never split into invalid text.

The same artifact bytes, deterministic summary, model configuration, and policy
produce the same chunk boundaries, prompts, and request hashes.

## Coverage accounting

Every artifact has a public review identity containing:

- logical artifact name and label;
- language;
- complete UTF-8 byte size and SHA-256;
- conservative token estimate;
- ordered covered ranges; and
- a boolean complete-coverage result.

Every range records `[start, end)` byte offsets and the SHA-256 of exactly those
bytes. Loupe validates that ranges begin at zero, remain contiguous without gaps
or overlaps, and end at the complete artifact size.

The staged inventory includes reproducibility metadata, all ordered source text,
cleaned WIR, raw and optimized LLVM, assembly, linked disassembly, optimization
records, diagnostics, deterministic analysis, build manifest, and compiler trace.
Empty artifacts still receive an explicit zero-length covered range.

## Request provenance

Generated Markdown reports contain a **Model review coverage and requests**
section. It lists:

- review mode, estimator, policy, total estimate, and request count;
- every artifact hash, size, estimate, and covered range;
- every request ID and kind;
- request dependencies;
- estimated input and reserved output tokens;
- exact prompt and canonical request hashes;
- requested and provider-reported models;
- provider response ID and finish reason; and
- provider prompt, completion, and total token usage.

The final synthesis request lists every artifact request as a dependency. The
normal report content seal covers this complete provenance together with the
model review and deterministic evidence.

## Failure behavior

Loupe returns infrastructure exit code `1` and publishes no passing report when:

- an artifact exceeds its configured limit;
- the complete plan exceeds the total limit;
- a request or synthesis cannot fit the per-request limit;
- coverage contains a gap or overlap;
- the endpoint fails partway through a staged review;
- an artifact or synthesis response violates its first-line protocol; or
- the provider reports truncation or another non-terminal finish reason.

This is deliberate. A cheaper partial review is not represented as a complete
release-gate audit.
