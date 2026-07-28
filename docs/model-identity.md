# Reviewer model identity

An LLM-assisted audit verdict depends on both the evidence and the reviewer. Two
models, model versions, providers, or routing aliases may inspect identical
source-to-native artifacts and reach different conclusions. Weave Loupe therefore
treats the configured model string as part of the report identity.

Every generated audit report records:

```text
- **LLM model:** `z-ai/glm-5.2`
```

Repository-owned verification always compares that value with the active
`WEAVE_LLM_MODEL`. A missing value or mismatch makes the report stale and causes
the full audit to run again.

A local deterministic check does not contact the model:

```sh
uv run loupe verify-report docs/audit/fibonacci.md \
  --weavec /path/to/weavec \
  --model z-ai/glm-5.2
```

The option defaults to `WEAVE_LLM_MODEL` when that environment variable is set.
Omitting both leaves model comparison disabled for standalone archival use; input,
compiler, auditor, compiler-lineage, and age checks still run. Pull-request and
scheduled workflows never omit the configured model.

The optional JSON output records both `report_identity.model` and
`current_model`, allowing release qualification and dashboards to explain model
drift without parsing human-readable output.
