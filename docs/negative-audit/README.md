# Negative audit corpus

This directory contains intentionally invalid Weave inputs and workflow-generated
reports proving that `weavec` rejects them in the declared way.

Each case consists of:

- one or more source files listed by the contract;
- an adjacent `*.audit.failure.toml` contract; and
- a workflow-owned `*.md` report created only after the contract passes.

The contract is strict and deterministic. It records:

- the ordered compiler inputs;
- the exact nonzero compiler exit code and failure phase;
- the exact diagnostic count, code, severity, source index, line and column span,
  and source text covered by the compiler byte span;
- optional semantic fields such as operand role, symbol, span origin, and analysis
  completeness; and
- artifact names that must not be published after the rejected compilation.

The audit captures a normal portable bundle, validates the structured diagnostics,
proves that no forbidden native artifact exists, and emits a sealed Loupe report.
No model request is made for an expected failure: the report records
`deterministic-expected-failure` review provenance explicitly while preserving the
configured model and endpoint identities for freshness checks.

## Coverage matrix

| Case | Primary coverage | Deterministic assertions |
|---|---|---|
| `missing_module` | explicit-module import resolution failure | exit 10, frontend phase, exact `frontend.module.import-missing-module` span over `absent`, no executable, assembly, or disassembly |

Generated reports are not hand-maintained. Change the source or its contract and
let the trusted pull-request audit publish fresh evidence after all checks pass.
The positive source-to-native corpus remains under [`docs/audit`](../audit/README.md).
