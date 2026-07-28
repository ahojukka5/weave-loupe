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

The bundle retains ordered source copies, WIR, provenance-rich LLVM,
diagnostics, compilation trace, build manifest, stdout, stderr, hashes, and the
compiler exit code. A failed compiler run is still captured with every artifact
that reached publication.

Compare two compiler results:

```sh
uv run loupe diff before.loupe after.loupe \
  --json-out comparison.json \
  --html-out comparison.html
```

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

The first model line must be `OK` or
`FAILED: <lowercase-kebab-code>: <reason>`. Loupe returns non-zero for failed or
malformed audits and writes the report only after an `OK` verdict. Verbose reports
include the complete source, readable WIR, raw and optimized LLVM, assembly,
linked native disassembly, optimization remarks, native optimization contract,
direct runtime observations, diagnostics, deterministic analysis, build manifest,
and compiler trace, together with timestamps, Git SHAs, hashes, and machine
specifications.

The report also records the normalized LLM endpoint, requested model, maximum
tokens, temperature, exact prompt SHA-256, canonical request SHA-256, and any
provider-returned model, response ID, system fingerprint, finish reason, creation
time, and token usage. URL credentials, query parameters, fragments, and API keys
are never published.

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
mismatches behind the first one.

Generated reports contain a portable SHA-256 content seal covering the exact
Markdown, including request and provider provenance, model review, and verbose
compiler evidence. This detects accidental or unsealed manual edits; it is not a
digital signature and does not prove who produced a report.

An adjacent `foo.audit.json` file may define exact native executions and a
versioned native optimization contract. Runtime cases describe arguments,
environment, standard input, expected exit status, and expected output streams.
Native contracts can bound linked-executable function counts, instructions,
padding, and calls, and can require exact direct-call targets and native loop
backedges. Loupe deterministically rejects semantic mismatches, exceeded ceilings,
unmet structural minima, or missing required calls even when the reviewing model
returns `OK`.

See the [native optimization budget guide](docs/native-budgets.md), the
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
