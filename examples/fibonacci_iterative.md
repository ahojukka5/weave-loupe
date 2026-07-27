# Weave Loupe Audit Report

## Verdict

- **Status:** OK
- **Code:** none
- **Reason:** No blocking defect found.

## Reproducibility

- **Audit timestamp (UTC):** `2026-07-27T10:50:31+00:00`
- **Audited source Git SHA:** `056919ee586dd2d9d2608bd23cc486a3e05f8c94`
- **Source tree state:** `clean`
- **Weave Loupe Git SHA:** `056919ee586dd2d9d2608bd23cc486a3e05f8c94`
- **weavec Git SHA:** `dbe9e379f663d6dbc7627b3acf21c6d1452db425`
- **weavec binary SHA-256:** `44da49a96942174d8f29dca9ca5582d5ef330e272c6b5de622d66162f500f6ac`
- **weavec version:** `unavailable`
- **LLM model:** `z-ai/glm-5.2`
- **GitHub run ID:** `30259571989`
- **GitHub workflow SHA:** `957ca1739ea7f05f12baec01dca23fcbd6584b70`

## Machine and running conditions

- **Operating system:** `Ubuntu 24.04.4 LTS`
- **Kernel:** `Linux 6.17.0-1020-azure`
- **Architecture:** `x86_64`
- **CPU:** `AMD EPYC 9V74 80-Core Processor`
- **Logical CPUs:** `4`
- **Memory:** `16766423040` bytes
- **Python:** `3.12.13`
- **libc:** `glibc 2.39`

## Audited inputs

- `examples/fibonacci_iterative.weave` — SHA-256 `f0b0307bf52ed886b7ee63a4aa952f327204bc79530dea0abe013f24369dd04f`

## Captured evidence

- `assembly` — SHA-256 `7b499c3329a52cdeb44a0f97fd11525a60c93660e5b4b97c5a860aba92e37f30`
- `build_manifest` — SHA-256 `c78f8e92245d8a83faa685f127485626ee117c89b79343d4322371f21b07f260`
- `diagnostics` — SHA-256 `a40b573053cda943c381742ad672108b1c8985ecc97e2f21dfa604094e31ff63`
- `disassembly` — SHA-256 `ce594649f3931d9724a2c505ac0628e6d5e243e0ef235568cdb34af2ebb926c5`
- `llvm` — SHA-256 `a2d3a6cba133125c3812a7afe01fa96f3a42bd632db5e61326f8858d182f6e7b`
- `optimization_record` — SHA-256 `c96b1b3b7a120ce22ccac3b010192ea88c0b1ce0ef063a37cc8a17d35ef8489f`
- `optimized_llvm` — SHA-256 `6a39a848a5afa41ed5d9880d34996be771d0e8148bf60409b42879d2eb896c62`
- `trace` — SHA-256 `a3fa45bd822b2e4ac2d0e0ef5eaec2b1e4ce370790ea88456f6832e92f659ed8`
- `wir` — SHA-256 `fa90aabd5cedee107e98c59d8135d129b27d58a74e2f12a1211cad6595f94647`

## LLM review

## Summary
The Weave compiler successfully lowered `examples/fibonacci_iterative.weave` to valid LLVM IR and native x86_64 code. The program computes `fib(10)` iteratively and returns the result as the exit code. The raw LLVM IR uses stack allocas for local variables, but the LLVM optimizer promotes these to SSA registers and inlines the `fib` call into `main`, which is then constant-folded to `ret i32 55`. The final linked disassembly confirms `main` returns `0x37` (55), matching the expected behavior. No merge-blocking defects were observed in the generated code.

## Blocking findings
None found.

## Non-blocking opportunities
- **Raw LLVM stack traffic**: The raw LLVM IR for `fib` uses `alloca` and `load`/`store` for `prev`, `curr`, and `i`. This is expected for a straightforward lowering but is completely optimized away by LLVM's `mem2reg` pass, as shown in the optimized LLVM IR. This is not a defect.
- **Loop vectorization**: The optimization record notes that the loop in `fib` was not vectorized due to non-reduction value usage and uncomputable iteration count. This is a source-level algorithm characteristic (iterative Fibonacci with a loop-carried dependency chain), not compiler-generated overhead. No action required.

## Suggested verification
- Run the linked executable and verify the process exit code is `55`.
- Test `fib` with edge cases (e.g., `n = 0`, `n = 1`, `n = 2`) to confirm the `le_i32 n 1` guard returns `n` correctly.
- Test with a larger `n` (e.g., `n = 20`) to confirm the iterative loop executes the expected number of times and returns the correct Fibonacci number.

<details>
<summary>Raw model response</summary>

```text
OK
## Summary
The Weave compiler successfully lowered `examples/fibonacci_iterative.weave` to valid LLVM IR and native x86_64 code. The program computes `fib(10)` iteratively and returns the result as the exit code. The raw LLVM IR uses stack allocas for local variables, but the LLVM optimizer promotes these to SSA registers and inlines the `fib` call into `main`, which is then constant-folded to `ret i32 55`. The final linked disassembly confirms `main` returns `0x37` (55), matching the expected behavior. No merge-blocking defects were observed in the generated code.

## Blocking findings
None found.

## Non-blocking opportunities
- **Raw LLVM stack traffic**: The raw LLVM IR for `fib` uses `alloca` and `load`/`store` for `prev`, `curr`, and `i`. This is expected for a straightforward lowering but is completely optimized away by LLVM's `mem2reg` pass, as shown in the optimized LLVM IR. This is not a defect.
- **Loop vectorization**: The optimization record notes that the loop in `fib` was not vectorized due to non-reduction value usage and uncomputable iteration count. This is a source-level algorithm characteristic (iterative Fibonacci with a loop-carried dependency chain), not compiler-generated overhead. No action required.

## Suggested verification
- Run the linked executable and verify the process exit code is `55`.
- Test `fib` with edge cases (e.g., `n = 0`, `n = 1`, `n = 2`) to confirm the `le_i32 n 1` guard returns `n` correctly.
- Test with a larger `n` (e.g., `n = 20`) to confirm the iterative loop executes the expected number of times and returns the correct Fibonacci number.
```
</details>
