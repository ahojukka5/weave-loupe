# `weave-loupe-bundle-v1`

A bundle is an ordinary directory. It can be archived, copied, reviewed, or
checked into an external evidence store without requiring Loupe to read compiler
temporary directories.

```text
example.loupe/
├── bundle.json
├── sources/
│   └── 000-input.weave
├── artifacts/
│   ├── program.wir
│   ├── program.ll
│   ├── diagnostics.json
│   ├── trace.json
│   └── build-manifest.json
└── logs/
    ├── stdout.txt
    └── stderr.txt
```

The optional executable is stored only when `capture --include-executable` is
used.

## Manifest guarantees

`bundle.json` records:

- format identifier `weave-loupe-bundle-v1`;
- ordered source inputs and copied bundle paths;
- SHA-256 digest and byte size for every copied source, artifact, and new log
  entry;
- the portable public `weavec build` command shape;
- compiler exit code;
- published artifact and log paths.

No timestamp is required, so repeated capture of identical compiler output does
not gain presentation-only nondeterminism.

Current captures represent logs as the same `{path, size, sha256}` file entries
used by sources and artifacts. The verifier also accepts older v1 manifests
where `logs.stdout` and `logs.stderr` are path strings. Those legacy log bytes
cannot be authenticated because the old manifest did not record their hashes;
the machine-readable result lists them in `legacy_unhashed_logs`.

## Integrity verification

Every trust boundary calls the same fail-closed verifier. `loupe report`,
`loupe diff`, and `loupe audit` cannot consume a bundle until verification
succeeds.

Run verification directly with:

```sh
uv run loupe verify-bundle build/fibonacci.loupe \
  --json-out build/fibonacci-bundle-verification.json
```

The command exits:

- `0` when the bundle is valid;
- `2` when one or more integrity problems are found;
- `1` when verification evidence cannot be written.

The `weave-loupe-bundle-verification-v1` JSON result contains every detected
problem in deterministic order. Verification checks:

- the complete manifest shape and supported format;
- compiler metadata and ordered source indices;
- canonical relative POSIX paths;
- duplicate and conflicting path declarations;
- regular-file type, declared byte size, and SHA-256 identity;
- missing success artifacts according to the compiler exit code;
- required stdout and stderr logs;
- undeclared files in a closed bundle.

The verifier rejects absolute paths, drive-qualified paths, path traversal,
non-canonical separators, NUL bytes, symbolic links at any declared path
component, non-regular files, missing files, and duplicate JSON object keys.

A closed bundle contains only `bundle.json`, declared files, and their
directories. Evidence-store metadata can be permitted explicitly with
`--allow-undeclared`; declared content is still verified normally.

## Successful and failed builds

A successful compiler run must publish WIR, raw and optimized LLVM, assembly,
linked disassembly, optimization remarks, diagnostics, trace, and build
manifest. The executable remains optional because capture omits it unless
`--include-executable` is requested.

The compiler publishes WIR after frontend success and LLVM after backend
success. Failed runs therefore require only the ordered sources and compiler
logs; Loupe records and verifies whichever artifacts reached publication. This
keeps failed builds inspectable without pretending that later pipeline stages
must exist.

## Portability

All authenticated identities are based on bundle-relative paths and file bytes,
not the checkout location. A valid bundle can therefore move to another
directory or machine without becoming invalid.

HTML reports escape all source and artifact contents, include no remote
resources, and use no JavaScript. Raw compiler artifacts remain unchanged inside
the bundle.
