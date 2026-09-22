# Inspecting compiler evidence

Loupe is a compiler-engineering tool. A bundle answers what was compiled, with
which compiler, which intermediates were produced, and which objects correspond
across stages. Filenames are not identity.

## Capture

```sh
uv run loupe capture examples/fibonacci_iterative.weave \
  --output build/fibonacci.loupe
```

Evidence levels:

| Level | Retained by default |
| --- | --- |
| `lightweight` | sources, logs, diagnostics, trace, build manifest, capabilities |
| `standard` | plus WIR, raw LLVM, optimized LLVM, assembly, disassembly, remarks |
| `full` | plus the native executable |

`--include-executable` is an independent retention override. It does not
rename the declared evidence level. `standard --include-executable` remains
`standard` and keeps the binary. `lightweight --include-executable` is a
lightweight bundle plus that binary: IR and native emits stay omitted, and
the compiler command stays the lightweight public `weavec build` shape.
`--evidence-level full` implies the executable (`retention.level` is `full`
and `include_executable` is true).

The compiler command is still the public `weavec build` interface. Loupe does
not invent extra stage boundaries; it records the compiler's own artifacts:

`source → WIR → LLVM → optimized LLVM → native → runtime`

Runtime observations are usually absent from `capture`. Their absence is
recorded as `unavailable`, not guessed.

## Identity

New bundles declare `compilation.identity` with:

- SHA-256 of the compiler binary;
- version / git identity when `weavec --version` provides it;
- capability-registry hash matching `compiler_capabilities`;
- target triple when the build manifest includes one.

Two builds are not comparable merely because both contain `program.ll`.
Compare hashes and declared lineage.

## Inspect and analyze

```sh
uv run loupe inspect build/fibonacci.loupe
uv run loupe inspect build/fibonacci.loupe --stage llvm --json-out llvm.json
uv run loupe inspect build/fibonacci.loupe --view source_ir --json-out ir.json
uv run loupe analyze build/fibonacci.loupe --markdown-out build/fibonacci.md
```

`inspect` lists stages, completeness gaps, and identity. `analyze` adds
existing deterministic structural checks and explanation paths such as
`source → WIR` when WIR is invalid. Those paths cite retained artifacts. They
do not replace LLVM's verifier.

## Compare good and bad builds

```sh
uv run loupe diff build/good.loupe build/bad.loupe --json-out build/cmp.json
```

The v2 document includes `localization`:

- `matched_inputs` — source identities agree;
- `first_changed_stage` — earliest stage whose retained artifacts diverge;
- unchanged stages, missing evidence, diagnostic/runtime change flags;
- a caveat that the first changed stage is localization evidence, not a proven
  defect origin.

Incomplete bundles are marked incomplete. Missing evidence is a finding.

## Information conditions

`--view` projects review conditions over one bundle:

1. `source_tests` — sources, logs, diagnostics, manifest, capabilities
2. `source_ir` — plus WIR and LLVM
3. `full` — every retained artifact
4. `deterministic` — same objects; analysis is added by `loupe analyze`
5. `model` — a structured subset for later model review

Budgets report object counts, raw bytes, and UTF-8 text bytes. A richer view
is not automatically a better diagnosis.

## Historical bundles

Bundles captured before lineage existed still verify. Loupe infers stages from
known artifact names and marks `inferred: true`. It does not rewrite the
manifest to invent artifacts the old compiler never published.

## Worked comparison

1. Capture a known-good compiler: `loupe capture ... -o good.loupe`
2. Capture a suspected-bad compiler on the same sources: `-o bad.loupe`
3. `loupe inspect` each bundle and confirm completeness.
4. `loupe diff good.loupe bad.loupe` and read `localization.first_changed_stage`
5. `loupe analyze` the bad bundle for explanation paths and structural findings.
6. Open the HTML report if you need the raw artifacts next to the summary.

This is ordinary compiler debugging. The research comparison in
`` reuses the same capture, views, and localization; it
does not replace this workflow.
