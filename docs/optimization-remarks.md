# LLVM optimization remark analysis

LLVM optimization records are YAML streams emitted by compiler passes. Loupe
parses this evidence into `weave-loupe-optimization-remarks-v1` so optimization
quality can be queried, compared, rendered, and gated without depending on LLVM
bindings or a live toolchain.

The raw YAML artifact remains unchanged in the portable bundle. The normalized
analysis is a derived deterministic projection.

## Normalized record

Each remark contains:

- `category`: `passed`, `missed`, `analysis`, `failure`,
  `analysis-fp-commute`, or `unsupported`;
- `pass`, `name`, and `function`;
- optional `location` with file, line, and column;
- optional numeric `hotness`;
- ordered normalized `arguments` and their human-readable `message`;
- stable `unknown_fields`; and
- a SHA-256 `identity` over canonical normalized content.

LLVM root tags such as `!Passed` and `!Missed` determine the category. Loupe also
accepts explicit `RemarkType` or `Type` fields and older records whose `Name` is
the category. Unknown tags remain visible as unsupported records instead of being
silently discarded.

The parser handles multi-document YAML, quoted scalars, Unicode, missing debug
locations, and nested unknown fields. Malformed YAML and unsupported document
shapes produce indexed diagnostics and make the analysis invalid.

## Summaries

The analysis counts remarks by category, pass, function, and pass/category pair.
It also publishes the twenty highest-value missed optimizations. Missed remarks
are ordered by descending hotness and then by function, pass, name, and stable
identity.

HTML bundle reports group these missed optimizations by function and pass. The
complete normalized records remain available in an expandable JSON section.

## Deterministic diffs

`weave-loupe-diff-v2` compares normalized record multisets rather than raw YAML
bytes. Formatting, document ordering, quoting, and unknown-field ordering do not
create false semantic changes.

The diff publishes:

- evidence availability and parser-validity changes;
- before, after, and delta counters by category, pass, and function;
- complete added and removed normalized records; and
- classified change entries in the global deterministic change list.

A newly added `missed` or `failure` remark is a quality warning. Removing a
`passed` remark is also a quality warning. Unsupported records are errors because
the compiler-quality signal cannot be interpreted reliably.

## Compiler-audit policy

A `weave-loupe-compiler-audit-policy-v1` document may include an
`optimization_remarks` object:

```json
{
  "format": "weave-loupe-compiler-audit-policy-v1",
  "optimization_remarks": {
    "required": [
      {
        "category": "passed",
        "pass": "inline",
        "name": "Inlined"
      }
    ],
    "forbidden": [
      {
        "category": "missed",
        "pass": "loop-vectorize"
      }
    ],
    "forbid_added": [
      {
        "category": "failure"
      }
    ],
    "forbid_removed": [
      {
        "category": "passed",
        "pass": "inline"
      }
    ]
  }
}
```

The four rule lists have distinct meanings:

- `required` selectors must match at least one candidate record;
- `forbidden` selectors must match no candidate record;
- `forbid_added` selectors must match no record added relative to baseline; and
- `forbid_removed` selectors must match no record removed relative to baseline.

Selectors may use exact `category`, `pass`, `name`, and `function` fields plus a
`message_contains` substring. All supplied fields must match the same record.
Empty selectors, unknown fields, invalid categories, and non-string values are
configuration errors.

An invalid baseline optimization record is an infrastructure failure. When the
baseline is valid and the candidate becomes invalid, the audit fails as a quality
regression. A model review cannot override deterministic remark-policy failures.

## Audit prompts

Normalized optimization remarks are included in the complete analysis JSON given
to audit reviewers. The original YAML is supplied separately, so a reviewer can
cross-check the normalized summary against exact compiler evidence while the
deterministic gate remains authoritative.
