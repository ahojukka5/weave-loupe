# JSON Schema contracts

Weave Loupe publishes deterministic JSON Schema Draft 2020-12 contracts for its
public versioned JSON inputs and evidence outputs. The catalog is part of the
Python package and requires no schema registry or network access.

## Discover schemas

List the installed format names through the library:

```python
from weave_loupe.schemas import schema_formats

for format_name in schema_formats():
    print(format_name)
```

Retrieve one independent schema document, its deterministic JSON form, or its
installed source location:

```python
from weave_loupe.schemas import schema_document, schema_json, schema_location

schema = schema_document("weave-loupe-runtime-cases-v1")
text = schema_json("weave-loupe-runtime-cases-v1")
location = schema_location("weave-loupe-runtime-cases-v1")
```

The command-line equivalent is:

```bash
loupe schema weave-loupe-runtime-cases-v1
loupe schema weave-loupe-runtime-cases-v1 -o runtime-cases.schema.json
```

Every schema has a stable HTTPS `$id`, but the identifier is an identity rather
than a download requirement. Loupe always validates against the installed
catalog.

## Validate JSON

Loupe infers the schema from the top-level `format` field:

```bash
loupe validate-json examples/fibonacci_iterative.audit.json
```

Use `--format` for detached fragments or to assert an expected format explicitly:

```bash
loupe validate-json budget.json \
  --format weave-loupe-native-budget-v1 \
  --json-out validation.json
```

Exit codes are:

- `0` for a valid document;
- `2` for a structurally invalid document; and
- `1` when the file cannot be read, JSON cannot be decoded, or the requested
  format is unknown.

Diagnostics use stable JSON-style paths such as
`$.cases[0].expect.exit_code`. Machine-readable validation output uses
`weave-loupe-json-validation-v1`.

## Input validation order

External runtime sidecars are validated structurally before semantic parsing and
execution-specific checks. Loaded bundle manifests satisfy both their schema and
the existing fail-closed path, size, digest, symlink, and closed-directory
verification.

Schema validation does not replace semantic validation. Contracts that compare a
minimum with a maximum, enforce source order, verify hashes, execute native code,
or inspect cross-field compiler semantics remain explicit Python checks after the
structural gate.

## Published formats

The installed catalog includes current contracts for:

- bundle manifests and bundle-verification results;
- deterministic analysis and v1/v2 diff results;
- runtime sidecars and execution matrices;
- native and optimized-LLVM budgets and their result evidence;
- audit metadata and report-verification evidence;
- compiler-audit policies and sealed compiler-audit results;
- portable path identities; and
- schema-validation evidence itself.

Representative examples are available through `schema_example()` and
`schema_examples_document()`. CI validates every example and current generated
bundle, analysis, and diff documents against the catalog.

## Version evolution

A format version is a compatibility boundary.

Changes that remain backward compatible within the same version may:

- clarify descriptions without changing validation;
- loosen a constraint so every previously valid document remains valid;
- add an optional field when producers do not require consumers to understand
  it; or
- add a new schema for a new independently versioned format.

Changes require a new format version when they:

- add a required field;
- remove or rename a field;
- narrow a type, enumeration, range, pattern, or nested shape;
- change the meaning or units of an existing field;
- alter ordering, hashing, or canonicalization semantics; or
- make a document previously accepted by the published schema invalid.

When a format version changes, Loupe keeps the older schema available while its
compatibility parser remains supported. Migration notes must identify field
mapping, default behavior, and any information that cannot be represented in the
new version.

## Drift prevention

Schema changes must update the representative example and tests in the same
logical commit. CI rejects:

- a catalog format without an example;
- an example that does not validate;
- serializer output that no longer matches its schema;
- unknown required properties, wrong types, invalid enumerations, and malformed
  nested contracts; and
- non-deterministic schema serialization or identifiers.
