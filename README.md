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
uv run loupe capture examples/fibonacci_iterative.weave \
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
uv run loupe audit examples/fibonacci_iterative.weave \
  --report-out examples/fibonacci_iterative.md
```

The first model line must be `OK` or
`FAILED: <lowercase-kebab-code>: <reason>`. Loupe returns non-zero for failed or
malformed audits and writes the report only after an `OK` verdict. Reports include
the audit timestamp, source/compiler Git SHAs, binary and artifact hashes, and
machine specifications. See the [pull-request audit gate](docs/audit-gate.md).

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
