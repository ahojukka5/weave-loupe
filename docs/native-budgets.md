# Native optimization budgets

A semantically correct executable can still regress by retaining extra functions,
instructions, padding, or calls. Loupe can make selected final-code properties a
deterministic merge contract by adding `native_budget` to the source's adjacent
`.audit.json` sidecar.

```json
{
  "format": "weave-loupe-runtime-cases-v1",
  "native_budget": {
    "format": "weave-loupe-native-budget-v1",
    "max_program_owned_functions": 1,
    "max_reachable_program_functions": 1,
    "max_unreachable_program_functions": 0,
    "max_unreachable_program_instructions": 0,
    "functions": {
      "main": {
        "max_instructions": 2,
        "max_padding_instructions": 0,
        "max_direct_calls": 0,
        "max_indirect_calls": 0
      }
    }
  },
  "cases": [
    {
      "name": "native-result",
      "expect": {"exit_code": 55}
    }
  ]
}
```

The top-level sidecar format remains `weave-loupe-runtime-cases-v1` for backward
compatibility. Runtime cases and a native budget may appear together. A budget-only
sidecar is also valid.

## Supported limits

Global limits apply to program-owned functions discovered from optimized LLVM and
the linked executable:

- `max_program_owned_functions`
- `max_reachable_program_functions`
- `max_unreachable_program_functions`
- `max_unreachable_program_instructions`

Per-function limits under `functions.<symbol>` are:

- `max_instructions`
- `max_padding_instructions`
- `max_direct_calls`
- `max_indirect_calls`

Every limit is a non-negative integer and means “observed value must be less than
or equal to this number.” Unknown fields, negative values, empty function names,
and empty budgets are rejected as infrastructure errors rather than silently
ignored.

A named function is required to exist in the linked disassembly. Missing functions
fail the budget. This lets a contract assert that `main` remains present while a
global function-count limit prevents unwanted helpers from surviving.

## Gate behavior

Loupe evaluates the budget from deterministic disassembly metrics before applying
the final verdict. When the model returns `OK` but any limit is exceeded, Loupe
replaces it with:

```text
FAILED: native-budget-exceeded: ...
```

The generated failure evidence lists every exceeded limit. A budget cannot be
waived by model prose. The report output file is not published for a failed gate.

Budget evaluation fails closed when linked disassembly is unavailable or the
program-owned call graph is incomplete. Indirect calls make complete reachability
impossible and should normally be bounded to zero for small audit fixtures.

The sidecar SHA-256 already participates in report validity. Changing a budget,
adding one, or removing one invalidates the adjacent report and triggers a fresh
source-to-native audit.

## Choosing limits

Use the tightest limits justified by inspected native evidence.

For a constant-folded program whose complete body is `mov constant; ret`, an exact
two-instruction budget is a strong target-specific optimality contract. For a
dynamic program, use a small ceiling that preserves the necessary loop and
external calls while rejecting known forms of compiler overhead.

Budgets are maximums, so compiler improvements continue to pass. Tighten the
contract after an improvement when the smaller result has been reviewed and is
expected to remain stable.

A passing budget is not a mathematical proof that no better instruction sequence
exists. It proves that the current executable stays within an explicit,
hash-addressed quality envelope. Loupe still supplies the full disassembly,
optimized LLVM, optimization remarks, runtime observations, deterministic metrics,
and LLM review so humans can decide whether the envelope is sufficiently strict.

## Canonical corpus

The constant Fibonacci fixture requires exactly one program-owned `main`, two
non-padding instructions, no calls, and no dead code. The runtime-input fixture
allows the scalar loop plus its two required C-library calls while bounding the
instruction count, padding, and indirect calls.

These two contracts cover complementary regressions:

- failure to constant-fold or delete the loop;
- survival of dead helper functions;
- newly introduced call or dispatch overhead;
- stack or control-flow expansion large enough to exceed the reviewed ceiling; and
- loss of complete native reachability evidence.
