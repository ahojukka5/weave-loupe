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
uv run loupe audit examples/fibonacci_iterative.weave \
  --weavec /path/to/weavec \
  --model z-ai/glm-5.2 \
  --report-out examples/fibonacci_iterative.md
```

Every generated report records the UTC timestamp, audited source Git SHA, Loupe
and compiler Git SHAs when discoverable, compiler binary hash and version, source
and artifact hashes, model, operating system, kernel, CPU architecture and model,
logical CPU count, memory, Python version, and libc. The deterministic envelope
is produced by Loupe rather than delegated to the model.

The `Weave audit` workflow audits every added, copied, modified, or renamed
`.weave` file in a pull request, regardless of its directory. Changes to the audit
engine itself run the checked-in examples as a self-test. Each successful
`foo.weave` audit produces `foo.md`; reports are committed to the pull-request
branch only when every audited source passes. The workflow updates one persistent
PR comment with pass or failure details and uploads the complete result as an
artifact.

A report records the exact code commit that was audited. The following automated
commit adds only the generated report, so its parent is the reproducible audited
state rather than an unaudited source change.

Configure `WEAVE_LLM_ENDPOINT` and `WEAVE_LLM_API_KEY` as repository secrets (or
use `WEAVE_LLM_API_TOKEN` for the token compatibility name). The workflow
intentionally accepts secrets only on same-repository pull-request branches. It
does not use `pull_request_target`, because executing untrusted fork code with the
LLM secret would expose the credential. Repositories that consume Loupe separately
need their own selected repository or organization secrets.
