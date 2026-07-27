# Weave Loupe Audit Report

## Verdict

- **Status:** OK
- **Code:** none
- **Reason:** No blocking defect found.

## Reproducibility

- **Audit timestamp (UTC):** `2026-07-27T10:43:03+00:00`
- **Audited source Git SHA:** `bed7a38ca994211b61646cf5fc95e8edec1ef7d2`
- **Source tree state:** `clean`
- **Weave Loupe Git SHA:** `bed7a38ca994211b61646cf5fc95e8edec1ef7d2`
- **weavec Git SHA:** `dbe9e379f663d6dbc7627b3acf21c6d1452db425`
- **weavec binary SHA-256:** `44da49a96942174d8f29dca9ca5582d5ef330e272c6b5de622d66162f500f6ac`
- **weavec version:** `unavailable`
- **LLM model:** `z-ai/glm-5.2`
- **GitHub run ID:** `30259093396`
- **GitHub workflow SHA:** `8385b3ac248f5771385257871075a3189107f32a`

## Machine and running conditions

- **Operating system:** `Ubuntu 24.04.4 LTS`
- **Kernel:** `Linux 6.17.0-1020-azure`
- **Architecture:** `x86_64`
- **CPU:** `INTEL(R) XEON(R) PLATINUM 8573C`
- **Logical CPUs:** `4`
- **Memory:** `16765386752` bytes
- **Python:** `3.12.13`
- **libc:** `glibc 2.39`

## Audited inputs

- `examples/fibonacci_iterative.weave` — SHA-256 `f0b0307bf52ed886b7ee63a4aa952f327204bc79530dea0abe013f24369dd04f`

## Captured evidence

- `assembly` — SHA-256 `730fac8186d8bc25f4032e836d77c1f94dc3c7b1ffe881974e2064880963da31`
- `build_manifest` — SHA-256 `dc44aad5daa334cac2dd139cb1f2615afb68348752343be4dd821a62381716e4`
- `diagnostics` — SHA-256 `a40b573053cda943c381742ad672108b1c8985ecc97e2f21dfa604094e31ff63`
- `disassembly` — SHA-256 `20b493cf2dbbede5b47a5bac08af3043eb8675a5fdc176fa9a7f992b102dd8e0`
- `llvm` — SHA-256 `af4d59c4ad3395034f553ff0132ba9b46aab5c9660aad68f9f86c531a5b90023`
- `optimization_record` — SHA-256 `c96b1b3b7a120ce22ccac3b010192ea88c0b1ce0ef063a37cc8a17d35ef8489f`
- `optimized_llvm` — SHA-256 `6a39a848a5afa41ed5d9880d34996be771d0e8148bf60409b42879d2eb896c62`
- `trace` — SHA-256 `a3fa45bd822b2e4ac2d0e0ef5eaec2b1e4ce370790ea88456f6832e92f659ed8`
- `wir` — SHA-256 `fa90aabd5cedee107e98c59d8135d129b27d58a74e2f12a1211cad6595f94647`

## LLM review

## Summary
The Weave compiler toolchain successfully lowers `examples/fibonacci_iterative.weave` to correct, memory-safe, and target-compatible machine code. The source defines an iterative Fibonacci function and a `main` entry point that returns `fib(10)` as the process exit code. The raw LLVM IR uses explicit stack allocations (`alloca`) and `load`/`store` traffic for local variables, but the optimized LLVM IR completely promotes these to SSA registers via `mem2reg` and related passes. The constant argument `10` is propagated into `fib`, the loop is unrolled and folded, and `main` is reduced to a single `ret i32 55` instruction. The target assembly and linked executable disassembly confirm this: `main` executes `movl $0x37, %eax` (55 decimal) followed by `retq`, with zero stack usage. The `fib` function is also correctly lowered to a tight, register-based loop in native code. No undefined behavior, invalid IR, memory unsafety, or lingering compiler-generated overhead is present in the optimized output.

## Blocking findings
None found.

## Non-blocking opportunities
- **Raw LLVM stack traffic**: The raw LLVM IR for `fib` allocates three stack slots (`%prev.addr`, `%curr.addr`, `%i.addr`) and performs six `load`/`store` operations. This is a standard, conservative lowering strategy for mutable local variables and is completely optimized away by LLVM's `mem2reg` pass, resulting in zero `alloca` or memory operations in the optimized LLVM IR. This is non-blocking and represents no defect.
- **Loop vectorization**: The optimization record notes that the loop in `fib` was not vectorized due to a value being used outside the loop and an inability to compute the number of iterations. This is a missed optimization opportunity, not a defect. The iterative Fibonacci algorithm contains a loop-carried data dependency that makes it inherently difficult to vectorize. The final native code is efficient and correct.

## Suggested verification
- **Dynamic execution test**: Run the linked executable and verify the process exit code is exactly `55` (`echo $?`), which would confirm the end-to-end correctness of the `fib(10)` computation.
- **Boundary value testing**: Compile and run test cases for `fib(0)`, `fib(1)`, and `fib(2)` to verify the `le_i32 n (const_i32 1)` condition and the loop initialization logic behave as expected at boundaries.
- **Larger input testing**: Test with a larger input (e.g., `fib(20)`) to ensure the loop iterates correctly and does not encounter unexpected integer overflow or logic errors.

<details>
<summary>Raw model response</summary>

```text
OK
## Summary
The Weave compiler toolchain successfully lowers `examples/fibonacci_iterative.weave` to correct, memory-safe, and target-compatible machine code. The source defines an iterative Fibonacci function and a `main` entry point that returns `fib(10)` as the process exit code. The raw LLVM IR uses explicit stack allocations (`alloca`) and `load`/`store` traffic for local variables, but the optimized LLVM IR completely promotes these to SSA registers via `mem2reg` and related passes. The constant argument `10` is propagated into `fib`, the loop is unrolled and folded, and `main` is reduced to a single `ret i32 55` instruction. The target assembly and linked executable disassembly confirm this: `main` executes `movl $0x37, %eax` (55 decimal) followed by `retq`, with zero stack usage. The `fib` function is also correctly lowered to a tight, register-based loop in native code. No undefined behavior, invalid IR, memory unsafety, or lingering compiler-generated overhead is present in the optimized output.

## Blocking findings
None found.

## Non-blocking opportunities
- **Raw LLVM stack traffic**: The raw LLVM IR for `fib` allocates three stack slots (`%prev.addr`, `%curr.addr`, `%i.addr`) and performs six `load`/`store` operations. This is a standard, conservative lowering strategy for mutable local variables and is completely optimized away by LLVM's `mem2reg` pass, resulting in zero `alloca` or memory operations in the optimized LLVM IR. This is non-blocking and represents no defect.
- **Loop vectorization**: The optimization record notes that the loop in `fib` was not vectorized due to a value being used outside the loop and an inability to compute the number of iterations. This is a missed optimization opportunity, not a defect. The iterative Fibonacci algorithm contains a loop-carried data dependency that makes it inherently difficult to vectorize. The final native code is efficient and correct.

## Suggested verification
- **Dynamic execution test**: Run the linked executable and verify the process exit code is exactly `55` (`echo $?`), which would confirm the end-to-end correctness of the `fib(10)` computation.
- **Boundary value testing**: Compile and run test cases for `fib(0)`, `fib(1)`, and `fib(2)` to verify the `le_i32 n (const_i32 1)` condition and the loop initialization logic behave as expected at boundaries.
- **Larger input testing**: Test with a larger input (e.g., `fib(20)`) to ensure the loop iterates correctly and does not encounter unexpected integer overflow or logic errors.
```
</details>
