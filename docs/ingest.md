# Retained compiler evidence ingestion

`loupe ingest` converts an already completed `weavec` invocation into the same
portable `weave-loupe-bundle-v1` format produced by `loupe capture`:

```bash
loupe ingest \
  --request build/ingest-request.json \
  --output build/program.loupe
```

The command performs no compilation, linking, executable launch, runtime case,
or model request. It only validates declared files, copies their exact bytes
into the canonical bundle layout, verifies the completed closed bundle, and
publishes it atomically.

## Request contract

The request is a UTF-8 JSON document with format
`weave-loupe-ingest-request-v1`. All file paths are POSIX-style paths relative
to the directory containing the request.

```json
{
  "format": "weave-loupe-ingest-request-v1",
  "source_identity": {
    "format": "weave-loupe-portable-path-v1",
    "root_kind": "git"
  },
  "compiler": {
    "binary": "weavec",
    "command": [
      "weavec",
      "build",
      "src/demo.weave",
      "-o",
      "out/program",
      "--emit-wir",
      "out/program.wir",
      "--diagnostics-json",
      "out/diagnostics.json"
    ],
    "exit_code": 0,
    "execution": {
      "exit_code": 0,
      "termination_reason": "exited"
    }
  },
  "sources": [
    {
      "path": "src/demo.weave",
      "size": 23,
      "sha256": "<64 lowercase hexadecimal characters>",
      "input": "src/demo.weave",
      "identity": {
        "format": "weave-loupe-portable-path-v1",
        "path": "src/demo.weave",
        "scope": "root",
        "symlinked": false
      }
    }
  ],
  "artifacts": {
    "compiler_capabilities": {
      "path": "out/compiler-capabilities.json",
      "size": 4096,
      "sha256": "<64 lowercase hexadecimal characters>"
    },
    "wir": {
      "path": "out/program.wir",
      "size": 512,
      "sha256": "<64 lowercase hexadecimal characters>"
    },
    "diagnostics": {
      "path": "out/diagnostics.json",
      "size": 64,
      "sha256": "<64 lowercase hexadecimal characters>"
    }
  },
  "logs": {
    "stdout": {
      "path": "out/stdout.txt",
      "size": 9,
      "sha256": "<64 lowercase hexadecimal characters>"
    },
    "stderr": {
      "path": "out/stderr.txt",
      "size": 0,
      "sha256": "<64 lowercase hexadecimal characters>"
    }
  }
}
```

Every declared source and produced compiler artifact must occur exactly once in
the retained compiler command and sources must occur in the same order. The
capability registry is retained separately because it comes from the bounded
`weavec capabilities --json` negotiation rather than the build invocation.

The accepted compiler artifact names are:

- `compiler_capabilities`
- `executable`
- `wir`
- `llvm`
- `optimized_llvm`
- `assembly`
- `disassembly`
- `optimization_record`
- `diagnostics`
- `trace`
- `build_manifest`

A compiler exit code of zero must provide the complete successful evidence set
required by `weave-loupe-bundle-v1`. A nonzero exit may provide a phase-scoped
subset, such as capabilities, diagnostics, trace, logs, and any intermediate
artifacts produced before failure. Ingestion success is independent of the
retained compiler exit code.

## Source producer metadata

A source may carry bounded additive metadata:

```json
{
  "producer": "weave-jacquard",
  "revision": {
    "id": "abc123",
    "repository": "ahojukka5/weave-jacquard",
    "ref": "refs/heads/main"
  },
  "document": {
    "id": "document-7",
    "version": "3"
  },
  "node_map": {
    "path": "out/document-7.node-map.json",
    "size": 1024,
    "sha256": "<64 lowercase hexadecimal characters>"
  }
}
```

Loupe retains a node map as a hashed bundle artifact and replaces the request
path with a stable artifact reference in source metadata. Revision, document,
producer, and node-map identity then appear in deterministic analysis JSON and
therefore in generated reports and diffs. Loupe does not interpret
Jacquard-specific internals.

## Fail-closed validation

Ingestion rejects the request before publication when any of these checks fail:

- request shape, field allowlist, item count, or byte limit;
- duplicate JSON keys;
- absolute, backslash, parent-traversal, escaping, or symlinked paths;
- missing or non-regular files;
- duplicate paths or hard-linked duplicate inputs;
- declared size or SHA-256 mismatch;
- compiler binary, exit-code, command-path, or source-order inconsistency;
- incompatible `weavec-capabilities-v1`;
- invalid WIR core, diagnostics, trace, or build-manifest protocol;
- incomplete successful-build evidence;
- final bundle schema, path, hash, or closed-directory verification.

No destination is replaced until the temporary canonical bundle has passed all
checks.

## Offline schema

Print or save the installed request schema:

```bash
loupe schema weave-loupe-ingest-request-v1
loupe schema weave-loupe-ingest-request-v1 \
  --output build/weave-loupe-ingest-request-v1.schema.json
```

Validate a request without reading any declared artifact:

```bash
loupe validate-json build/ingest-request.json
```

`validate-json` checks the JSON contract. `loupe ingest` additionally performs
all filesystem, byte-identity, protocol, command, and final-bundle checks.
