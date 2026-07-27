# Weave Loupe Audit Report

## Verdict

- **Status:** OK
- **Code:** none
- **Reason:** No blocking defect found.

## Reproducibility

- **Audit timestamp (UTC):** `2026-07-27T10:48:31+00:00`
- **Audited source Git SHA:** `89b3438ad1bd7a283381a613062e1c0330361b28`
- **Source tree state:** `clean`
- **Weave Loupe Git SHA:** `89b3438ad1bd7a283381a613062e1c0330361b28`
- **weavec Git SHA:** `dbe9e379f663d6dbc7627b3acf21c6d1452db425`
- **weavec binary SHA-256:** `44da49a96942174d8f29dca9ca5582d5ef330e272c6b5de622d66162f500f6ac`
- **weavec version:** `unavailable`
- **LLM model:** `z-ai/glm-5.2`
- **GitHub run ID:** `30259448900`
- **GitHub workflow SHA:** `71971c46c0d78b7b031ecf465595001fe6ff4f8a`

## Machine and running conditions

- **Operating system:** `Ubuntu 24.04.4 LTS`
- **Kernel:** `Linux 6.17.0-1020-azure`
- **Architecture:** `x86_64`
- **CPU:** `AMD EPYC 7763 64-Core Processor`
- **Logical CPUs:** `4`
- **Memory:** `16766423040` bytes
- **Python:** `3.12.13`
- **libc:** `glibc 2.39`

## Audited inputs

- `examples/fibonacci_iterative.weave` — SHA-256 `f0b0307bf52ed886b7ee63a4aa952f327204bc79530dea0abe013f24369dd04f`

## Captured evidence

- `assembly` — SHA-256 `7b499c3329a52cdeb44a0f97fd11525a60c93660e5b4b97c5a860aba92e37f30`
- `build_manifest` — SHA-256 `53d027cc1ff4c883232bd8ce292c8110b489d552877a6b2bd7a66fc817d84647`
- `diagnostics` — SHA-256 `a40b573053cda943c381742ad672108b1c8985ecc97e2f21dfa604094e31ff63`
- `disassembly` — SHA-256 `ce594649f3931d9724a2c505ac0628e6d5e243e0ef235568cdb34af2ebb926c5`
- `llvm` — SHA-256 `5112c97b1f35c7ad2ea782ce6b930366279841896a0de32e9a1fb000ee5e4dcb`
- `optimization_record` — SHA-256 `c96b1b3b7a120ce22ccac3b010192ea88c0b1ce0ef063a37cc8a17d35ef8489f`
- `optimized_llvm` — SHA-256 `6a39a848a5afa41ed5d9880d34996be771d0e8148bf60409b42879d2eb896c62`
- `trace` — SHA-256 `a3fa45bd822b2e4ac2d0e0ef5eaec2b1e4ce370790ea88456f6832e92f659ed8`
- `wir` — SHA-256 `fa90aabd5cedee107e98c59d8135d129b27d58a74e2f12a1211cad6595f94647`

## LLM review

## Summary
The Weave compiler toolchain successfully compiles `examples/fibonacci_iterative.weave` to valid LLVM IR and native x86_64 code. The raw LLVM IR uses stack allocations (`alloca`) for local variables, but LLVM's `mem2reg` and subsequent optimization passes successfully promote these to SSA registers, as evidenced by the optimized LLVM IR containing `phi` nodes and zero `alloca`/`load`/`store` instructions. The `main` function is correctly constant-folded to return `55` (the 10th Fibonacci number), matching the source intent. The final native code for `fib` is a tight loop with no stack frame overhead, and `main` is a single `mov` and `ret`. No merge-blocking defects were identified.

## Blocking findings
None found.

## Non-blocking opportunities
- **Raw LLVM IR stack traffic**: The raw LLVM IR for `fib` uses `alloca` and explicit `load`/`store` for `prev`, `curr`, and `i`. While this is optimized away in the final code, a direct SSA-based IR generation in `weavec` could reduce the initial IR size and potentially speed up the LLVM optimization pipeline. This is a compiler implementation efficiency note, not a defect in the output.
- **Loop vectorization**: The optimization record notes that the loop in `fib` was not vectorized due to the value being used outside the loop and uncomputable iteration count. This is inherent to the iterative Fibonacci algorithm (recurrence relation) and not a compiler deficiency.

## Suggested verification
- **Boundary tests**: Verify `fib(0)` and `fib(1)` return `0` and `1` respectively, matching the early return condition in the source.
- **Large input test**: Test `fib(46)` (result 1836311903) to ensure no overflow issues occur within the `i32` type and the loop terminates correctly.
- **Negative input test**: Test `fib(-1)` to document behavior for inputs less than 1, as the source returns `n` directly for `n <= 1`.

<details>
<summary>Raw model response</summary>

```text
OK

## Summary
The Weave compiler toolchain successfully compiles `examples/fibonacci_iterative.weave` to valid LLVM IR and native x86_64 code. The raw LLVM IR uses stack allocations (`alloca`) for local variables, but LLVM's `mem2reg` and subsequent optimization passes successfully promote these to SSA registers, as evidenced by the optimized LLVM IR containing `phi` nodes and zero `alloca`/`load`/`store` instructions. The `main` function is correctly constant-folded to return `55` (the 10th Fibonacci number), matching the source intent. The final native code for `fib` is a tight loop with no stack frame overhead, and `main` is a single `mov` and `ret`. No merge-blocking defects were identified.

## Blocking findings
None found.

## Non-blocking opportunities
- **Raw LLVM IR stack traffic**: The raw LLVM IR for `fib` uses `alloca` and explicit `load`/`store` for `prev`, `curr`, and `i`. While this is optimized away in the final code, a direct SSA-based IR generation in `weavec` could reduce the initial IR size and potentially speed up the LLVM optimization pipeline. This is a compiler implementation efficiency note, not a defect in the output.
- **Loop vectorization**: The optimization record notes that the loop in `fib` was not vectorized due to the value being used outside the loop and uncomputable iteration count. This is inherent to the iterative Fibonacci algorithm (recurrence relation) and not a compiler deficiency.

## Suggested verification
- **Boundary tests**: Verify `fib(0)` and `fib(1)` return `0` and `1` respectively, matching the early return condition in the source.
- **Large input test**: Test `fib(46)` (result 1836311903) to ensure no overflow issues occur within the `i32` type and the loop terminates correctly.
- **Negative input test**: Test `fib(-1)` to document behavior for inputs less than 1, as the source returns `n` directly for `n <= 1`.
```
</details>
