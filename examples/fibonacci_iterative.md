# Weave Loupe Audit Report

## Verdict

- **Status:** OK
- **Code:** none
- **Reason:** No blocking defect found.

## Reproducibility

- **Audit timestamp (UTC):** `2026-07-27T10:47:40+00:00`
- **Audited source Git SHA:** `cba9327ec737a866ee0f5274d52e22a36f3b6925`
- **Source tree state:** `clean`
- **Weave Loupe Git SHA:** `cba9327ec737a866ee0f5274d52e22a36f3b6925`
- **weavec Git SHA:** `dbe9e379f663d6dbc7627b3acf21c6d1452db425`
- **weavec binary SHA-256:** `44da49a96942174d8f29dca9ca5582d5ef330e272c6b5de622d66162f500f6ac`
- **weavec version:** `unavailable`
- **LLM model:** `z-ai/glm-5.2`
- **GitHub run ID:** `30259394437`
- **GitHub workflow SHA:** `9bf95fcf4872e3f66c0dd4f6105bac32914c981c`

## Machine and running conditions

- **Operating system:** `Ubuntu 24.04.4 LTS`
- **Kernel:** `Linux 6.17.0-1020-azure`
- **Architecture:** `x86_64`
- **CPU:** `Intel(R) Xeon(R) Platinum 8370C CPU @ 2.80GHz`
- **Logical CPUs:** `4`
- **Memory:** `16769720320` bytes
- **Python:** `3.12.13`
- **libc:** `glibc 2.39`

## Audited inputs

- `examples/fibonacci_iterative.weave` — SHA-256 `f0b0307bf52ed886b7ee63a4aa952f327204bc79530dea0abe013f24369dd04f`

## Captured evidence

- `assembly` — SHA-256 `730fac8186d8bc25f4032e836d77c1f94dc3c7b1ffe881974e2064880963da31`
- `build_manifest` — SHA-256 `e3c0c2b6a370f7d88aab029a1412f248c62558562e241613863246f0d2f11eb0`
- `diagnostics` — SHA-256 `a40b573053cda943c381742ad672108b1c8985ecc97e2f21dfa604094e31ff63`
- `disassembly` — SHA-256 `20b493cf2dbbede5b47a5bac08af3043eb8675a5fdc176fa9a7f992b102dd8e0`
- `llvm` — SHA-256 `b2785a6f1637ed8024b4edf510e629b4ddf8b80d0f46bfa44530ca3c4030af55`
- `optimization_record` — SHA-256 `c96b1b3b7a120ce22ccac3b010192ea88c0b1ce0ef063a37cc8a17d35ef8489f`
- `optimized_llvm` — SHA-256 `6a39a848a5afa41ed5d9880d34996be771d0e8148bf60409b42879d2eb896c62`
- `trace` — SHA-256 `a3fa45bd822b2e4ac2d0e0ef5eaec2b1e4ce370790ea88456f6832e92f659ed8`
- `wir` — SHA-256 `fa90aabd5cedee107e98c59d8135d129b27d58a74e2f12a1211cad6595f94647`

## LLM review

## Summary
The Weave compiler toolchain successfully compiles `examples/fibonacci_iterative.weave` to valid LLVM IR and x86_64 native code. The source computes `fib(10)` iteratively and returns it as the process exit code. The raw LLVM IR uses explicit stack allocations (`alloca`) and `load`/`store` instructions for local variables, which are completely promoted to SSA registers in the optimized LLVM IR. The `fib` function is inlined into `main` and the loop is constant-folded, resulting in `main` directly returning the constant `55` (`0x37`). The final linked executable disassembly confirms this behavior. No undefined behavior, memory unsafety, or target incompatibility is present.

## Blocking findings
None found.

## Non-blocking opportunities
- **Raw LLVM stack traffic**: The raw LLVM IR for `fib` allocates stack space for `prev`, `curr`, and `i`, and repeatedly loads/stres them inside the loop. This is standard unoptimized IR and is completely eliminated by LLVM's `mem2reg` pass, resulting in zero `alloca` or `load`/`store` instructions in the optimized LLVM IR. This is not a compiler-generated overhead defect.
- **Loop vectorization**: The optimization record notes that the loop in `fib` was not vectorized. This is expected given the loop-carried dependencies and is a non-blocking optimization miss, not a defect.

## Suggested verification
- Run the compiled executable and verify the process exit code is exactly `55` to confirm end-to-end behavior.
- Test `fib` with edge cases such as `n = 0`, `n = 1`, and `n = 2` to ensure the `le_i32 n (const_i32 1)` boundary condition behaves correctly.
- Test with a larger `n` (e.g., `n = 20`) to ensure the iterative loop scales correctly and is not incorrectly constant-folded in cases where the input is not statically known.

<details>
<summary>Raw model response</summary>

```text
OK

## Summary
The Weave compiler toolchain successfully compiles `examples/fibonacci_iterative.weave` to valid LLVM IR and x86_64 native code. The source computes `fib(10)` iteratively and returns it as the process exit code. The raw LLVM IR uses explicit stack allocations (`alloca`) and `load`/`store` instructions for local variables, which are completely promoted to SSA registers in the optimized LLVM IR. The `fib` function is inlined into `main` and the loop is constant-folded, resulting in `main` directly returning the constant `55` (`0x37`). The final linked executable disassembly confirms this behavior. No undefined behavior, memory unsafety, or target incompatibility is present.

## Blocking findings
None found.

## Non-blocking opportunities
- **Raw LLVM stack traffic**: The raw LLVM IR for `fib` allocates stack space for `prev`, `curr`, and `i`, and repeatedly loads/stres them inside the loop. This is standard unoptimized IR and is completely eliminated by LLVM's `mem2reg` pass, resulting in zero `alloca` or `load`/`store` instructions in the optimized LLVM IR. This is not a compiler-generated overhead defect.
- **Loop vectorization**: The optimization record notes that the loop in `fib` was not vectorized. This is expected given the loop-carried dependencies and is a non-blocking optimization miss, not a defect.

## Suggested verification
- Run the compiled executable and verify the process exit code is exactly `55` to confirm end-to-end behavior.
- Test `fib` with edge cases such as `n = 0`, `n = 1`, and `n = 2` to ensure the `le_i32 n (const_i32 1)` boundary condition behaves correctly.
- Test with a larger `n` (e.g., `n = 20`) to ensure the iterative loop scales correctly and is not incorrectly constant-folded in cases where the input is not statically known.
```
</details>
