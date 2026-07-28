# Audit report validity

A passing audit report is not a permanent statement. It is valid only while its
recorded inputs, compiler executable, auditor implementation, reviewer model,
compiler identity, and maximum age still match the current environment.

Use the deterministic verifier without recompiling or contacting an LLM:

```sh
uv run loupe verify-report docs/audit/fibonacci.md \
  --weavec /path/to/weavec \
  --model z-ai/glm-5.2
```

The audited source defaults to the adjacent `.weave` file. Supply it explicitly
when the report and source are stored separately:

```sh
uv run loupe verify-report archived/report.md \
  --source docs/audit/fibonacci.weave \
  --weavec /path/to/weavec \
  --model z-ai/glm-5.2
```

`--model` defaults to `WEAVE_LLM_MODEL` when set. A standalone invocation may
omit both, in which case model identity is not evaluated. The pull-request and
scheduled workflows always provide their configured model, so repository-owned
reports cannot remain valid after the reviewer changes.

## Result contract

The command returns:

- `0` when every requested validity condition still holds;
- `2` when the report is stale; and
- `1` for an invalid invocation or infrastructure failure.

A stale result prints every detected reason. This matters when several things
changed together—for example, both the source and compiler executable—because a
single first failure would hide the complete re-audit scope.

## Verified conditions

The verifier checks the stable generated report envelope, not model-authored
prose. It verifies:

- report timestamp and maximum age;
- audited source path and SHA-256;
- runtime matrix path and SHA-256, including addition or removal;
- compiler executable SHA-256;
- content fingerprint of the audit implementation and locked dependencies;
- configured LLM model, when supplied;
- development compiler version; and
- migration to command-attested compiler identity when available.

The report is stale when any enabled condition fails. The default maximum age is
30 days and may be changed with `--max-age-days`.

## JSON evidence

Write a versioned machine-readable verification document with:

```sh
uv run loupe verify-report docs/audit/fibonacci.md \
  --weavec /path/to/weavec \
  --model z-ai/glm-5.2 \
  --json-out build/fibonacci-validity.json
```

The `weave-loupe-report-verification-v1` document contains the checked time,
policy lifetime, report and source paths, all stale reasons, the identity parsed
from the report, the current compiler identity and binary hash, the current
auditor fingerprint, and the current configured model.

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
