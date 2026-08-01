# Native optimization budgets

A semantically correct executable can still regress by retaining extra functions,
instructions, padding, or calls—or by losing native structure that must remain
dynamic. Loupe can make selected final-code properties a deterministic merge
contract by adding `native_budget` to the source's adjacent `.audit.json` sidecar.

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
        "max_instructions": 32,
        "max_padding_instructions": 1,
        "max_direct_calls": 2,
        "max_indirect_calls": 0,
        "min_backward_conditional_branches": 1,
        "max_backward_conditional_branches": 1,
        "required_direct_calls": [
          "atoi@plt",
          "getenv@plt"
        ]
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

## Supported global limits

Global limits apply to program-owned functions discovered from optimized LLVM and
the linked executable:

- `max_program_owned_functions`
- `max_reachable_program_functions`
- `max_unreachable_program_functions`
- `max_unreachable_program_instructions`

## Per-function contracts

Maximum limits under `functions.<symbol>` are:

- `max_instructions`
- `max_padding_instructions`
- `max_direct_calls`
- `max_indirect_calls`
- `max_backward_conditional_branches`

A dynamic function may additionally require:

- `min_backward_conditional_branches`
- `required_direct_calls`

Every numeric contract is a non-negative integer. A minimum must not exceed its
matching maximum. `required_direct_calls` is a duplicate-free list of exact
normalized targets from the linked disassembly.

Backward conditional branches are control-flow edges whose direct target address
is lower than the branch instruction address. Loupe recognizes x86-64 and AArch64
through architecture-specific classifiers. This is a structural observation, not
a source-level guess: one required backedge proves that a native loop remains in
the linked function.

Direct-call targets use the symbol shown by the disassembler after removing a
function offset such as `+0x20`. On Linux x86-64, external calls commonly appear as
`getenv@plt` and `atoi@plt`. Mach-O public symbols have one ABI leading underscore
removed so they match LLVM identities. Compiler-created suffixes such as `.cold`
and `.llvm.123` remain distinct.

Contracts remain target-sensitive even though x86-64 and AArch64 share normalized
metric names. Instruction count and external-symbol conventions may change with
the operating system, object format, linker, architecture, or disassembler. Review
and update tight budgets intentionally when changing those inputs.

Unknown fields, negative values, empty function names, duplicate required calls,
and empty contracts are rejected as infrastructure errors rather than silently
ignored. A named function is required to exist in the linked disassembly.

## Gate behavior

Loupe evaluates the contract from deterministic disassembly metrics before
applying the final verdict. When the model returns `OK` but any maximum is
exceeded, minimum is unmet, or required call target is missing, Loupe replaces it
with:

```text
FAILED: native-budget-exceeded: ...
```

The generated failure evidence lists every violated requirement. Model prose
cannot waive the deterministic result, and the report output file is not published
for a failed gate.

Evaluation fails closed when linked disassembly is unavailable, its architecture
is unsupported or contradictory, symbols cannot be normalized safely, the parser
cannot recover functions reliably, or the program-owned call graph is incomplete.
Indirect calls make complete reachability impossible and should normally be bounded
to zero for small audit fixtures.

Unsupported targets do not produce synthetic zero-valued metrics. The analysis
records `supported: false` and a clear `failure_reason`, while configured native
budgets reject incomplete reachability. See the
[architecture-aware native analysis guide](native-analysis.md) for the parser and
evidence contract.

The sidecar SHA-256 participates in report validity. Changing a limit or structural
requirement, adding a budget, or removing one invalidates the adjacent report and
triggers a fresh source-to-native audit.

## Choosing contracts

Use the tightest contract justified by inspected native evidence.

For a constant-folded program whose complete body is `mov constant; ret`, an exact
two-instruction maximum plus zero backward conditional branches is a strong
target-specific optimality contract.

For a dynamic program, combine ceilings with positive evidence that required work
still exists. A small instruction ceiling alone does not prove that an input-
dependent loop survived; a compiler bug or hard-coded lookup might also be small.
Require the expected loop backedge and external call targets, then use runtime
cases to verify observable behavior over representative inputs.

Maximums allow compiler improvements to pass. Structural minima preserve required
dynamic behavior. Tighten a ceiling after an improvement when the smaller result
has been reviewed and is expected to remain stable.

A passing contract is not a mathematical proof that no better instruction sequence
exists. It proves that the current executable stays within an explicit,
hash-addressed quality envelope and retains declared native structure. Loupe still
supplies the full disassembly, optimized LLVM, optimization remarks, runtime
observations, deterministic metrics, and LLM review so humans can judge whether
the contract is sufficiently strict.

## Canonical corpus

The constant Fibonacci fixture requires exactly one program-owned `main`, two
non-padding instructions, no calls, no dead code, and no backward conditional
branches.

The runtime-input fixture requires exactly one backward conditional branch in
`main`, proving the scalar recurrence loop survives, plus direct calls to
`getenv@plt` and `atoi@plt`. It also bounds instruction count, padding, function
count, dead code, and indirect calls. Nine runtime cases independently check the
linked executable's observable behavior.

Together, the contracts cover:

- failure to constant-fold or delete the constant loop;
- accidental deletion or replacement of the required dynamic loop;
- loss or substitution of required external input handling;
- survival of dead helper functions;
- newly introduced call or dispatch overhead;
- stack or control-flow expansion large enough to exceed the reviewed ceiling; and
- loss of complete native reachability evidence.
