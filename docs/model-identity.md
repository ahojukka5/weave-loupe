# Reviewer model and provider identity

An LLM-assisted audit verdict depends on both the evidence and the reviewer. Two
models, model versions, providers, or routing aliases may inspect identical
source-to-native artifacts and reach different conclusions. Weave Loupe therefore
treats the requested model and configured endpoint as part of report identity.

Every generated audit report records a stable envelope such as:

```text
- **LLM endpoint:** `https://integrate.api.nvidia.com/v1`
- **LLM model:** `z-ai/glm-5.2`
- **Provider-reported model:** `z-ai/glm-5.2`
- **Provider response ID:** `chatcmpl-...`
- **Provider system fingerprint:** `unavailable`
```

The endpoint identity is normalized before publication. Plain HTTP is upgraded to
HTTPS, the host is lower-cased, trailing slashes are removed, and URL credentials,
query parameters, and fragments are discarded. API keys are never written to the
report.

`LLM model` is the exact requested model string. The remaining provider fields are
read from the OpenAI-compatible completion response. Providers may omit a response
ID or system fingerprint; Loupe records `unavailable` rather than inventing an
identity. These fields identify the exact response that produced the verdict and
are covered by the report content seal.

Repository-owned verification compares the stored endpoint and requested model
with `WEAVE_LLM_ENDPOINT` and `WEAVE_LLM_MODEL`. A missing value or mismatch makes
the report stale and causes the full audit to run again.

A local deterministic check does not contact the model:

```sh
uv run loupe verify-report docs/audit/fibonacci.md \
  --weavec /path/to/weavec \
  --model z-ai/glm-5.2 \
  --llm-endpoint https://integrate.api.nvidia.com/v1
```

Both options default to their matching environment variables. Omitting an option
and its environment variable disables only that comparison for standalone
archival use; input, report-content, compiler, auditor, compiler-lineage, and age
checks still run. Pull-request and scheduled workflows always provide both values.

The optional JSON output records `report_identity.endpoint`, provider provenance,
`current_endpoint`, `report_identity.model`, and `current_model`. This lets release
qualification and dashboards explain reviewer drift without parsing Markdown.

Provider-returned fields are attestations supplied by that endpoint, not a
cryptographic proof of the provider's internal model weights. A routing alias may
change behind an unchanged endpoint and model string. The maximum report age still
forces periodic re-auditing, while any visible endpoint or model configuration
change invalidates the report immediately.
