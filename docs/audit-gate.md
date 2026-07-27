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

`--verbose` embeds the focused compiler evidence in the Markdown report: source,
raw LLVM, optimized LLVM, target assembly, linked executable disassembly,
optimization remarks, diagnostics, deterministic analysis, build manifest, and
compiler trace. This is the mode used by the pull-request workflow so a human can
inspect the evidence independently of the LLM verdict.

WIR is intentionally omitted from the LLM prompt and generated Markdown. Current
WIR contains dense source-provenance annotations that add substantial context
without improving the source-to-native review. The compiler still captures WIR
inside the bundle, and `--wir-out path.wir` exports it explicitly when a lowering
or provenance investigation needs it.

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

Every generated report records the UTC timestamp, audited source Git SHA, Loupe
and compiler Git SHAs when discoverable, compiler binary hash and version, source
and artifact hashes, model, operating system, kernel, CPU architecture and model,
logical CPU count, memory, Python version, and libc. The deterministic envelope
is produced by Loupe rather than delegated to the model.

The audit prompt is adversarial and requires a stage-by-stage verification matrix.
An `OK` verdict requires affirmative evidence for source semantics, source-to-LLVM
preservation, LLVM validity, signedness and arithmetic behavior, ABI and register
use, memory safety, target compatibility, and the absence of avoidable compiler
overhead in final native code. Missing essential evidence produces
`FAILED: insufficient-evidence: ...` rather than a speculative pass.

The `Weave audit` workflow audits every added, copied, modified, or renamed
`.weave` file in a pull request, regardless of its directory. Changes to the audit
engine itself run the canonical programs under `docs/audit/` as a self-test. Each
successful `foo.weave` audit produces `foo.md`; reports are committed to the
pull-request branch only when every audited source passes. The workflow updates
one persistent PR comment with pass or failure details and uploads the complete
result as an artifact.

A report records the exact code commit that was audited. The following automated
commit adds only the generated report, so its parent is the reproducible audited
state rather than an unaudited source change.

Configure these repository secrets:

- `WEAVE_LLM_ENDPOINT`
- `WEAVE_LLM_API_KEY` or the compatibility name `WEAVE_LLM_API_TOKEN`
- `WEAVE_GITHUB_TOKEN`, a fine-grained personal access token or GitHub App token
  with write access to repository contents

The report commit uses `WEAVE_GITHUB_TOKEN` instead of the workflow-generated
`GITHUB_TOKEN`. GitHub therefore treats it as an ordinary authenticated push and
starts the follow-up pull-request checks automatically. The guard recognizes the
report-only commit, skips the expensive second LLM audit, and lets normal CI
validate the resulting branch state.

The workflow intentionally accepts secrets only on same-repository pull-request
branches. It does not use `pull_request_target`, because executing untrusted fork
code with the LLM or repository-write credential would expose those secrets.
Repositories that consume Loupe separately need their own selected repository or
organization secrets.
