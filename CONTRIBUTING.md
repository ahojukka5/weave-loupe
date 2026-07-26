# Contributing

Thanks for contributing to weave-loupe. This document describes how we
collaborate on the project. Start with the commit rules below; more
guidelines will be added as the project grows.

## Development setup

```sh
uv sync
```

## Commit rules

We prefer **small, targeted commits**. Each commit should tell **one
story**, not two. The files in a commit must be related and form a
single logical change.

Do not mix unrelated concerns in one commit (for example a feature and
an unrelated cleanup, or a fix and an unrelated rename). If work spans
more than one story, split it into separate commits.

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
