# Compiler capability negotiation

Loupe treats the final user-facing `weavec` executable as the authority for the
Weave language and compiler protocols. Before any uncached compiler binary is
used for capture or differential audit, Loupe runs:

```sh
weavec capabilities --json
```

The compiler must emit deterministic `weavec-capabilities-v1`. Loupe does not
infer compatibility from `--help`, filenames, repository layout, bootstrap
products, or successful process startup.

## Bounded handshake

Capability discovery runs through the same process supervisor used for compiler
and runtime work, with its own conservative limits:

- five-second wall-clock ceiling;
- one-MiB stdout and stderr ceiling;
- bounded CPU, address space, file output, and process count;
- complete process-group termination on timeout or overflow.

The configured compiler is hashed through a no-follow regular-file descriptor
before the request. The binary is hashed again afterward. Replacement or mutation
during negotiation fails closed.

A validated immutable registry is cached by exact compiler SHA-256. Replacing the
binary at the configured path therefore forces a new handshake.

## Compatibility policy

Loupe requires:

- final public compiler variant `weavec`;
- `weave-surface-v1` and `weave-surface-grammar-v1`;
- WIR core versions 2 and 3;
- `weavec-capabilities-v1`;
- `weavec-build-manifest-v1`;
- `weavec-diagnostics-v1`;
- `weavec-compilation-trace-v1`;
- a stable `capabilities` command;
- a stable `build` command advertising the build protocols;
- one installed native default target;
- optimization level `O3`;
- native CPU selection.

Unknown additive object fields remain compatible. Unknown top-level formats,
incompatible required protocol versions, missing commands, invalid references,
unsupported public variants, malformed targets, and inconsistent surface-form
registries fail before source compilation.

Registry version 1 does not advertise every `weavec build` output flag as a
separate machine-readable entry. Loupe therefore records its complete capture
profile and binds it to the strongest contract expressible by version 1: the
stable public build command, the supported WIR core versions, the three
versioned JSON protocols, the
native target, `O3`, and native CPU selection. A future additive registry field
may make individual output negotiation explicit without weakening this baseline.

## Evidence identity

Every new `weave-loupe-bundle-v1` stores the exact validated registry bytes at:

```text
artifacts/compiler-capabilities.json
```

The ordinary bundle manifest records its byte count and SHA-256. The stable bundle
format does not need a new version because artifact names are already extensible.
Loading a new bundle verifies both its normal closed-bundle integrity and the
retained registry semantics.

Compiler-audit baseline and candidate evidence additionally expose a path-free
identity containing:

- registry SHA-256 and byte count;
- compiler version;
- surface and grammar identifiers;
- WIR core version;
- required protocol versions;
- selected target and runtime class;
- the complete Loupe capture profile.

The live build result also binds the exact compiler binary SHA-256 and byte count.
A retained standalone bundle cannot reconstruct that binary hash from registry
bytes alone, so it does not invent one.

## Offline validation

A saved registry can be validated without network or compiler access:

```sh
python -m weave_loupe.compiler_capabilities weavec-capabilities.json
```

A valid document prints its normalized path-free compatibility identity as JSON.
Invalid UTF-8, malformed JSON, incompatible fields, missing protocols, and
unsupported targets return status 2 with a stable `WEAVEC_*` error on stderr.

## Ownership boundary

`weavec` owns the registry and all language, WIR, target, runtime, build,
diagnostic, trace, and artifact semantics. Loupe only validates that public
contract and consumes the resulting evidence. Loupe does not import compiler
implementation modules or depend on `weavec0`, `weavec1`, `weavec-bootstrap`, or
Jacquard.
