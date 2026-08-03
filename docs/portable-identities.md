# Portable source and sidecar identities

Weave Loupe publishes content identities, not workstation layout. Source paths in
bundles, audit reports, compiler comparisons, prompts, and request hashes use the
`weave-loupe-portable-path-v1` contract. Absolute paths remain local execution
state and are not part of published evidence.

## Root selection

Loupe selects one audit root in this order:

1. `--audit-root`, when provided;
2. a Git worktree shared by every source; or
3. the common parent directory of all sources.

Files below that root use NFC-normalized, repository-relative POSIX paths such as
`src/examples/fibonacci.weave`. Path separators therefore do not depend on the
host operating system.

```sh
uv run loupe audit src/examples/fibonacci.weave \
  --audit-root . \
  --weavec /path/to/weavec \
  --model z-ai/glm-5.2
```

The selected root itself is never written to the bundle or report. Evidence may
record whether the root was explicit, Git-derived, or a common parent, but not its
host location.

## Inputs outside the root

An input that resolves outside the audit root must receive an explicit logical
name. Repeat `--source-name` in the same order as the positional sources:

```sh
uv run loupe capture ../fixtures/a.weave ../fixtures/b.weave \
  --audit-root . \
  --source-name fixtures/a.weave \
  --source-name fixtures/b.weave \
  --output build/example.loupe
```

The public identities become `external/fixtures/a.weave` and
`external/fixtures/b.weave`. The number of logical names must equal the number of
sources. Empty, absolute, parent-traversing, or control-character-containing
names are rejected.

An adjacent `*.audit.json` sidecar follows the source identity. For example,
`external/fixtures/a.weave` has sidecar identity
`external/fixtures/a.audit.json`.

## Symlinks and collisions

Loupe resolves source paths before deciding whether they are inside the root. A
symlink that escapes the root is therefore treated as an external input and
requires an explicit logical name. This prevents a repository-local symlink from
silently publishing or trusting a file elsewhere on the machine.

Portable names are Unicode NFC-normalized and compared with Unicode case folding.
Names that would collide on a case-insensitive filesystem are rejected even when
the current host distinguishes them.

## Published evidence

The portable identity is used in:

- `bundle.json` source entries and compiler command projections;
- runtime, native-budget, and optimized-LLVM sidecar evidence;
- audit metadata and the stable `Audited inputs` report section;
- compiler-audit JSON and Markdown;
- model prompts, deterministic review summaries, and request hashes; and
- report-validity comparisons.

Before a report is sealed, Loupe also replaces known audit-root, home-directory,
and GitHub runner workspace prefixes in textual compiler evidence. Explicit local
`--wir-out` and `--llvm-out` files retain the raw compiler bytes because they are
local debugging outputs rather than published attestations.

## Relocation and compatibility

A report with a portable identity verifies in another clean checkout when the
repository-relative path, source order, content hash, and sidecar hash are
unchanged. Moving the checkout does not make the report stale and does not alter
the model request hash.

Existing reports that recorded absolute paths remain readable. The verifier tries
repository-relative suffixes and content hashes so a unique matching file in a
moved checkout can satisfy the legacy identity. New reports always use the
portable contract.

Content and ordering checks remain fail closed. Relocation compatibility does not
permit a changed source, changed sidecar, ambiguous hash match, reordered source
set, or symlink escape to pass verification.
