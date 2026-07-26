# weave-loupe

Tools to help in Weave compiler development.

## Setup

```sh
uv sync --group dev
```

Ensure `weavec` is on `PATH` (or set `WEAVEC_BIN`), and configure:

```sh
export WEAVE_LLM_ENDPOINT=https://integrate.api.nvidia.com/v1
export WEAVE_LLM_API_KEY=...
```

## Usage

```sh
uv run loupe <command>
```

### audit

Compile a Weave program to WIR and LLVM IR, then ask an LLM for a serious-issue
and performance report. The prompt includes `.weave`, `.wir`, and `.ll` by
default:

```sh
uv run loupe audit examples/fibonacci_iterative.weave
uv run loupe audit examples/fibonacci_iterative.weave --verbose
```

Optional flags: `--model`, `--weavec`, `--wir-out`, `--llvm-out`,
`--max-tokens`, `--verbose`.

## Quality checks

```sh
uv run ruff check .
uv run ruff format .
uv run mypy
uv run pytest
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution and commit rules.
