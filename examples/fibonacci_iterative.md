# Weave Loupe Audit Report

## Verdict

- **Status:** OK
- **Code:** none
- **Reason:** No blocking defect found.

## Reproducibility

- **Audit timestamp (UTC):** `2026-07-27T10:45:40+00:00`
- **Audited source Git SHA:** `6f9390f9f5821df38578c199fa09d64d76722c00`
- **Source tree state:** `clean`
- **Weave Loupe Git SHA:** `6f9390f9f5821df38578c199fa09d64d76722c00`
- **weavec Git SHA:** `dbe9e379f663d6dbc7627b3acf21c6d1452db425`
- **weavec binary SHA-256:** `44da49a96942174d8f29dca9ca5582d5ef330e272c6b5de622d66162f500f6ac`
- **weavec version:** `unavailable`
- **LLM model:** `z-ai/glm-5.2`
- **GitHub run ID:** `30259264799`
- **GitHub workflow SHA:** `62c26549259b5ab68b98ae8d6c43bec8bb728ced`

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
- `build_manifest` — SHA-256 `69b24974f59643cad5c126d68bf5727b13a9fd2f41cf2a83f7ace1cfca53c034`
- `diagnostics` — SHA-256 `a40b573053cda943c381742ad672108b1c8985ecc97e2f21dfa604094e31ff63`
- `disassembly` — SHA-256 `ce594649f3931d9724a2c505ac0628e6d5e243e0ef235568cdb34af2ebb926c5`
- `llvm` — SHA-256 `9b97c6f47c5945800233041b996aa3669950df2527d5df7f40a843a61e33c37e`
- `optimization_record` — SHA-256 `c96b1b3b7a120ce22ccac3b010192ea88c0b1ce0ef063a37cc8a17d35ef8489f`
- `optimized_llvm` — SHA-256 `6a39a848a5afa41ed5d9880d34996be771d0e8148bf60409b42879d2eb896c62`
- `trace` — SHA-256 `a3fa45bd822b2e4ac2d0e0ef5eaec2b1e4ce370790ea88456f6832e92f659ed8`
- `wir` — SHA-256 `fa90aabd5cedee107e98c59d8135d129b27d58a74e2f12a1211cad6595f94647`

## LLM review

## Summary
The Weave compiler successfully lowered `examples/fibonacci_iterative.weave` to valid LLVM IR and native x86_64 code. The raw LLVM IR uses stack alloca/load/store traffic for local variables, but the optimized LLVM IR promotes these to SSA registers and inlines the constant `fib(10)` call in `main`, yielding `ret i32 55`. The final linked executable confirms this with `main` compiling to `movl $0x37, %eax; retq`. The `fib` function is correctly preserved for external use and compiles to a tight register-only loop. No undefined behavior, memory unsafety, invalid IR, or target incompatibility is present.

## Blocking findings
None found.

## Non-blocking opportunities
- **Raw LLVM stack traffic**: The raw LLVM IR for `fib` uses `alloca` and `store`/`load` for `prev`, `curr`, and `i`. This is standard unoptimized IR and is completely eliminated by LLVM's `mem2reg` pass, as shown by the optimized LLVM IR which contains no `alloca`, `store`, or `load` instructions. This is not a compiler-generated overhead defect.
- **Loop vectorization**: The optimization record notes that the loop in `fib` was not vectorized due to non-reduction values used outside the loop and unknown iteration counts. This is an inherent property of the iterative Fibonacci algorithm and does not represent a compiler defect.

## Suggested verification
- Execute the compiled binary and verify the process exit code is `55` (0x37).
- Test `fib` with edge cases such as `0`, `1`, and `2` to ensure the `le_i32 n 1` boundary condition behaves correctly.
- Test `fib` with a larger value (e.g., `20`) to ensure the iterative loop scales correctly and returns the expected Fibonacci number.

<details>
<summary>Raw model response</summary>

```text
OK

## Summary
The Weave compiler successfully lowered `examples/fibonacci_iterative.weave` to valid LLVM IR and native x86_64 code. The raw LLVM IR uses stack alloca/load/store traffic for local variables, but the optimized LLVM IR promotes these to SSA registers and inlines the constant `fib(10)` call in `main`, yielding `ret i32 55`. The final linked executable confirms this with `main` compiling to `movl $0x37, %eax; retq`. The `fib` function is correctly preserved for external use and compiles to a tight register-only loop. No undefined behavior, memory unsafety, invalid IR, or target incompatibility is present.

## Blocking findings
None found.

## Non-blocking opportunities
- **Raw LLVM stack traffic**: The raw LLVM IR for `fib` uses `alloca` and `store`/`load` for `prev`, `curr`, and `i`. This is standard unoptimized IR and is completely eliminated by LLVM's `mem2reg` pass, as shown by the optimized LLVM IR which contains no `alloca`, `store`, or `load` instructions. This is not a compiler-generated overhead defect.
- **Loop vectorization**: The optimization record notes that the loop in `fib` was not vectorized due to non-reduction values used outside the loop and unknown iteration counts. This is an inherent property of the iterative Fibonacci algorithm and does not represent a compiler defect.

## Suggested verification
- Execute the compiled binary and verify the process exit code is `55` (0x37).
- Test `fib` with edge cases such as `0`, `1`, and `2` to ensure the `le_i32 n 1` boundary condition behaves correctly.
- Test `fib` with a larger value (e.g., `20`) to ensure the iterative loop scales correctly and returns the expected Fibonacci number.
```
</details>
