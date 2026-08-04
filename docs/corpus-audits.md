# Corpus audit command

The installed `loupe-corpus` command exposes the same positive and
expected-failure corpus orchestration used by the scheduled GitHub Actions
workflow. It calls `weave_loupe.scheduled_audit:main` directly; the repository
script remains a compatibility entry point rather than a separate implementation.

## Refresh stale reports

Provide the compiler and reviewer identity plus explicit output locations:

```sh
export WEAVE_LLM_ENDPOINT=https://example.test/v1
export WEAVE_LLM_API_KEY=...

uv run loupe-corpus \
  --weavec /path/to/weavec \
  --model z-ai/glm-5.2 \
  --llm-endpoint "$WEAVE_LLM_ENDPOINT" \
  --max-tokens 4096 \
  --summary build/corpus-audit/summary.md \
  --reports-list build/corpus-audit/reports.txt \
  --failures-json build/corpus-audit/failures.json \
  --logs-dir build/corpus-audit/logs
```

By default the command discovers `docs/audit` and `docs/negative-audit`, checks
all report identities and freshness conditions, and runs only cases that are
missing or stale. Override the roots with `--source-root` and `--negative-root`
when auditing another corpus layout.

Freshness includes source and sidecar content, compiler version and binary hash,
auditor content, model and endpoint identities, token policy, and report age. Use
`--max-age-days` to change the age limit.

## Pull-request boundary

A corpus case is model-audited in a pull request only when that pull request adds
or directly changes its `.weave` source, `.audit.json` runtime sidecar,
`.audit.sources` manifest, or `.audit.failure.toml` contract. Changes to Loupe
implementation, workflows, package metadata, ordinary documentation, or a
generated report do not re-run historical cases such as Fibonacci.

The scheduled workflow owns ongoing corpus maintenance. It checks freshness
daily, but with the default 30-day age limit a still-valid report is normally
re-audited about once a month. Compiler, input, auditor, endpoint, or reviewer
identity changes can make a report due sooner.

## Run the complete corpus

Add `--force` to execute every discovered positive and expected-failure case even
when its checked-in report is fresh:

```sh
uv run loupe-corpus \
  --weavec /path/to/weavec \
  --model z-ai/glm-5.2 \
  --llm-endpoint "$WEAVE_LLM_ENDPOINT" \
  --max-tokens 4096 \
  --summary build/corpus-audit/summary.md \
  --reports-list build/corpus-audit/reports.txt \
  --failures-json build/corpus-audit/failures.json \
  --logs-dir build/corpus-audit/logs \
  --force
```

## Outputs and publication

The command writes:

- a Markdown summary with discovered counts, due counts, per-case duration, and
  failure class;
- a reports list containing the report paths published by the run;
- a versioned failures JSON document separating compiler findings from
  infrastructure failures;
- bounded stdout and stderr logs for every executed case.

Candidate reports are generated in an isolated temporary directory. They replace
the checked-in report paths only when every executed case passes. A mixed or
failing run therefore cannot publish a partial corpus refresh.

## Exit codes

- `0` — every executed audit passed, or no report was due;
- `2` — at least one deterministic compiler finding was observed and no
  infrastructure failure occurred;
- `1` — discovery, configuration, compiler execution, model transport, or another
  infrastructure step failed.

The existing `scripts/reaudit_stale.py` command accepts the same arguments and
remains available for workflow compatibility. New installed-package integrations
should use `loupe-corpus`.
