# Contributing

Thanks for contributing to weave-loupe. This document describes how we
collaborate on the project. Start with the commit rules below; more
guidelines will be added as the project grows.

## Development setup

```sh
uv sync --group dev
```

## Quality checks

```sh
uv run ruff check .
uv run ruff format .
uv run mypy
uv run pytest
```

Run the full suite, not just files you touched — a change to shared or
module-level code can silently break an existing test elsewhere that never
appears in your diff. When you add a new CLI command or other entry point,
make sure the test suite actually invokes it end to end (not just its helper
functions): unit tests on the pieces can all pass while the wiring between
them is wrong.

If ruff or mypy report errors, fix only the ones your change introduced and
fold that fix into the commit that caused it. Leave pre-existing baseline
issues alone, even in a file you're already touching — that's scope creep,
not part of your story.

A local failure is not automatically a merge blocker. If it doesn't
reproduce in CI, check whether it's caused by a local tool-version gap (for
example, an older `bwrap` build without `--clearenv` support) rather than the
change itself before treating it as a defect.

## Commit rules

We prefer **small, targeted commits**. Each commit should tell **one
story**, not two. The files in a commit must be related and form a
single logical change.

Do not mix unrelated concerns in one commit (for example a feature and
an unrelated cleanup, or a fix and an unrelated rename). If work spans
more than one story, split it into separate commits.

Conversely, don't leave a commit only half-correct: if a change breaks an
existing test, or a chain of follow-up commits exists only to fix a mistake
introduced earlier in the same branch, fold the fix into the commit whose
mistake it corrects rather than leaving a separate `fix:`/`fix tests` commit
on top. The merged history should show each story working correctly on its
own, not the debugging trail that got there.

### Conventional Commits

Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/).

Subject (topic) line:

```text
<type>[optional scope]: <description>
```

Common types:

| Type | Use when |
| --- | --- |
| `feat` | A new user-facing capability |
| `fix` | A bug fix |
| `docs` | Documentation only |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `test` | Adding or updating tests |
| `chore` | Build, tooling, or maintenance work |
| `perf` | A performance improvement |

### Subject and body formatting

- **Subject maximum length:** 72 characters.
- **Body wrap:** wrap lines to 80 characters.
- Use the imperative mood in the subject (`add`, not `added` or `adds`).
- Do not end the subject with a period.

### Commit body

After a blank line following the subject, the body must start with a
**brief summary of the commit content (1–3 sentences)**.

If more detail is useful, put it **after** that summary as a
**bullet-pointed list**.

Example:

```text
feat(cli): add weavec version probe

Add a small CLI helper that reports the discovered weavec binary and
its version so other tools can share one lookup path.

- Prefer WEAVEC_BIN when set
- Fall back to PATH lookup
- Exit non-zero when weavec is missing
```

### Checklist before committing

- [ ] The commit is one logical story
- [ ] Included files belong to that story
- [ ] Subject uses Conventional Commits and is ≤ 72 characters
- [ ] Body opens with a 1–3 sentence summary
- [ ] Extra detail (if any) is a bullet list after the summary
- [ ] Body lines are wrapped to 80 characters

## Pull requests and merging

- Generated audit evidence (`docs/audit/*.md`, `*.audit.json` reports) is
  workflow-owned: the `weave-audit` GitHub Action regenerates it after a
  passing verdict. If rebasing a branch conflicts in these files — typically
  because another PR touching the same reports merged first — do not
  hand-merge the generated content. Drop the stale diff, push the real code
  changes, and wait for the workflow's own regeneration commit before
  merging.
- Merge by rebase (`gh pr merge --rebase`), not squash, so the commit
  boundaries you've cleaned up per the rules above are preserved in
  `master`'s history.
- If you rewrite a PR's history before merging, verify the resulting tree
  matches the original PR diff (aside from an intentional fix) before
  pushing — only commit boundaries should move.

### What blocks a merge

`master` is protected by a repository ruleset. Deterministic CI is the merge
authority; model-backed auditing is advisory evidence and never gates a merge.

The one required check is:

```text
test: lint, type-check & pytest
```

That job runs workflow-security validation, Ruff lint, Ruff format checking,
mypy, and the full pytest suite. A pull request cannot merge while it is queued,
running, failing, or cancelled.

`test: weave audit (LLM-verified)` is **not** required. Its absence, a model
outage, a rate limit, or a model concern must never decide whether code can
merge. Promoting it — or any other advisory workflow — to a required check is a
policy change to make deliberately, not a side effect of renaming a job.

The ruleset also blocks branch deletion and force pushes, requires linear
history, and requires changes to arrive through a pull request. It has no bypass
actors, so administrators follow the same path.

Approvals are not required, because the repository is developed by a single
maintainer working with agents; the gate that matters here is that the
deterministic check has actually finished and passed.

Branches are not required to be up to date with `master` before merging. That
would force a rebase and a full re-run every time an unrelated pull request
merged first, and it protects against a different failure class than the one
this ruleset exists for.

To inspect or change the ruleset:

```sh
# what GitHub currently enforces on master
gh api repos/ahojukka5/weave-loupe/rules/branches/master

# the ruleset itself, including bypass actors
gh api repos/ahojukka5/weave-loupe/rulesets
gh api repos/ahojukka5/weave-loupe/rulesets/<id>
```

If a required job is ever renamed, the ruleset's `required_status_checks`
context must be updated in the same change, or the gate silently stops
applying — a renamed job is simply a check that never reports.
