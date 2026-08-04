# Pull-request audit gate

`loupe audit` is a merge gate, not only a free-form reviewer. The model response
must start with one exact protocol line:

```text
OK
```

or:

```text
FAILED: lowercase-kebab-code: one-line reason
```

A failed verdict returns exit code `2`. A malformed response or infrastructure
failure returns exit code `1`. A passing verdict returns `0` and may write a
Markdown report with `--report-out`. Failed and malformed audits never publish a
report file; an existing output at that path is removed to prevent stale evidence
from being mistaken for a pass.

```sh
export WEAVE_LLM_ENDPOINT=https://integrate.api.nvidia.com/v1
uv run loupe audit docs/audit/fibonacci.weave \
  --weavec /path/to/weavec \
  --model z-ai/glm-5.2 \
  --verbose \
  --report-out docs/audit/fibonacci.md
```

`--verbose` embeds source, readable WIR, raw LLVM, optimized LLVM, target
assembly, linked executable disassembly, optimization remarks, native
optimization budget, direct runtime observations, diagnostics, deterministic
analysis, build manifest, and compiler trace. This lets a human inspect the same
source-to-native evidence independently of the LLM verdict.

## Readable WIR projection

The compiler's raw WIR remains captured and hash-addressed in the `.loupe`
bundle. `--wir-out path.wir` exports those exact bytes for provenance debugging.

The prompt and Markdown report use a deterministic review projection instead:

- source-file and source-span comments are hidden;
- semantic tokens, strings, list structure, and ordering are preserved;
- the remaining S-expression is reparsed and formatted to a readable width.

This keeps WIR visible for human lowering review without allowing provenance
annotations to dominate the report or model context.

## Native runtime matrices

A source may have an adjacent `foo.audit.json` file using format
`weave-loupe-runtime-cases-v1`. Loupe then captures the exact linked executable
and runs every declared case before asking the model for a verdict.

```json
{
  "format": "weave-loupe-runtime-cases-v1",
  "timeout_seconds": 5,
  "inherit_environment": false,
  "cases": [
    {
      "name": "twelve",
      "env": {"WEAVE_AUDIT_N": "12"},
      "args": [],
      "stdin": "",
      "expect": {
        "exit_code": 144,
        "stdout": "",
        "stderr": ""
      }
    }
  ]
}
```

Each case may specify command-line arguments, environment changes, standard
input, and exact expected exit status, standard output, and standard error.
Omitted output expectations are not compared. The default environment is empty
so host-specific variables do not silently affect results; a matrix may opt into
the inherited environment explicitly. Execution uses no shell, has a bounded
timeout, and embeds at most 16 KiB from each output stream.

The report records the sidecar and executable SHA-256 values plus each case's
command, environment, expectations, observations, output hashes, timeout status,
and failures. A mismatch triggers Loupe's deterministic gate with
`runtime-mismatch`; an LLM `OK` cannot waive directly observed incorrect native
behavior. Invalid sidecars and unavailable executables are infrastructure
failures rather than compiler findings.

## Native optimization budgets

The same sidecar may contain a versioned `native_budget` that limits measured
properties of the linked executable:

```json
{
  "format": "weave-loupe-runtime-cases-v1",
  "native_budget": {
    "format": "weave-loupe-native-budget-v1",
    "max_program_owned_functions": 1,
    "max_unreachable_program_functions": 0,
    "max_unreachable_program_instructions": 0,
    "functions": {
      "main": {
        "max_instructions": 2,
        "max_padding_instructions": 0,
        "max_direct_calls": 0,
        "max_indirect_calls": 0
      }
    }
  }
}
```

Runtime cases and native limits may be combined, and a budget-only sidecar is
valid. Limits are maximums: smaller final code continues to pass. Unknown fields,
negative values, missing named functions, unavailable disassembly, and incomplete
program-owned reachability fail closed.

An exceeded contract triggers `native-budget-exceeded` even when the reviewing
model returns `OK`. The failure lists every exceeded limit. The model is also
required to inspect the disassembly independently because a passing ceiling
prevents regressions but does not prove that no better sequence exists.

See [Native optimization budgets](native-budgets.md) for the complete schema and
review guidance.

Changes to `foo.audit.json` automatically re-audit `foo.weave` in pull requests.
Scheduled re-audits discover the sidecar through the source and therefore repeat
the same runtime matrix and final-code contract.

## Canonical audit corpus

The checked-in corpus contains complementary Fibonacci programs:

- `docs/audit/fibonacci.weave` passes the constant input `10`. It verifies
  inlining, constant propagation, loop deletion, and dead-code elimination. Its
  contract requires exactly one program-owned `main`, two non-padding
  instructions, no calls, and no dead code. Its runtime case requires exit status
  `55`.
- `docs/audit/fibonacci_runtime.weave` reads `WEAVE_AUDIT_N` at runtime. The
  compiler may still inline functions and promote variables to SSA, but it cannot
  replace the input-dependent Fibonacci computation with one constant return.
  Its matrix covers missing input, base cases, ordinary values, range fallbacks,
  and the fixture's documented non-numeric `atoi` behavior. Its budget permits
  the scalar loop and two required library calls while bounding instruction,
  padding, function, and indirect-call overhead.

For a local runtime check:

```sh
WEAVE_AUDIT_N=12 ./fibonacci_runtime
printf '%s\n' "$?"  # 144
```

The upper bound keeps every accepted Fibonacci result representable as signed
`i32`, so native-code review is not obscured by overflow semantics.

## Reproducible compiler identity

Every report records the UTC timestamp, source and Loupe Git SHAs, compiler
repository SHA, compiler binary hash, reviewer endpoint and model, provider
completion identity, machine details, and a normalized weavec version.

The preferred identity comes from `weavec --version`. For older binaries Loupe
uses the repository `VERSION` file and Git metadata:

```text
weavec v0.3.0                   # exact release
weavec v0.3.0+git.b7046aacc634  # development build
```

Reports also state whether the compiler is a release or development build and
how the version was discovered. A report must never silently use `unknown` as
the compiler version when a `VERSION` file and Git SHA are available.

A version reported by the executable is stronger evidence than an identity
inferred from the checkout around it: it proves what the audited binary itself
claims to contain. When a compiler gains native `--version` support, scheduled
auditing refreshes otherwise-fresh legacy reports whose identity source is
`repository`, `version-file`, or missing. The replacement report therefore moves
to `weavec version source: command` even when the displayed version string has
not changed.

The compiler binary SHA-256 is an independent identity. Two executables may claim
the same source version while differing because of build flags, toolchains,
packaging, corruption, or tampering. Daily maintenance therefore refreshes a
report whenever the rebuilt compiler bytes differ from the audited binary, even
when `weavec --version` is unchanged.

## Reviewer model and provider identity

The configured endpoint and requested model are part of the verdict identity.
Different models, model versions, providers, or routing aliases can inspect the
same evidence and reach different conclusions. A report therefore records:

- the normalized endpoint;
- the exact model string passed to `loupe audit`;
- the configured maximum completion size and temperature;
- the exact prompt and canonical request SHA-256 values;
- the model string returned by the provider, when supplied;
- the provider response ID and system fingerprint, when supplied; and
- the provider finish reason, creation time, and token usage, when supplied.

Endpoint normalization strips credentials, query strings, and fragments, removes
trailing slashes, lower-cases the host, and upgrades plain HTTP to HTTPS. API keys
are never published. Missing provider response fields are recorded as
`unavailable` rather than inferred.

`loupe verify-report --model MODEL --llm-endpoint ENDPOINT --max-tokens N` checks
the configured identity without making a model request. Model and endpoint options
default to `WEAVE_LLM_MODEL` and `WEAVE_LLM_ENDPOINT`; maximum-token comparison is
explicit. Pull-request and scheduled workflows provide all three. Provider-returned
fields are immutable completion provenance covered by the report content seal; the
offline verifier cannot query them independently.

The client retries bounded transient routing, throttling, timeout, connection, and
server failures. Permanent client errors fail immediately. Retry behavior changes
availability, not the request identity: every attempt uses the same prompt and
canonical request envelope.

## Auditor implementation identity

Every report also records `weave-loupe-auditor-identity-v1`, a content fingerprint
of the implementation that produced the verdict. The fingerprint covers:

- all Python modules under `src/weave_loupe/`;
- `scripts/audit_pr.py` and `scripts/reaudit_stale.py`;
- `.github/workflows/weave-audit.yml` and
  `.github/workflows/scheduled-reaudit.yml`;
- `pyproject.toml`; and
- `uv.lock`.

Paths and exact bytes are hashed in deterministic order. The identity is stable
across rebases, squash merges, and report-only commits because it does not depend
on Git history. It changes when review prompts, deterministic gates, evidence
analysis, report rendering, maintenance logic, workflow control, declared
dependencies, or locked dependency versions change.

A fresh report made by an older auditor is re-run immediately. This prevents a
fixed analysis bug or strengthened policy from leaving previously passing reports
trusted until their calendar deadline. Documentation and generated reports are
excluded because they cannot change audit decisions.

## Audited input identity

The stable `Audited inputs` section names every source and configured audit
sidecar with its SHA-256. These hashes define the exact semantic and final-code
claims reviewed by the model, exercised by runtime cases, and enforced by native
budgets. The report is invalid as soon as any source hash changes, a sidecar is
added or removed, or a sidecar hash changes. This applies even when the report is
younger than 30 days and the compiler version is unchanged.

Older reports with an unlabelled source line remain readable during migration,
but a report without an auditable source hash is refreshed rather than trusted.
The scheduled checker parses only the stable input section, so hashes inside raw
model prose or embedded analysis JSON cannot accidentally satisfy the gate.

## Pull-request workflow

The adversarial prompt requires a stage-by-stage verification matrix. An `OK`
verdict requires affirmative evidence for source semantics, Weave-to-WIR and
WIR-to-LLVM preservation, LLVM validity, arithmetic behavior, ABI and register
use, memory safety, target compatibility, configured runtime cases, configured
native limits, and the absence of avoidable compiler overhead in final native
code. Missing essential evidence produces
`FAILED: insufficient-evidence: ...` rather than a speculative pass.

The `Weave audit` workflow runs a model-backed audit only when the pull request
adds or directly modifies an existing `.weave` source, `.audit.json` runtime
sidecar, `.audit.sources` source-set manifest, or `.audit.failure.toml`
expected-failure contract. A companion source change selects its declared
multi-source target, and a sidecar change selects its adjacent source.

Changes to Loupe implementation, workflows, package metadata, ordinary
documentation, or generated `foo.md` reports do not re-run historical corpus
cases. Those pull requests complete the audit check after scope detection,
without checking out `weavec`, installing LLVM, or calling the reviewer model.
Quality CI tests the audit implementation itself.

Each successful changed-case audit produces its generated report. Reports are
committed only when every selected target passes and each new report passes
`loupe verify-report` with the same endpoint, model, and maximum-token setting.
The workflow uploads complete audit and validity evidence, and the trusted
publisher commits only those newly generated reports to the pull-request branch.

## Scheduled re-audits

`.github/workflows/scheduled-reaudit.yml` polls daily and checks every canonical
report for freshness. A still-valid report is normally due only when it reaches
the default 30-day age limit, so historical cases such as Fibonacci are generally
re-audited about once a month rather than on each pull request. A report is due
sooner when:

- it is manually forced through `workflow_dispatch`;
- its timestamp is missing or at least 30 days old;
- its source hash is missing or differs from the current source;
- an adjacent audit sidecar was added, changed, or removed;
- its compiler binary hash is missing or differs from the current executable;
- its auditor fingerprint is missing or differs from the current implementation;
- its recorded model is missing or differs from the configured model;
- its recorded endpoint is missing or differs from the configured endpoint;
- its recorded maximum completion size is missing or differs from the configured
  value;
- the current compiler is a development build and its version differs from the
  version recorded in the report; or
- the current executable reports its own version but the stored report used a
  weaker inferred identity source.

Input, toolchain, endpoint, model, and request-limit identities are checked before
age and compiler lineage. A one-minute-old report therefore cannot remain green
after its program, runtime expectations, native budget, compiler executable,
auditor implementation, endpoint, or requested reviewer changes.

Passing reports replace the old files atomically and are committed to `master`.
A failed re-audit preserves the last passing report and uploads the new failure
evidence. Exit code `2` creates or updates a deduplicated issue in
`ahojukka5/weavec` with the compiler identity, affected sources, reviewer request,
and workflow link. Infrastructure failures fail the scheduled job but do not
misclassify the compiler. Scheduled summaries and failure JSON record endpoint,
model, request limit, compiler version, compiler binary hash, identity source, and
auditor content fingerprint.

Configure these repository secrets:

- `WEAVE_LLM_ENDPOINT`
- `WEAVE_LLM_API_KEY` or the compatibility name `WEAVE_LLM_API_TOKEN`
- `WEAVE_GITHUB_TOKEN`, a fine-grained personal access token or GitHub App token
  with repository-content write access to `weave-loupe` and issue write access to
  `weavec`

Optional repository variables include `WEAVE_LLM_MODEL`,
`WEAVE_LLM_MAX_TOKENS`, and `WEAVE_LLM_MAX_ATTEMPTS`.

Scheduled report commits use `WEAVE_GITHUB_TOKEN` instead of the
workflow-generated `GITHUB_TOKEN`. GitHub therefore treats them as ordinary
authenticated pushes and starts follow-up checks automatically. The pull-request
workflow ignores report-only changes, so those commits do not start another
expensive model audit.

The pull-request workflow accepts secrets only on same-repository branches. It
does not use `pull_request_target`, because executing untrusted fork code with the
LLM or repository-write credential would expose those secrets. Repositories that
consume Loupe separately need their own selected repository or organization
secrets.
