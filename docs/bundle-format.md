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
- SHA-256 digest and byte size for every copied source and artifact;
- the portable public `weavec build` command shape;
- compiler exit code;
- published artifact and log paths.

No timestamp is required, so repeated capture of identical compiler output does
not gain presentation-only nondeterminism.

## Failed builds

The compiler publishes WIR after frontend success and LLVM after backend
success. Loupe records whichever artifacts exist after the command returns.
Therefore a backend failure can still leave inspectable WIR, and a codegen or
link failure can still leave inspectable WIR and LLVM.

## Security and portability

Bundle paths are resolved beneath the bundle root before reading. HTML reports
escape all source and artifact contents, include no remote resources, and use no
JavaScript. Raw compiler artifacts remain unchanged inside the bundle.
