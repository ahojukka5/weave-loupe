# Audit report validity

A passing audit report is not a permanent statement. It is valid only while its
recorded inputs, complete generated Markdown, compiler executable, auditor
implementation, reviewer endpoint, model and request limits, compiler identity,
and maximum age still match the current environment.

Use the deterministic verifier without recompiling or contacting an LLM:

```sh
uv run loupe verify-report docs/audit/fibonacci.md \
  --weavec /path/to/weavec \
  --model z-ai/glm-5.2 \
  --llm-endpoint https://integrate.api.nvidia.com/v1 \
  --max-tokens 4096
```

The verifier reads every source entry from the stable `Audited inputs` section
and preserves compiler input order. It resolves recorded paths automatically, so
normal repository-owned reports do not need `--source` arguments.

Resolution tries report-relative and repository-relative paths first. It also
recognizes absolute paths from an older checkout when their repository suffix
matches the current file. When necessary, it searches the current repository for
a unique file with the recorded name and SHA-256. This allows unchanged reports
to remain verifiable after a checkout is moved to another machine or directory.

For detached or archived reports, supply every source explicitly in the same
order used by the compiler:

```sh
uv run loupe verify-report archived/report.md \
  --source sources/declarations.weave \
  --source sources/program.weave \
  --weavec /path/to/weavec \
  --model z-ai/glm-5.2 \
  --llm-endpoint https://integrate.api.nvidia.com/v1 \
  --max-tokens 4096
```

A single repeated option remains compatible with the previous single-source CLI
usage. Omitting all `--source` options is preferred for repository-owned reports,
because the complete recorded set is then resolved from the report itself.

`--model` and `--llm-endpoint` default to `WEAVE_LLM_MODEL` and
`WEAVE_LLM_ENDPOINT` when set. `--max-tokens` enables comparison with the exact
maximum completion size recorded in the report. A standalone invocation may omit
any reviewer-request value, in which case only that comparison is disabled.
Pull-request and scheduled workflows always provide all three, so repository-owned
reports cannot remain valid after endpoint, model, or response-limit changes.

Endpoint comparison uses a public normalized identity. Credentials, query strings,
and fragments are removed, the hostname is lower-cased, trailing slashes are
removed, and plain HTTP is upgraded to HTTPS. Verification never writes an API key
or contacts the endpoint.

## Ordered source identity

Each source record contains its path, SHA-256 digest, and, for newly generated
reports, byte size. The ordered collection is part of the audit identity because
compiler input order can change name resolution, declarations, and generated
code.

Verification detects all of the following independently:

- a source file added to or removed from the current input set;
- the same files supplied in a different order;
- a source renamed or resolved to a different path;
- a recorded source that is missing;
- changed source content; and
- a changed byte size when the report records one.

Older single-source reports and older source lines without a byte size remain
supported. Their first-source `source_path` and `source_sha256` fields are retained
in the public Python and JSON contracts while the ordered `sources` collection is
the authoritative representation.

A runtime sidecar is resolved from the complete current source set. Verification
rejects a newly added, removed, renamed, or modified sidecar, and treats multiple
current sidecars as ambiguous rather than choosing one silently.

## Result contract

The command returns:

- `0` when every requested validity condition still holds;
- `2` when the report is stale; and
- `1` for an invalid invocation or infrastructure failure.

A stale result prints every detected reason. This matters when several things
changed together—for example, both the second source and compiler executable—
because a single first failure would hide the complete re-audit scope.

## Exact reviewer request

Each report records:

- normalized endpoint, requested model, maximum tokens, and temperature;
- SHA-256 of the exact UTF-8 prompt;
- SHA-256 of a canonical request envelope containing endpoint, model, user message,
  maximum tokens, and temperature;
- provider model, response ID, and system fingerprint when supplied;
- finish reason and provider creation timestamp when supplied; and
- prompt, completion, and total token counts when supplied.

The prompt hash distinguishes any evidence or prompt-template change. The request
hash also distinguishes endpoint or generation-setting changes. These values are
provenance anchors for the request that produced the verdict. The offline verifier
does not reconstruct the historical prompt from current code because machine,
compiler, report, and evidence metadata may legitimately differ later.

Maximum tokens is checked directly because a smaller limit can truncate an
otherwise identical review. Temperature remains fixed by the auditor implementation;
a code change alters the auditor fingerprint and therefore invalidates older
reports automatically.

## Complete report content

The final generated Markdown contains one stable line:

```text
- **Report content SHA-256:** `<64 lowercase hexadecimal characters>`
```

Loupe calculates it only after verbose source-to-native evidence and request and
completion provenance have been inserted. The hash therefore covers the verdict,
model narrative, request hashes and settings, provider telemetry, every ordered
source identity, WIR, LLVM, assembly, executable disassembly, runtime observations,
diagnostics, analysis, build manifest, compiler trace, and all other published
Markdown. Only the seal line itself is excluded from its own calculation.

Verification rejects a missing, malformed, duplicated, or mismatched seal. A
seal-looking line inside model-authored prose remains part of the hashed content
and cannot replace the stable envelope field.

This SHA-256 seal provides portable tamper evidence for accidental or unsealed
manual edits. It is not a digital signature: someone able to alter a report and
recompute its seal can forge the checksum. Repository branch protection, workflow
permissions, commit identity, and external signing remain separate trust layers.

## Verified conditions

The verifier checks the stable generated report envelope, not model-authored
metadata claims. It verifies:

- complete report content SHA-256;
- report timestamp and maximum age;
- the complete ordered source set, including path, SHA-256, and recorded size;
- runtime matrix path and SHA-256, including addition or removal;
- compiler executable SHA-256;
- content fingerprint of the audit implementation and locked dependencies;
- configured LLM model, when supplied;
- configured LLM endpoint, when supplied;
- configured maximum completion size, when supplied;
- development compiler version; and
- migration to command-attested compiler identity when available.

Provider telemetry and prompt and request hashes are preserved as provenance for
the exact historical request. They cannot be independently queried from the
offline provider and are therefore not treated as current-environment inputs.

The report is stale when any enabled condition fails. The default maximum age is
30 days and may be changed with `--max-age-days`.

## JSON evidence

Write a versioned machine-readable verification document with:

```sh
uv run loupe verify-report docs/audit/fibonacci.md \
  --weavec /path/to/weavec \
  --model z-ai/glm-5.2 \
  --llm-endpoint https://integrate.api.nvidia.com/v1 \
  --max-tokens 4096 \
  --json-out build/fibonacci-validity.json
```

The `weave-loupe-report-verification-v1` document contains the checked time,
policy lifetime, report path, legacy first-source path, complete current `sources`
array, all stale reasons, and the full stable identity parsed from the report.
The report identity contains the ordered source records as well as the legacy
first-source fields.

For every source difference, `source_mismatches` records:

- mismatch kind;
- recorded and current indices;
- recorded and current paths;
- recorded and current SHA-256 values;
- recorded and current byte sizes; and
- a human-readable detail string matching the stale reason.

This makes a changed second or later source directly diagnosable without parsing
console text. A pure reorder is represented as a dedicated `reordered` mismatch
rather than a set of false content changes.

The identity also includes content, prompt, and request SHA-256 values; endpoint,
model, maximum tokens, and temperature; provider model, response ID, system
fingerprint, finish reason, creation timestamp, and token usage. The document
records the current compiler identity and binary hash, auditor fingerprint,
endpoint, model, and maximum-token value.

The JSON file is written for both valid and stale results. It is suitable for CI,
release qualification, dashboards, and archival evidence.

## Relationship to scheduled re-auditing

The daily scheduled workflow and `loupe verify-report` use the same parser and
validity evaluator. Scheduled maintenance uses the primary reason to decide why a
report is due, while the public command exposes the complete reason set for human
and automated diagnosis.

Verification is deliberately cheaper than re-auditing: it performs no
compilation, native execution, or model request. A stale result says that the old
verdict can no longer be trusted for the current environment; the full audit
workflow must produce the replacement report.
