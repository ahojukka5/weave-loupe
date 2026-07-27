# Weave Loupe Audit Report

## Verdict

- **Status:** OK
- **Code:** none
- **Reason:** No blocking defect found.

## Reproducibility

- **Audit timestamp (UTC):** `2026-07-27T11:18:27+00:00`
- **Audited source Git SHA:** `67e7567904c6eccbf10713cfc9b0fc37ca2076a7`
- **Source tree state:** `clean`
- **Weave Loupe Git SHA:** `67e7567904c6eccbf10713cfc9b0fc37ca2076a7`
- **weavec Git SHA:** `dbe9e379f663d6dbc7627b3acf21c6d1452db425`
- **weavec binary SHA-256:** `44da49a96942174d8f29dca9ca5582d5ef330e272c6b5de622d66162f500f6ac`
- **weavec version:** `unavailable`
- **LLM model:** `z-ai/glm-5.2`
- **GitHub run ID:** `30261385429`
- **GitHub workflow SHA:** `88a03b44ed4dbde306ce427b1e9be4aecd885420`

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

- `examples/fibonacci.weave` — SHA-256 `dba4af6fabb682368b23767ac4891addbfad84263b301e49e726dd64f4f14d8d`

## Captured evidence

- `assembly` — SHA-256 `7b499c3329a52cdeb44a0f97fd11525a60c93660e5b4b97c5a860aba92e37f30`
- `build_manifest` — SHA-256 `d789c1cfb9580c52fa18b305e3ba2017a76466500d8966dc1b7708a037854c76`
- `diagnostics` — SHA-256 `a40b573053cda943c381742ad672108b1c8985ecc97e2f21dfa604094e31ff63`
- `disassembly` — SHA-256 `ce594649f3931d9724a2c505ac0628e6d5e243e0ef235568cdb34af2ebb926c5`
- `llvm` — SHA-256 `04e261ceeaad1294205d4f276a16b172eddb821ddec433539f728b0cb1d24e65`
- `optimization_record` — SHA-256 `c96b1b3b7a120ce22ccac3b010192ea88c0b1ce0ef063a37cc8a17d35ef8489f`
- `optimized_llvm` — SHA-256 `1271d4a27ff0eac2c525d5b7f9bb682e51bacdd658302ee50d1f023d5a603dad`
- `trace` — SHA-256 `7b9cef8e4044659177d8413dc9f3d99d48fd756f4d5fcb2dab1965e7523b6ede`
- `wir` — SHA-256 `2892e11ad2634624c55db30e23e34d08de42943d9af4beffa36aeedd9b7256f7`

## LLM review

## Summary
The Weave compiler toolchain successfully compiles `examples/fibonacci.weave` to valid LLVM IR and native x86_64 code. The source defines an iterative `fib` function and a `main` entry point that returns `fib(10)`. The raw LLVM IR uses explicit stack allocations (`alloca`) and loads/stores for local variables, which is a standard, safe lowering strategy. The LLVM optimizer completely promotes these stack allocations to registers and inlines the `fib` function into `main`. The optimized LLVM IR and final disassembly confirm that `main` directly returns the constant `55` (`0x37`), which is the correct value for `fib(10)`. The `fib` function is also correctly compiled to a tight loop. No undefined behavior, memory unsafety, or target incompatibility is present.

## Blocking findings
None found.

## Non-blocking opportunities
- **Raw LLVM IR stack traffic**: The raw LLVM IR for `fib` uses `alloca` and explicit `load`/`store` instructions for `previous`, `current`, and `index`. While this is memory-safe and standard, it generates unnecessary stack traffic in the unoptimized IR. This is non-blocking because LLVM's `mem2reg` pass completely eliminates these allocations in the optimized LLVM IR, resulting in a clean loop using SSA `phi` nodes.
- **Loop vectorization**: The optimization record indicates that the loop in `fib` was not vectorized due to the value being used outside the loop and an undetermined iteration count. This is a non-blocking missed optimization opportunity, as the iterative Fibonacci algorithm has a loop-carried dependency that makes simple vectorization difficult or impossible without advanced transformations.

## Suggested verification
- **Dynamic execution**: Run the compiled executable and verify the process exit code is `55` to confirm end-to-end behavioral correctness.
- **Boundary tests**: Compile and run test cases for `fib(0)`, `fib(1)`, and `fib(2)` to ensure the `le_i32` condition and loop logic handle edge cases correctly.
- **Negative input tests**: Test `fib` with negative inputs to document or verify the intended behavior of the signed integer comparison (`icmp sle`).

<details>
<summary>Raw model response</summary>

```text
OK
## Summary
The Weave compiler toolchain successfully compiles `examples/fibonacci.weave` to valid LLVM IR and native x86_64 code. The source defines an iterative `fib` function and a `main` entry point that returns `fib(10)`. The raw LLVM IR uses explicit stack allocations (`alloca`) and loads/stores for local variables, which is a standard, safe lowering strategy. The LLVM optimizer completely promotes these stack allocations to registers and inlines the `fib` function into `main`. The optimized LLVM IR and final disassembly confirm that `main` directly returns the constant `55` (`0x37`), which is the correct value for `fib(10)`. The `fib` function is also correctly compiled to a tight loop. No undefined behavior, memory unsafety, or target incompatibility is present.

## Blocking findings
None found.

## Non-blocking opportunities
- **Raw LLVM IR stack traffic**: The raw LLVM IR for `fib` uses `alloca` and explicit `load`/`store` instructions for `previous`, `current`, and `index`. While this is memory-safe and standard, it generates unnecessary stack traffic in the unoptimized IR. This is non-blocking because LLVM's `mem2reg` pass completely eliminates these allocations in the optimized LLVM IR, resulting in a clean loop using SSA `phi` nodes.
- **Loop vectorization**: The optimization record indicates that the loop in `fib` was not vectorized due to the value being used outside the loop and an undetermined iteration count. This is a non-blocking missed optimization opportunity, as the iterative Fibonacci algorithm has a loop-carried dependency that makes simple vectorization difficult or impossible without advanced transformations.

## Suggested verification
- **Dynamic execution**: Run the compiled executable and verify the process exit code is `55` to confirm end-to-end behavioral correctness.
- **Boundary tests**: Compile and run test cases for `fib(0)`, `fib(1)`, and `fib(2)` to ensure the `le_i32` condition and loop logic handle edge cases correctly.
- **Negative input tests**: Test `fib` with negative inputs to document or verify the intended behavior of the signed integer comparison (`icmp sle`).
```
</details>
