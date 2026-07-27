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
uv run loupe audit docs/audit/fibonacci.weave \
  --weavec /path/to/weavec \
  --model z-ai/glm-5.2 \
  --verbose \
  --report-out docs/audit/fibonacci.md
```

`--verbose` embeds source, readable WIR, raw LLVM, optimized LLVM, target
assembly, linked executable disassembly, optimization remarks, diagnostics,
deterministic analysis, build manifest, and compiler trace. This lets a human
inspect the same source-to-native evidence independently of the LLM verdict.

## Readable WIR projection

The compiler's raw WIR remains captured and hash-addressed in the `.loupe`
bundle. `--wir-out path.wir` exports those exact bytes for provenance debugging.

The prompt and Markdown report use a deterministic review projection instead:

- source-file and source-span comments are hidden;
- semantic tokens, strings, list structure, and ordering are preserved;
- the remaining S-expression is reparsed and formatted to a readable width.

This keeps WIR visible for human lowering review without allowing provenance
annotations to dominate the report or model context.

## Canonical audit corpus

The checked-in corpus contains complementary Fibonacci programs:

- `docs/audit/fibonacci.weave` passes the constant input `10`. It verifies
  inlining, constant propagation, loop deletion, and dead-code elimination; the
  ideal final program is a two-instruction `main` returning `55`.
- `docs/audit/fibonacci_runtime.weave` reads `WEAVE_AUDIT_N` at runtime. The audit
  harness supplies a decimal value from `0` through `46`; missing or numerically
  out-of-range input falls back to `10`. The compiler may still inline functions
  and promote variables to SSA, but it cannot replace the input-dependent
  Fibonacci computation with one constant return.

For a local runtime check:

```sh
WEAVE_AUDIT_N=12 ./fibonacci_runtime
printf '%s\n' "$?"  # 144
```

The upper bound keeps every accepted Fibonacci result representable as signed
`i32`, so native-code review is not obscured by overflow semantics.

## Reproducible compiler identity

Every report records the UTC timestamp, source and Loupe Git SHAs, compiler
repository SHA, compiler binary hash, model, machine details, and a normalized
weavec version.

The preferred identity comes from `weavec --version`. For older binaries Loupe
uses the repository `VERSION` file and Git metadata:

```text
weavec v0.3.0                 # exact release
weavec v0.3.0+git.b7046aacc634  # development build
```

Reports also state whether the compiler is a release or development build and
how the version was discovered. A report must never silently use `unknown` as
the compiler version when a `VERSION` file and Git SHA are available.

## Pull-request workflow

The adversarial prompt requires a stage-by-stage verification matrix. An `OK`
verdict requires affirmative evidence for source semantics, Weave-to-WIR and
WIR-to-LLVM preservation, LLVM validity, arithmetic behavior, ABI and register
use, memory safety, target compatibility, and the absence of avoidable compiler
overhead in final native code. Missing essential evidence produces
`FAILED: insufficient-evidence: ...` rather than a speculative pass.

The `Weave audit` workflow audits every added, copied, modified, or renamed
`.weave` file in a pull request. Changes to the audit engine run the canonical
programs under `docs/audit/` as a self-test. Each successful `foo.weave` audit
produces `foo.md`; reports are committed only when every audited source passes.
The workflow updates one persistent PR comment and uploads complete evidence.

A report records the exact code commit that was audited. The automated report
commit contains only generated reports, so its parent is the reproducible audited
state rather than an unaudited source change.

## Scheduled re-audits

`.github/workflows/scheduled-reaudit.yml` runs daily and checks every canonical
report. A report is due when:

- its timestamp is missing or at least 30 days old;
- it is manually forced through `workflow_dispatch`; or
- the current compiler is a development build and its version differs from the
  version recorded in the report.

Passing reports replace the old files atomically and are committed to `master`.
A failed re-audit preserves the last passing report and uploads the new failure
evidence. Exit code `2` creates or updates a deduplicated issue in `ahojukka5/weavec`
with the compiler identity, affected sources, and workflow link. Infrastructure
failures fail the scheduled job but do not misclassify the compiler.

Configure these repository secrets:

- `WEAVE_LLM_ENDPOINT`
- `WEAVE_LLM_API_KEY` or the compatibility name `WEAVE_LLM_API_TOKEN`
- `WEAVE_GITHUB_TOKEN`, a fine-grained personal access token or GitHub App token
  with repository-content write access to `weave-loupe` and issue write access to
  `weavec`

The report commits use `WEAVE_GITHUB_TOKEN` instead of the workflow-generated
`GITHUB_TOKEN`. GitHub therefore treats them as ordinary authenticated pushes and
starts follow-up checks automatically. The pull-request guard recognizes its own
report-only commit and avoids a duplicate expensive LLM audit.

The pull-request workflow accepts secrets only on same-repository branches. It
does not use `pull_request_target`, because executing untrusted fork code with the
LLM or repository-write credential would expose those secrets. Repositories that
consume Loupe separately need their own selected repository or organization
secrets.
