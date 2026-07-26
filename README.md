# weave-loupe

Tools to help in Weave compiler development.

The headline capability is **`loupe audit`**: compile a Weave program through
WIR to LLVM IR, then ask an LLM for a serious-issue and performance report
across all three artifacts.

## Setup

```sh
uv sync --group dev
```

Ensure `weavec` is on `PATH` (or set `WEAVEC_BIN`), and configure:

```sh
export WEAVE_LLM_ENDPOINT=https://integrate.api.nvidia.com/v1
export WEAVE_LLM_API_KEY=...
```

## Usage

```sh
uv run loupe <command>
```

### audit

```sh
uv run loupe audit examples/fibonacci_iterative.weave
```

The prompt includes `.weave`, `.wir`, and `.ll` by default. Optional flags:
`--model`, `--weavec`, `--wir-out`, `--llvm-out`, `--max-tokens`, `--verbose`.

#### Example

Audit the bundled iterative Fibonacci program:

```sh
uv run loupe audit examples/fibonacci_iterative.weave
```

Example report (model `z-ai/glm-5.2`):

````markdown
# Weave Loupe Audit Report

## Summary
The emitted LLVM IR is functionally correct and free of undefined behavior, but it is not performance-ready. The backend lowers mutable local variables to stack allocations (`alloca`) and uses a conservative loop-exit pattern that forces memory traffic at loop exits. This introduces redundant loads, stores, and identity-add instructions that a production-quality compiler would eliminate via `mem2reg` and instruction combining. The surface Weave and WIR are clean and accurately represent the algorithm; the suboptimal shape is introduced entirely during LLVM emission.

## Serious issues
None found.

## Performance opportunities

### Opportunity: Loop-carried variables kept on the stack instead of in SSA registers
- Impact: high
- Location: LLVM, `@fib` (variables `prev`, `curr`, `i`)
- Evidence: The backend emits `alloca` for `prev`, `curr`, and `i` in the `entry` block and immediately stores to them in `endif`. While the loop body correctly uses SSA `phi` nodes for the hot path, the exit block `while.exit-merge1` writes them back to the stack:
  ```llvm
  while.exit-merge1:
    store i32 %prev.phi1, ptr %prev.addr
    store i32 %curr.phi1, ptr %curr.addr
    store i32 %i.phi1, ptr %i.addr
  ```
  This is followed by a reload of `curr` in `while.end1`:
  ```llvm
  while.end1:
    %t3 = load i32, ptr %curr.addr
    ret i32 %t3
  ```
- Ideal shape: The variables should be promoted to SSA registers entirely. The exit block should return the final value directly from the `phi` node without any stack involvement:
  ```llvm
  while.exit-merge1:
    ret i32 %curr.phi1
  ```
- Suggestion: Run `mem2reg` or implement direct SSA promotion in the Weave backend for mutable local variables to eliminate the `alloca`, the exit-merge stores, and the final load.

### Opportunity: Redundant identity adds for variable updates
- Impact: medium
- Location: LLVM, `@fib` (`while.body1`)
- Evidence: The lowering of `set` statements emits identity additions instead of direct value copies or SSA renames:
  ```llvm
  %prev.next1 = add i32 %curr.phi1, 0
  %curr.next1 = add i32 %t2, 0
  ```
- Ideal shape: These should be direct assignments or eliminated entirely by SSA value forwarding:
  ```llvm
  %prev.next1 = or i32 %curr.phi1, 0  ; (or simply reuse %curr.phi1)
  %curr.next1 = or i32 %t2, 0         ; (or simply reuse %t2)
  ```
- Suggestion: The backend should emit a copy instruction (e.g., `or` with 0) or rely on `instcombine` to clean this up. Better yet, forward the value directly in the phi nodes if the `set` semantics allow it.

### Opportunity: Unnecessary empty latch block
- Impact: low
- Location: LLVM, `@fib` (`while.latch1`)
- Evidence: The loop contains an empty latch block that only branches back to the condition:
  ```llvm
  while.latch1:
    br label %while.cond1
  ```
- Ideal shape: The body should branch directly to the condition block:
  ```llvm
  while.body1:
    ...
    %i.next1 = add i32 %i.phi1, 1
    br label %while.cond1
  ```
- Suggestion: Collapse the latch block into the body block during LLVM emission to reduce basic block count and branch overhead.

### Opportunity: Redundant loop-preheader initialization loads
- Impact: low
- Location: LLVM, `@fib` (`while.pre1`)
- Evidence: The preheader loads values from the stack that were just stored in the `endif` block:
  ```llvm
  endif:
    store i32 0, ptr %prev.addr
    ...
  while.pre1:
    %prev.init1 = load i32, ptr %prev.addr
    ...
  ```
- Ideal shape: With SSA promotion, the constants would flow directly into the phi nodes:
  ```llvm
  while.cond1:
    %prev.phi1 = phi i32 [0, %endif], [%prev.next1, %while.body1]
  ```
- Suggestion: Eliminate the stack round-trip by promoting variables to SSA registers, allowing the phi nodes to take the constant initial values directly.

## Algorithmic notes
The algorithm is an optimal iterative O(n) time, O(1) space Fibonacci implementation. The structure is clear and avoids the exponential blowup of naive recursion. For the fixed input `n=10` (as called from `main`), the compiler could theoretically evaluate this entirely at compile time via constant propagation, but the algorithm itself is correct and efficient for general `n`. No algorithmic changes are needed.

## Suggested next steps
1. Implement or enable `mem2reg` promotion in the Weave backend to eliminate all `alloca`, stack stores, and loads for local variables in `@fib`.
2. Fix the lowering of `set` to avoid identity `add` instructions; use direct value forwarding or copy instructions.
3. Collapse the empty `while.latch1` block into `while.body1` to simplify the control flow graph.
4. Consider adding constant folding/propagation to evaluate the `fib(10)` call in `main` at compile time, reducing `@main` to a single `ret i32 55`.
````

## Quality checks

```sh
uv run ruff check .
uv run ruff format .
uv run mypy
uv run pytest
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution and commit rules.
