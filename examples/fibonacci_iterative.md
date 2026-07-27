# Weave Loupe Audit Report

## Verdict

- **Status:** OK
- **Code:** none
- **Reason:** No blocking defect found.

## Reproducibility

- **Audit timestamp (UTC):** `2026-07-27T10:49:47+00:00`
- **Audited source Git SHA:** `9a063d42249ade71929606f4855407927b0d0c47`
- **Source tree state:** `clean`
- **Weave Loupe Git SHA:** `9a063d42249ade71929606f4855407927b0d0c47`
- **weavec Git SHA:** `dbe9e379f663d6dbc7627b3acf21c6d1452db425`
- **weavec binary SHA-256:** `44da49a96942174d8f29dca9ca5582d5ef330e272c6b5de622d66162f500f6ac`
- **weavec version:** `unavailable`
- **LLM model:** `z-ai/glm-5.2`
- **GitHub run ID:** `30259524648`
- **GitHub workflow SHA:** `ae151961a98a7fb624edb9b4985ae095af56aa1d`

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
- `build_manifest` — SHA-256 `ce631b9457943a1cb0d4e9c7823f267072bf96622ab97a5f3d9c1bd32d066d03`
- `diagnostics` — SHA-256 `a40b573053cda943c381742ad672108b1c8985ecc97e2f21dfa604094e31ff63`
- `disassembly` — SHA-256 `ce594649f3931d9724a2c505ac0628e6d5e243e0ef235568cdb34af2ebb926c5`
- `llvm` — SHA-256 `3fe082d59f6d168cb7ee0d15a9cbf0c8a7686231d2bd916003c3420f070fd8c0`
- `optimization_record` — SHA-256 `c96b1b3b7a120ce22ccac3b010192ea88c0b1ce0ef063a37cc8a17d35ef8489f`
- `optimized_llvm` — SHA-256 `6a39a848a5afa41ed5d9880d34996be771d0e8148bf60409b42879d2eb896c62`
- `trace` — SHA-256 `a3fa45bd822b2e4ac2d0e0ef5eaec2b1e4ce370790ea88456f6832e92f659ed8`
- `wir` — SHA-256 `fa90aabd5cedee107e98c59d8135d129b27d58a74e2f12a1211cad6595f94647`

## LLM review

## Summary
The Weave compiler successfully lowered `examples/fibonacci_iterative.weave` to valid LLVM IR and native x86_64 code. The program computes `fib(10)` iteratively and returns it as the exit code. The raw LLVM IR uses stack allocas for local variables, but LLVM's `mem2reg` and subsequent optimization passes promote these to SSA registers and fully evaluate `main` at compile time. The optimized LLVM IR for `main` directly returns `55` (`0x37`), which matches the expected mathematical result and is confirmed by the linked executable disassembly (`movl $0x37, %eax`). No undefined behavior, memory unsafety, target incompatibility, or lingering compiler-generated overhead is present in the final machine code.

## Blocking findings
None found.

## Non-blocking opportunities
- **Raw LLVM stack traffic**: The raw LLVM IR allocates `i32` stack slots for `prev`, `curr`, and `i`, and performs repeated `load`/`store` operations inside the `while` loop. This is a standard unoptimized IR pattern and is completely eliminated by LLVM's optimization pipeline (as seen in the optimized LLVM IR, which uses `phi` nodes and has zero `alloca`/`load`/`store` instructions). This is non-blocking.
- **Loop vectorization**: The optimization record notes that the `fib` loop was not vectorized due to non-reduction values used outside the loop and uncomputable iteration counts. This is an inherent property of the iterative Fibonacci algorithm as written and does not represent compiler-generated overhead. This is non-blocking.

## Suggested verification
- Run the linked executable and verify the process exit code is exactly `55` to confirm end-to-end behavior.
- Test `fib` with edge-case inputs (e.g., `0`, `1`, negative numbers) to ensure the `le_i32` condition and signed integer semantics behave as expected across the Weave-to-native pipeline.

<details>
<summary>Raw model response</summary>

```text
OK

## Summary
The Weave compiler successfully lowered `examples/fibonacci_iterative.weave` to valid LLVM IR and native x86_64 code. The program computes `fib(10)` iteratively and returns it as the exit code. The raw LLVM IR uses stack allocas for local variables, but LLVM's `mem2reg` and subsequent optimization passes promote these to SSA registers and fully evaluate `main` at compile time. The optimized LLVM IR for `main` directly returns `55` (`0x37`), which matches the expected mathematical result and is confirmed by the linked executable disassembly (`movl $0x37, %eax`). No undefined behavior, memory unsafety, target incompatibility, or lingering compiler-generated overhead is present in the final machine code.

## Blocking findings
None found.

## Non-blocking opportunities
- **Raw LLVM stack traffic**: The raw LLVM IR allocates `i32` stack slots for `prev`, `curr`, and `i`, and performs repeated `load`/`store` operations inside the `while` loop. This is a standard unoptimized IR pattern and is completely eliminated by LLVM's optimization pipeline (as seen in the optimized LLVM IR, which uses `phi` nodes and has zero `alloca`/`load`/`store` instructions). This is non-blocking.
- **Loop vectorization**: The optimization record notes that the `fib` loop was not vectorized due to non-reduction values used outside the loop and uncomputable iteration counts. This is an inherent property of the iterative Fibonacci algorithm as written and does not represent compiler-generated overhead. This is non-blocking.

## Suggested verification
- Run the linked executable and verify the process exit code is exactly `55` to confirm end-to-end behavior.
- Test `fib` with edge-case inputs (e.g., `0`, `1`, negative numbers) to ensure the `le_i32` condition and signed integer semantics behave as expected across the Weave-to-native pipeline.
```
</details>
