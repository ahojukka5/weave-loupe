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
uv run loupe audit docs/audit/fibonacci.weave \
  --model "$WEAVE_LLM_MODEL" \
  --verbose \
  --report-out docs/audit/fibonacci.md
```

The first model line must be `OK` or
`FAILED: <lowercase-kebab-code>: <reason>`. Loupe returns non-zero for failed or
malformed audits and writes the report only after an `OK` verdict. Verbose reports
include the complete source, WIR, raw and optimized LLVM, assembly, linked native
disassembly, optimization remarks, direct runtime observations, diagnostics,
deterministic analysis, build manifest, and compiler trace, together with
timestamps, Git SHAs, hashes, and machine specifications.

Verify later that a report still covers the current source, runtime matrix,
compiler executable, audit implementation, reviewer model, and validity period
without compiling or calling an LLM:

```sh
uv run loupe verify-report docs/audit/fibonacci.md \
  --weavec /path/to/weavec \
  --model "$WEAVE_LLM_MODEL" \
  --json-out build/fibonacci-validity.json
```

`--model` defaults to `WEAVE_LLM_MODEL` when that environment variable is set.
The verifier exits `0` for a valid report, `2` for a stale report, and `1` for an
invalid invocation or infrastructure failure. A stale result lists every detected
reason instead of hiding later mismatches behind the first one.

An adjacent `foo.audit.json` file may define exact native executions for
`foo.weave`: arguments, environment, standard input, expected exit status, and
expected output streams. Loupe runs those cases against the exact captured
executable, hashes the observations, and deterministically rejects a report when
native behavior disagrees even when the reviewing model returns `OK`. See the
[audit corpus](docs/audit/README.md) and the
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
