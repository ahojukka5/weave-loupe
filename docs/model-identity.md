# Reviewer request and provider identity

An LLM-assisted audit verdict depends on the evidence, reviewer, and exact request
settings. Two models, providers, routing aliases, prompt versions, or response
limits may inspect the same compiler artifacts and reach different conclusions.
Weave Loupe therefore records the complete reviewer request identity.

Every generated audit report contains a stable envelope such as:

```text
- **LLM endpoint:** `https://integrate.api.nvidia.com/v1`
- **LLM model:** `z-ai/glm-5.2`
- **LLM max tokens:** `4096`
- **LLM temperature:** `0.0`
- **LLM prompt SHA-256:** `<64 lowercase hexadecimal characters>`
- **LLM request SHA-256:** `<64 lowercase hexadecimal characters>`
- **Provider-reported model:** `z-ai/glm-5.2`
- **Provider response ID:** `chatcmpl-...`
- **Provider system fingerprint:** `unavailable`
- **Provider finish reason:** `stop`
- **Provider created (Unix):** `1785236400`
- **Provider prompt tokens:** `12345`
- **Provider completion tokens:** `678`
- **Provider total tokens:** `13023`
```

The endpoint field is a public identity derived separately from the private
transport URL passed to the OpenAI-compatible client. The configured `http` or
`https` scheme is preserved. The host is normalized, default ports and trailing
slashes are removed, and URL credentials, query parameters, and fragments are
discarded. API keys and the private transport URL are never written to the report.

HTTPS is accepted normally. Plain HTTP is accepted by default only for loopback
hosts: `localhost`, the IPv4 `127.0.0.0/8` range, and IPv6 `::1`. A non-loopback
HTTP endpoint requires `--allow-unsafe-http` or
`WEAVE_LLM_ALLOW_UNSAFE_HTTP=1`. See the
[endpoint transport guide](llm-endpoints.md) for the complete policy.

`LLM prompt SHA-256` hashes the exact UTF-8 prompt sent to the provider. `LLM
request SHA-256` hashes a canonical envelope containing the public endpoint
identity, requested model, exact user message, maximum completion size, and
temperature. This distinguishes requests that use identical prompt text but
different routing or generation settings without publishing transport-only
credentials or query parameters.

The hashes are reproducibility anchors, not substitutes for the prompt. A verbose
report already embeds the source-to-native evidence reviewed by the model, while
the prompt hash provides a compact exact identity for automation and archives.
Both hashes and all response fields are themselves covered by the final report
content seal.

The provider model, response ID, system fingerprint, creation time, finish reason,
and token counts are read from the OpenAI-compatible completion response. Providers
may omit any optional field; Loupe records `unavailable` rather than inventing a
value. A `length` finish reason or completion count at the configured limit is
therefore visible when a review may have been truncated.

Repository-owned verification compares the stored public endpoint identity,
requested model, and maximum completion size with `WEAVE_LLM_ENDPOINT`,
`WEAVE_LLM_MODEL`, and `WEAVE_LLM_MAX_TOKENS`. A missing value or mismatch makes
the report stale and causes the full audit to run again.

A local deterministic check does not contact the model:

```sh
uv run loupe verify-report docs/audit/fibonacci.md \
  --weavec /path/to/weavec \
  --model z-ai/glm-5.2 \
  --llm-endpoint https://integrate.api.nvidia.com/v1 \
  --max-tokens 4096
```

Model and endpoint options default to their matching environment variables. The
maximum-token comparison is enabled explicitly. Omitting a request option disables
only that comparison for standalone archival use; input, report-content, compiler,
auditor, compiler-lineage, and age checks still run. Pull-request and scheduled
workflows always provide all three values.

The optional JSON output records the parsed prompt and request hashes, every
provider response field, and the current public endpoint identity, model, and
maximum-token value. This lets release qualification and dashboards explain
reviewer drift, request truncation, and token consumption without parsing
Markdown.

Provider-returned fields are attestations supplied by that endpoint, not a
cryptographic proof of its internal model weights. A routing alias may change
behind an unchanged endpoint and model string. The maximum report age still forces
periodic re-auditing, while visible endpoint, model, request-limit, compiler,
auditor, input, or report-content changes invalidate the report immediately.
