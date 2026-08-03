# GitHub Actions security model

Weave Loupe treats audit execution and report publication as separate trust
zones. Compiler output, pull-request code, model responses, and generated
artifacts are untrusted inputs until a publication job verifies their bounded
contract.

## Immutable workflow dependencies

Every remote `uses:` reference is pinned to a reviewed 40-character commit SHA.
The corresponding upstream major release tag remains beside the pin as a
maintenance note, for example:

```yaml
- uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262 # v4
```

`uv run python scripts/check_workflow_security.py` rejects mutable action tags,
missing release annotations, unexpected write permissions, unsafe credential
placement, read-only checkouts that retain credentials, and
`pull_request_target`.

## Pull-request boundary

The `Weave audit` workflow has repository read permission only.

For a same-repository pull request it may receive the configured LLM secret,
compile the current `weavec`, execute deterministic checks, and generate reports.
It never receives a repository publication credential and every checkout sets
`persist-credentials: false`.

A passing run stages only these publication inputs:

- the persistent pull-request summary;
- the explicit report path list;
- verified report files under `docs/audit/`;
- report-validity evidence; and
- compiler self-comparison evidence.

The artifact includes a SHA-256 manifest. The audit workflow cannot comment,
commit, or push.

`Publish Weave audit` is a separate `workflow_run` workflow loaded from the
default branch. It receives narrowly scoped `contents: write` and
`pull-requests: write` permissions. Before publishing, it:

1. requires a successful same-repository pull-request audit;
2. downloads only the current run's named artifact;
3. verifies every manifest entry;
4. rejects symbolic links, traversal, and paths outside `docs/audit/`;
5. confirms the branch still points to the audited SHA; and
6. copies only verified Markdown reports before committing.

The publisher does not install the project, run Python, execute compiler output,
or call repository scripts while a write token is available.

## Fork pull requests

Forks never receive model or publication secrets. They run the full hosted
quality suite through the `Fork quality` job. The audit workflow also publishes
a job summary describing the trusted path: a maintainer may mirror the commit to
a branch in this repository and rerun the model-backed audit.

This keeps a useful non-secret validation path without using
`pull_request_target`.

## Scheduled audits

Scheduled re-auditing follows the same separation:

- `re-audit` has read-only repository permissions and generates a manifested
  artifact;
- `publish-reports` receives only `contents: write`, verifies the artifact and
  audited `master` SHA, and commits approved report paths; and
- `publish-findings` receives no repository write permission and uses the
  cross-repository credential only inside the GitHub API step that updates the
  `weavec` issue.

The workflow-generated `GITHUB_TOKEN` publishes reports. The
`WEAVE_GITHUB_TOKEN` secret remains necessary only for writing findings to the
separate `ahojukka5/weavec` repository. Prefer a short-lived GitHub App
installation token; otherwise use a fine-grained token limited to issue write
access in that repository.

## Required secrets and variables

Same-repository model audits use:

- `WEAVE_LLM_ENDPOINT`;
- `WEAVE_LLM_API_KEY`, or the compatibility secret
  `WEAVE_LLM_API_TOKEN`; and
- optional variables `WEAVE_LLM_MODEL`, `WEAVE_LLM_MAX_TOKENS`, and
  `WEAVE_LLM_MAX_ATTEMPTS`.

Scheduled cross-repository findings additionally use `WEAVE_GITHUB_TOKEN` with
no content permission in Weave Loupe and only the required issue permission in
`weavec`.

## Reviewing dependency updates

When updating an action:

1. inspect the upstream release and changelog;
2. resolve the release tag to its full commit SHA;
3. update the SHA and adjacent release comment together;
4. run the workflow security policy and full quality suite; and
5. review permission and credential changes separately from functional changes.
