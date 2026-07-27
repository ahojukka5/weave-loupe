# Weave Loupe Audit Report

## Verdict

- **Status:** OK
- **Code:** none
- **Reason:** No blocking defect found.

## Reproducibility

- **Audit timestamp (UTC):** `2026-07-27T11:57:24+00:00`
- **Audited source Git SHA:** `dbb31eb2c3c7c94d2fec79815e78e315a090059f`
- **Source tree state:** `clean`
- **Weave Loupe Git SHA:** `dbb31eb2c3c7c94d2fec79815e78e315a090059f`
- **weavec Git SHA:** `dbe9e379f663d6dbc7627b3acf21c6d1452db425`
- **weavec binary SHA-256:** `44da49a96942174d8f29dca9ca5582d5ef330e272c6b5de622d66162f500f6ac`
- **weavec version:** `unavailable`
- **LLM model:** `z-ai/glm-5.2`
- **GitHub run ID:** `30263884596`
- **GitHub workflow SHA:** `c6fe8f1d69474d16f5db29be672605e68d8d509e`

## Machine and running conditions

- **Operating system:** `Ubuntu 24.04.4 LTS`
- **Kernel:** `Linux 6.17.0-1020-azure`
- **Architecture:** `x86_64`
- **CPU:** `AMD EPYC 7763 64-Core Processor`
- **Logical CPUs:** `4`
- **Memory:** `16770756608` bytes
- **Python:** `3.12.13`
- **libc:** `glibc 2.39`

## Audited inputs

- `examples/fibonacci_iterative.weave` — SHA-256 `f0b0307bf52ed886b7ee63a4aa952f327204bc79530dea0abe013f24369dd04f`

## Captured evidence

- `assembly` — SHA-256 `7b499c3329a52cdeb44a0f97fd11525a60c93660e5b4b97c5a860aba92e37f30`
- `build_manifest` — SHA-256 `1d5eec46b9637d58e954371f9f0f9b331891cac13f0cd1521664fd35525dd7ce`
- `diagnostics` — SHA-256 `a40b573053cda943c381742ad672108b1c8985ecc97e2f21dfa604094e31ff63`
- `disassembly` — SHA-256 `ce594649f3931d9724a2c505ac0628e6d5e243e0ef235568cdb34af2ebb926c5`
- `llvm` — SHA-256 `c4c80f095a9eda04807a62b4f4956794028987daf644234290cf3b94e8be4bd8`
- `optimization_record` — SHA-256 `c96b1b3b7a120ce22ccac3b010192ea88c0b1ce0ef063a37cc8a17d35ef8489f`
- `optimized_llvm` — SHA-256 `6a39a848a5afa41ed5d9880d34996be771d0e8148bf60409b42879d2eb896c62`
- `trace` — SHA-256 `a3fa45bd822b2e4ac2d0e0ef5eaec2b1e4ce370790ea88456f6832e92f659ed8`
- `wir` — SHA-256 `fa90aabd5cedee107e98c59d8135d129b27d58a74e2f12a1211cad6595f94647`

## LLM review

## Summary
The Weave compiler successfully lowers `examples/fibonacci_iterative.weave` to valid LLVM IR and native x86-64 code. The raw LLVM IR uses explicit stack allocations (`alloca`) and loads/stores for local variables, which is standard for unoptimized code. The LLVM optimizer completely promotes these to registers, inlines the `fib` function into `main`, and constant-folds the computation. The final linked executable correctly computes `fib(10) = 55` (visible as `movl $0x37, %eax` in the `main` disassembly). No merge-blocking defects were found.

## Blocking findings
None found.

## Non-blocking opportunities
- **Raw LLVM stack traffic**: The raw LLVM IR for `fib` allocates stack space for `prev`, `curr`, and `i`, then repeatedly loads and stores them inside the loop. This is eliminated by LLVM's `mem2reg` pass, as shown by the zero `alloca` and `load` counts in the optimized LLVM IR. This is non-blocking.
- **Loop vectorization**: The optimization record indicates the loop in `fib` was not vectorized. Given the data dependency between iterations, this is expected and not a compiler defect.

## Suggested verification
- Run the linked executable and verify the process exit code is `55`.
- Test `fib` with edge cases like `n = 0`, `n = 1`, and `n = 2` to ensure the `le_i32 n (const_i32 1)` condition behaves correctly.
- Test with a larger `n` (e.g., `n = 47`) to verify the iterative loop scales correctly without stack exhaustion.

<details>
<summary>Raw model response</summary>

```text
OK
## Summary
The Weave compiler successfully lowers `examples/fibonacci_iterative.weave` to valid LLVM IR and native x86-64 code. The raw LLVM IR uses explicit stack allocations (`alloca`) and loads/stores for local variables, which is standard for unoptimized code. The LLVM optimizer completely promotes these to registers, inlines the `fib` function into `main`, and constant-folds the computation. The final linked executable correctly computes `fib(10) = 55` (visible as `movl $0x37, %eax` in the `main` disassembly). No merge-blocking defects were found.

## Blocking findings
None found.

## Non-blocking opportunities
- **Raw LLVM stack traffic**: The raw LLVM IR for `fib` allocates stack space for `prev`, `curr`, and `i`, then repeatedly loads and stores them inside the loop. This is eliminated by LLVM's `mem2reg` pass, as shown by the zero `alloca` and `load` counts in the optimized LLVM IR. This is non-blocking.
- **Loop vectorization**: The optimization record indicates the loop in `fib` was not vectorized. Given the data dependency between iterations, this is expected and not a compiler defect.

## Suggested verification
- Run the linked executable and verify the process exit code is `55`.
- Test `fib` with edge cases like `n = 0`, `n = 1`, and `n = 2` to ensure the `le_i32 n (const_i32 1)` condition behaves correctly.
- Test with a larger `n` (e.g., `n = 47`) to verify the iterative loop scales correctly without stack exhaustion.
```
</details>
