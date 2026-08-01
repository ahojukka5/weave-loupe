# Weave Loupe Audit Report

## Verdict

- **Status:** OK
- **Code:** none
- **Reason:** No blocking defect found.

## Reproducibility

- **Report content SHA-256:** `dd489c8e74bc69a5c4f9be6f05cd4df6ae297011bd1754e2520be82b56fc63b3`
- **Audit timestamp (UTC):** `2026-08-01T20:46:47+00:00`
- **Re-audit no later than (UTC):** `2026-08-31T20:46:47+00:00`
- **Maximum audit age:** `30` days
- **Audited input invalidation:** `any source or runtime matrix hash change`
- **Compiler binary invalidation:** `any compiler binary hash change`
- **Auditor invalidation:** `any audit implementation fingerprint change`
- **Model invalidation:** `any configured LLM model or endpoint change`
- **Request limit invalidation:** `any configured LLM max-token change`
- **Development compiler invalidation:** `any compiler version change`
- **Identity attestation upgrade:** `required when command identity becomes available`
- **Audited source Git SHA:** `4bd74de32c87221ef828ee0da2c3c1263abe9c4a`
- **Source tree state:** `clean`
- **Weave Loupe Git SHA:** `4bd74de32c87221ef828ee0da2c3c1263abe9c4a`
- **Auditor content SHA-256:** `feb6f4b141181eeb0982aa71215cd4a860bd581043365fd1da9ee6d64a54afe6`
- **weavec Git SHA:** `254cce2108c771e651f875ab97965c72e7416e6d`
- **weavec binary SHA-256:** `cc26164a503490b3706ef5168171dd56a72ac31905203d55315e9c5c758b9dbb`
- **weavec version:** `weavec v0.3.0+git.254cce2108c7`
- **weavec build kind:** `development`
- **weavec version source:** `command`
- **Native analysis supported:** `True`
- **Native target architecture:** `x86_64`
- **Native object format:** `elf`
- **Native disassembler:** `llvm-objdump`
- **Native disassembler version:** `unavailable`
- **Native parser format:** `weave-loupe-native-disassembly-v1`
- **Native analysis failure:** `unavailable`
- **LLM endpoint:** `https://integrate.api.nvidia.com/v1`
- **LLM model:** `z-ai/glm-5.2`
- **LLM max tokens:** `4096`
- **LLM temperature:** `0.0`
- **LLM prompt SHA-256:** `d18ccdb94ac4e54c746a5948c2b32414e19eb8987c5cd59c7728e210fddf215f`
- **LLM request SHA-256:** `1d0c2e12684c58033f66b5640a22755a3622bf7b5c6735fa2a1f711ad4de0d06`
- **Provider-reported model:** `z-ai/glm-5.2`
- **Provider response ID:** `chatcmpl-53bc663a-5404-46bf-9046-f87265d46acf`
- **Provider system fingerprint:** `unavailable`
- **Provider finish reason:** `stop`
- **Provider created (Unix):** `1785617208`
- **Provider prompt tokens:** `14492`
- **Provider completion tokens:** `1060`
- **Provider total tokens:** `15552`
- **GitHub run ID:** `30717683339`
- **GitHub workflow SHA:** `61152d3daef68b4a6ccd405537a7c32b33732bd7`

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

- Source `docs/audit/fibonacci.weave` — SHA-256 `6cad78b00aaa67b434c4d7a920a3c9065bf7d7a802f5881ef831602e3e48b3d6` — 935 bytes
- Runtime matrix `docs/audit/fibonacci.audit.json` — SHA-256 `4032e56fd1ee0c869bded117fe11d6a7e3d00d3dd7c57edea7991230d7ef6ee6`

## Captured evidence

- `assembly` — SHA-256 `c9ada3f9b21f676366d69be9e0d67e8a8db3786a9e4fd3783f3dbe706b368e97`
- `build_manifest` — SHA-256 `65a263398b099227d87ddd2ca2b14a3d7c6a2cd6d1d612979ef4ad7e38d59859`
- `diagnostics` — SHA-256 `a40b573053cda943c381742ad672108b1c8985ecc97e2f21dfa604094e31ff63`
- `disassembly` — SHA-256 `3cbd74406c2576b10b521535213c7d2d51e0c4ee5a24e490febfdcf8afc0b94b`
- `executable` — SHA-256 `90a568e286f9d2d5ae1873d965c2364f89a46d071136e1cd18a1914f9e95ef89`
- `llvm` — SHA-256 `29db89767b2df7c2cd55d3d4a8b35057072f92f81479e4ccd67d7903291c946e`
- `optimization_record` — SHA-256 `3521b76a68875746bebe1b706f3129da67abd93aded7e79ead467f4008c16fa3`
- `optimized_llvm` — SHA-256 `057f82c503f63153db2cd05433300ee212c02b0986729d8497760c3595e18a21`
- `trace` — SHA-256 `973c782fd9436e06f7203fea9af0c26a62e0973bd46db644f14c0bb8e4e4f0c5`
- `wir` — SHA-256 `1dee19643aecdad282706b636fe965940cd06be29860f07d8352286514b354d9`

## Model review coverage and requests

- **Review format:** `weave-loupe-review-plan-v1`
- **Review mode:** `single`
- **Token estimator:** `utf8-byte-upper-bound-v1`
- **Estimated complete review tokens:** `47075`
- **Request count:** `1`
- **Maximum total tokens:** `524288`
- **Maximum request tokens:** `98304`
- **Maximum artifact tokens:** `262144`
- **Artifact-review completion tokens:** `512`

### Artifact coverage

#### `metadata` — Reproducibility metadata

- Language: `json`
- UTF-8 bytes: `9183`
- Estimated tokens: `9199`
- SHA-256: `961c0a0b98198075379f0673098640c7cef4b3da0b345fd0c1cb8232dccb4e4d`
- Complete coverage: `True`
- Covered ranges: `metadata:[0, 9183)@961c0a0b98198075379f0673098640c7cef4b3da0b345fd0c1cb8232dccb4e4d`

#### `source` — Weave source

- Language: `lisp`
- UTF-8 bytes: `970`
- Estimated tokens: `986`
- SHA-256: `08cc4b43b17a3614d68ae9fe381c7f33aac01c5ddd56b11efe6c79a9d9593dae`
- Complete coverage: `True`
- Covered ranges: `source:[0, 970)@08cc4b43b17a3614d68ae9fe381c7f33aac01c5ddd56b11efe6c79a9d9593dae`

#### `wir` — WIR review projection

- Language: `lisp`
- UTF-8 bytes: `670`
- Estimated tokens: `686`
- SHA-256: `725de77fa242cc92db08ca66c30d686c2c1264a3e59555bcf0da5c88347dc34c`
- Complete coverage: `True`
- Covered ranges: `wir:[0, 670)@725de77fa242cc92db08ca66c30d686c2c1264a3e59555bcf0da5c88347dc34c`

#### `raw_llvm` — Raw LLVM IR

- Language: `llvm`
- UTF-8 bytes: `3418`
- Estimated tokens: `3434`
- SHA-256: `29db89767b2df7c2cd55d3d4a8b35057072f92f81479e4ccd67d7903291c946e`
- Complete coverage: `True`
- Covered ranges: `raw_llvm:[0, 3418)@29db89767b2df7c2cd55d3d4a8b35057072f92f81479e4ccd67d7903291c946e`

#### `optimized_llvm` — Optimized LLVM IR

- Language: `llvm`
- UTF-8 bytes: `444`
- Estimated tokens: `460`
- SHA-256: `057f82c503f63153db2cd05433300ee212c02b0986729d8497760c3595e18a21`
- Complete coverage: `True`
- Covered ranges: `optimized_llvm:[0, 444)@057f82c503f63153db2cd05433300ee212c02b0986729d8497760c3595e18a21`

#### `assembly` — Target assembly

- Language: `asm`
- UTF-8 bytes: `390`
- Estimated tokens: `406`
- SHA-256: `c9ada3f9b21f676366d69be9e0d67e8a8db3786a9e4fd3783f3dbe706b368e97`
- Complete coverage: `True`
- Covered ranges: `assembly:[0, 390)@c9ada3f9b21f676366d69be9e0d67e8a8db3786a9e4fd3783f3dbe706b368e97`

#### `disassembly` — Linked executable disassembly

- Language: `asm`
- UTF-8 bytes: `5681`
- Estimated tokens: `5697`
- SHA-256: `3cbd74406c2576b10b521535213c7d2d51e0c4ee5a24e490febfdcf8afc0b94b`
- Complete coverage: `True`
- Covered ranges: `disassembly:[0, 5681)@3cbd74406c2576b10b521535213c7d2d51e0c4ee5a24e490febfdcf8afc0b94b`

#### `optimization_record` — LLVM optimization record

- Language: `yaml`
- UTF-8 bytes: `2406`
- Estimated tokens: `2422`
- SHA-256: `3521b76a68875746bebe1b706f3129da67abd93aded7e79ead467f4008c16fa3`
- Complete coverage: `True`
- Covered ranges: `optimization_record:[0, 2406)@3521b76a68875746bebe1b706f3129da67abd93aded7e79ead467f4008c16fa3`

#### `diagnostics` — Diagnostics

- Language: `json`
- UTF-8 bytes: `148`
- Estimated tokens: `164`
- SHA-256: `9683b322333373cb4d9534fef10e27edba462e771e2b03e02108d5c6a7fc71ca`
- Complete coverage: `True`
- Covered ranges: `diagnostics:[0, 148)@9683b322333373cb4d9534fef10e27edba462e771e2b03e02108d5c6a7fc71ca`

#### `analysis` — Complete deterministic analysis

- Language: `json`
- UTF-8 bytes: `11056`
- Estimated tokens: `11072`
- SHA-256: `199a6647144b48dd3aebc36a25e4490702bf76d57a5237b4b658db303a1f7d1d`
- Complete coverage: `True`
- Covered ranges: `analysis:[0, 11056)@199a6647144b48dd3aebc36a25e4490702bf76d57a5237b4b658db303a1f7d1d`

#### `build_manifest` — Compiler build manifest

- Language: `json`
- UTF-8 bytes: `688`
- Estimated tokens: `704`
- SHA-256: `65a263398b099227d87ddd2ca2b14a3d7c6a2cd6d1d612979ef4ad7e38d59859`
- Complete coverage: `True`
- Covered ranges: `build_manifest:[0, 688)@65a263398b099227d87ddd2ca2b14a3d7c6a2cd6d1d612979ef4ad7e38d59859`

#### `trace` — Compiler trace

- Language: `json`
- UTF-8 bytes: `205`
- Estimated tokens: `221`
- SHA-256: `973c782fd9436e06f7203fea9af0c26a62e0973bd46db644f14c0bb8e4e4f0c5`
- Complete coverage: `True`
- Covered ranges: `trace:[0, 205)@973c782fd9436e06f7203fea9af0c26a62e0973bd46db644f14c0bb8e4e4f0c5`


### Review requests

#### `single-0001` — single

- Estimated input tokens: `42979`
- Reserved output tokens: `4096`
- Depends on: none
- Covered ranges: `metadata:[0, 9183)@961c0a0b98198075379f0673098640c7cef4b3da0b345fd0c1cb8232dccb4e4d`, `source:[0, 970)@08cc4b43b17a3614d68ae9fe381c7f33aac01c5ddd56b11efe6c79a9d9593dae`, `wir:[0, 670)@725de77fa242cc92db08ca66c30d686c2c1264a3e59555bcf0da5c88347dc34c`, `raw_llvm:[0, 3418)@29db89767b2df7c2cd55d3d4a8b35057072f92f81479e4ccd67d7903291c946e`, `optimized_llvm:[0, 444)@057f82c503f63153db2cd05433300ee212c02b0986729d8497760c3595e18a21`, `assembly:[0, 390)@c9ada3f9b21f676366d69be9e0d67e8a8db3786a9e4fd3783f3dbe706b368e97`, `disassembly:[0, 5681)@3cbd74406c2576b10b521535213c7d2d51e0c4ee5a24e490febfdcf8afc0b94b`, `optimization_record:[0, 2406)@3521b76a68875746bebe1b706f3129da67abd93aded7e79ead467f4008c16fa3`, `diagnostics:[0, 148)@9683b322333373cb4d9534fef10e27edba462e771e2b03e02108d5c6a7fc71ca`, `analysis:[0, 11056)@199a6647144b48dd3aebc36a25e4490702bf76d57a5237b4b658db303a1f7d1d`, `build_manifest:[0, 688)@65a263398b099227d87ddd2ca2b14a3d7c6a2cd6d1d612979ef4ad7e38d59859`, `trace:[0, 205)@973c782fd9436e06f7203fea9af0c26a62e0973bd46db644f14c0bb8e4e4f0c5`
- Prompt SHA-256: `d18ccdb94ac4e54c746a5948c2b32414e19eb8987c5cd59c7728e210fddf215f`
- Request SHA-256: `1d0c2e12684c58033f66b5640a22755a3622bf7b5c6735fa2a1f711ad4de0d06`
- Requested model: `z-ai/glm-5.2`
- Provider model: `z-ai/glm-5.2`
- Provider response ID: `chatcmpl-53bc663a-5404-46bf-9046-f87265d46acf`
- Finish reason: `stop`
- Provider prompt tokens: `14492`
- Provider completion tokens: `1060`
- Provider total tokens: `15552`

## Complete compiler evidence

This section contains the exact evidence reviewed by the model so that the
source-to-native lowering can also be inspected manually.

### Weave source

```lisp
--- docs/audit/fibonacci.weave ---
; Canonical Weave Loupe audit corpus example.
; Computes fib(10) iteratively; the expected signed i32 return value is 55.
; The standalone executable must not retain fib after main is constant-folded.

(program
  (name "fibonacci")
  (version "0.1")
  (fn fib
    (params (n i32))
    (returns i32)
    (do
      (if
        (condition
          (le_i32 n (const_i32 1)))
        (then
          (do
            (return n)))
        (else
          (do)))
      (let previous i32 (const_i32 0))
      (let current i32 (const_i32 1))
      (let index i32 (const_i32 2))
      (while
        (condition
          (le_i32 index n))
        (do
          (let next i32 (add_i32 previous current))
          (set previous current)
          (set current next)
          (set index (add_i32 index (const_i32 1)))))
      (return current)))
  (entry main
    (params)
    (returns i32)
    (do
      (return (call_i32 fib (const_i32 10))))))
```

### WIR (provenance comments hidden)

```lisp
(core-module
  (core-version 2)
  (decls
    (fn
      fib
      (params (n i32))
      (returns i32)
      (do
        (if (condition (le_i32 n (const_i32 1))) (then (do (return n))) (else (do)))
        (let previous i32 (const_i32 0))
        (let current i32 (const_i32 1))
        (let index i32 (const_i32 2))
        (while
          (condition (le_i32 index n))
          (do
            (let next i32 (add_i32 previous current))
            (set previous current)
            (set current next)
            (set index (add_i32 index (const_i32 1)))))
        (return current)))
    (fn main (params) (returns i32) (do (return (call_i32 fib (const_i32 10)))))))
```

### Raw LLVM IR

```llvm
; generated by weavec
; source: /tmp/weavec-build-YV4eJr/program.wir
; core-version: 2

; weave.source kind=function index=0 bytes=836..933 wir-bytes=3030..3582 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave"
; function: main
; params: none
; returns: i32
define i32 @main() {
entry:
; weave.source kind=statement index=0 bytes=893..931 wir-bytes=3338..3580 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave"
  ; return
  %t0 = call i32 @fib(i32 10)
  ret i32 %t0
}

; weave.source kind=function index=0 bytes=252..833 wir-bytes=176..2991 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave"
; function: fib
; params: i32
; returns: i32
define internal i32 @fib(i32 %n) {
entry:
  %previous.addr = alloca i32
  %current.addr = alloca i32
  %index.addr = alloca i32
; weave.source kind=statement index=0 bytes=313..455 wir-bytes=593..1247 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave"
  ; if condition
  %t0 = icmp sle i32 %n, 1
  br i1 %t0, label %then, label %endif
then:
  ; then
; weave.source kind=statement index=0 bytes=412..422 wir-bytes=1086..1130 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave"
  ; return
  ret i32 %n
endif:
; weave.source kind=statement index=0 bytes=462..494 wir-bytes=1282..1450 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave"
  ; let previous
  store i32 0, ptr %previous.addr
; weave.source kind=statement index=0 bytes=501..532 wir-bytes=1485..1652 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave"
  ; let current
  store i32 1, ptr %current.addr
; weave.source kind=statement index=0 bytes=539..568 wir-bytes=1687..1852 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave"
  ; let index
  store i32 2, ptr %index.addr
; weave.source kind=statement index=0 bytes=575..808 wir-bytes=1887..2904 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave"
  ; while condition
  br label %while.cond1
while.cond1:
  %t1 = load i32, ptr %index.addr
  %t2 = icmp sle i32 %t1, %n
  br i1 %t2, label %while.body1, label %while.end1
while.body1:
  ; while body
; weave.source kind=statement index=0 bytes=651..692 wir-bytes=2233..2444 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave"
  %t3 = load i32, ptr %previous.addr
  %t4 = load i32, ptr %current.addr
  %t5 = add i32 %t3, %t4
  ; let next
; weave.source kind=statement index=0 bytes=703..725 wir-bytes=2479..2535 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave"
  ; set previous
  %t6 = load i32, ptr %current.addr
  store i32 %t6, ptr %previous.addr
; weave.source kind=statement index=0 bytes=736..754 wir-bytes=2570..2622 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave"
  ; set current
  store i32 %t5, ptr %current.addr
; weave.source kind=statement index=0 bytes=765..806 wir-bytes=2657..2902 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave"
  ; set index
  %t7 = load i32, ptr %index.addr
  %t8 = add i32 %t7, 1
  store i32 %t8, ptr %index.addr
  br label %while.cond1
while.end1:
; weave.source kind=statement index=0 bytes=815..831 wir-bytes=2939..2989 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave"
  ; return
  %t9 = load i32, ptr %current.addr
  ret i32 %t9
}
```

### Optimized LLVM IR

```llvm
; ModuleID = '<stdin>'
source_filename = "<stdin>"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(none)
define noundef i32 @main() local_unnamed_addr #0 {
entry:
  ret i32 55
}

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn memory(none) }
```

### Target assembly

```asm
	.text
	.file	"<stdin>"
	.globl	main                            # -- Begin function main
	.p2align	4, 0x90
	.type	main,@function
main:                                   # @main
# %bb.0:                                # %entry
	movl	$55, %eax
	retq
.Lfunc_end0:
	.size	main, .Lfunc_end0-main
                                        # -- End function
	.section	".note.GNU-stack","",@progbits
```

### Linked executable disassembly

```asm

<stdin>:	file format elf64-x86-64

Disassembly of section .init:

0000000000001000 <_init>:
    1000: f3 0f 1e fa                  	endbr64
    1004: 48 83 ec 08                  	subq	$0x8, %rsp
    1008: 48 8b 05 c1 2f 00 00         	movq	0x2fc1(%rip), %rax      # 0x3fd0 <__libc_start_main@GLIBC_2.34+0x3fd0>
    100f: 48 85 c0                     	testq	%rax, %rax
    1012: 74 02                        	je	0x1016 <_init+0x16>
    1014: ff d0                        	callq	*%rax
    1016: 48 83 c4 08                  	addq	$0x8, %rsp
    101a: c3                           	retq

Disassembly of section .plt:

0000000000001020 <.plt>:
    1020: ff 35 ca 2f 00 00            	pushq	0x2fca(%rip)            # 0x3ff0 <_GLOBAL_OFFSET_TABLE_+0x8>
    1026: ff 25 cc 2f 00 00            	jmpq	*0x2fcc(%rip)           # 0x3ff8 <_GLOBAL_OFFSET_TABLE_+0x10>
    102c: 0f 1f 40 00                  	nopl	(%rax)

Disassembly of section .plt.got:

0000000000001030 <__cxa_finalize@plt>:
    1030: ff 25 aa 2f 00 00            	jmpq	*0x2faa(%rip)           # 0x3fe0 <__libc_start_main@GLIBC_2.34+0x3fe0>
    1036: 66 90                        	nop

Disassembly of section .text:

0000000000001040 <_start>:
    1040: f3 0f 1e fa                  	endbr64
    1044: 31 ed                        	xorl	%ebp, %ebp
    1046: 49 89 d1                     	movq	%rdx, %r9
    1049: 5e                           	popq	%rsi
    104a: 48 89 e2                     	movq	%rsp, %rdx
    104d: 48 83 e4 f0                  	andq	$-0x10, %rsp
    1051: 50                           	pushq	%rax
    1052: 54                           	pushq	%rsp
    1053: 45 31 c0                     	xorl	%r8d, %r8d
    1056: 31 c9                        	xorl	%ecx, %ecx
    1058: 48 8d 3d d1 00 00 00         	leaq	0xd1(%rip), %rdi        # 0x1130 <main>
    105f: ff 15 5b 2f 00 00            	callq	*0x2f5b(%rip)           # 0x3fc0 <__libc_start_main@GLIBC_2.34+0x3fc0>
    1065: f4                           	hlt
    1066: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

0000000000001070 <deregister_tm_clones>:
    1070: 48 8d 3d 91 2f 00 00         	leaq	0x2f91(%rip), %rdi      # 0x4008 <completed.0>
    1077: 48 8d 05 8a 2f 00 00         	leaq	0x2f8a(%rip), %rax      # 0x4008 <completed.0>
    107e: 48 39 f8                     	cmpq	%rdi, %rax
    1081: 74 15                        	je	0x1098 <deregister_tm_clones+0x28>
    1083: 48 8b 05 3e 2f 00 00         	movq	0x2f3e(%rip), %rax      # 0x3fc8 <__libc_start_main@GLIBC_2.34+0x3fc8>
    108a: 48 85 c0                     	testq	%rax, %rax
    108d: 74 09                        	je	0x1098 <deregister_tm_clones+0x28>
    108f: ff e0                        	jmpq	*%rax
    1091: 0f 1f 80 00 00 00 00         	nopl	(%rax)
    1098: c3                           	retq
    1099: 0f 1f 80 00 00 00 00         	nopl	(%rax)

00000000000010a0 <register_tm_clones>:
    10a0: 48 8d 3d 61 2f 00 00         	leaq	0x2f61(%rip), %rdi      # 0x4008 <completed.0>
    10a7: 48 8d 35 5a 2f 00 00         	leaq	0x2f5a(%rip), %rsi      # 0x4008 <completed.0>
    10ae: 48 29 fe                     	subq	%rdi, %rsi
    10b1: 48 89 f0                     	movq	%rsi, %rax
    10b4: 48 c1 ee 3f                  	shrq	$0x3f, %rsi
    10b8: 48 c1 f8 03                  	sarq	$0x3, %rax
    10bc: 48 01 c6                     	addq	%rax, %rsi
    10bf: 48 d1 fe                     	sarq	%rsi
    10c2: 74 14                        	je	0x10d8 <register_tm_clones+0x38>
    10c4: 48 8b 05 0d 2f 00 00         	movq	0x2f0d(%rip), %rax      # 0x3fd8 <__libc_start_main@GLIBC_2.34+0x3fd8>
    10cb: 48 85 c0                     	testq	%rax, %rax
    10ce: 74 08                        	je	0x10d8 <register_tm_clones+0x38>
    10d0: ff e0                        	jmpq	*%rax
    10d2: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
    10d8: c3                           	retq
    10d9: 0f 1f 80 00 00 00 00         	nopl	(%rax)

00000000000010e0 <__do_global_dtors_aux>:
    10e0: f3 0f 1e fa                  	endbr64
    10e4: 80 3d 1d 2f 00 00 00         	cmpb	$0x0, 0x2f1d(%rip)      # 0x4008 <completed.0>
    10eb: 75 2b                        	jne	0x1118 <__do_global_dtors_aux+0x38>
    10ed: 55                           	pushq	%rbp
    10ee: 48 83 3d ea 2e 00 00 00      	cmpq	$0x0, 0x2eea(%rip)      # 0x3fe0 <__libc_start_main@GLIBC_2.34+0x3fe0>
    10f6: 48 89 e5                     	movq	%rsp, %rbp
    10f9: 74 0c                        	je	0x1107 <__do_global_dtors_aux+0x27>
    10fb: 48 8b 3d fe 2e 00 00         	movq	0x2efe(%rip), %rdi      # 0x4000 <__dso_handle>
    1102: e8 29 ff ff ff               	callq	0x1030 <__cxa_finalize@plt>
    1107: e8 64 ff ff ff               	callq	0x1070 <deregister_tm_clones>
    110c: c6 05 f5 2e 00 00 01         	movb	$0x1, 0x2ef5(%rip)      # 0x4008 <completed.0>
    1113: 5d                           	popq	%rbp
    1114: c3                           	retq
    1115: 0f 1f 00                     	nopl	(%rax)
    1118: c3                           	retq
    1119: 0f 1f 80 00 00 00 00         	nopl	(%rax)

0000000000001120 <frame_dummy>:
    1120: f3 0f 1e fa                  	endbr64
    1124: e9 77 ff ff ff               	jmp	0x10a0 <register_tm_clones>
    1129: 0f 1f 80 00 00 00 00         	nopl	(%rax)

0000000000001130 <main>:
    1130: b8 37 00 00 00               	movl	$0x37, %eax
    1135: c3                           	retq

Disassembly of section .fini:

0000000000001138 <_fini>:
    1138: f3 0f 1e fa                  	endbr64
    113c: 48 83 ec 08                  	subq	$0x8, %rsp
    1140: 48 83 c4 08                  	addq	$0x8, %rsp
    1144: c3                           	retq
```

### LLVM optimization record

```yaml
# weavec optimization stage: llvm-ir
--- !Passed
Pass:            loop-delete
Name:            Invariant
Function:        fib
Args:
  - String:          Loop deleted because it is invariant
...
--- !Passed
Pass:            inline
Name:            Inlined
Function:        main
Args:
  - String:          ''''
  - Callee:          fib
  - String:          ''' inlined into '''
  - Caller:          main
  - String:          ''''
  - String:          ' with '
  - String:          '(cost='
  - Cost:            '-15035'
  - String:          ', threshold='
  - Threshold:       '375'
  - String:          ')'
...

# weavec optimization stage: target-codegen
--- !Analysis
Pass:            size-info
Name:            FunctionMISizeChange
Function:        main
Args:
  - Pass:            'X86 DAG->DAG Instruction Selection'
  - String:          ': Function: '
  - Function:        main
  - String:          ': '
  - String:          'MI Instruction count changed from '
  - MIInstrsBefore:  '0'
  - String:          ' to '
  - MIInstrsAfter:   '3'
  - String:          '; Delta: '
  - Delta:           '3'
...
--- !Analysis
Pass:            size-info
Name:            FunctionMISizeChange
Function:        main
Args:
  - Pass:            Peephole Optimizations
  - String:          ': Function: '
  - Function:        main
  - String:          ': '
  - String:          'MI Instruction count changed from '
  - MIInstrsBefore:  '3'
  - String:          ' to '
  - MIInstrsAfter:   '2'
  - String:          '; Delta: '
  - Delta:           '-1'
...
--- !Analysis
Pass:            prologepilog
Name:            StackSize
Function:        main
Args:
  - NumStackBytes:   '0'
  - String:          ' stack bytes in function '''
  - Function:        main
  - String:          ''''
...
--- !Analysis
Pass:            stack-frame-layout
Name:            StackLayout
Function:        main
Args:
  - String:          "\nFunction: main"
...
--- !Analysis
Pass:            asm-printer
Name:            InstructionMix
Function:        main
Args:
  - String:          'BasicBlock: '
  - BasicBlock:      entry
  - String:          "\n"
  - String:          ''
  - String:          ': '
  - INST_:           '2'
  - String:          "\n"
...
--- !Analysis
Pass:            asm-printer
Name:            InstructionCount
Function:        main
Args:
  - NumInstructions: '2'
  - String:          ' instructions in function'
...
```

### Optimized LLVM contract

```json
{
  "configured": true,
  "failures": [],
  "format": "weave-loupe-optimized-llvm-budget-result-v1",
  "limits": {
    "max_alloca": 0,
    "max_basic_blocks": 1,
    "max_br": 0,
    "max_call": 0,
    "max_functions": 1,
    "max_identity_adds": 0,
    "max_instructions": 1,
    "max_invoke": 0,
    "max_load": 0,
    "max_phi": 0,
    "max_poison_uses": 0,
    "max_ret": 1,
    "max_store": 0,
    "max_switch": 0,
    "max_undef_uses": 0,
    "min_basic_blocks": 1,
    "min_functions": 1,
    "min_instructions": 1,
    "min_ret": 1,
    "required_defined_functions": [
      "main"
    ]
  },
  "observed": {
    "add": 0,
    "alloca": 0,
    "anonymous_ssa_lines": 0,
    "basic_blocks": 1,
    "br": 0,
    "call": 0,
    "call_targets": [],
    "defined_functions": [
      "main"
    ],
    "functions": 1,
    "icmp": 0,
    "identity_adds": 0,
    "instructions": 1,
    "invoke": 0,
    "load": 0,
    "mul": 0,
    "numeric_blocks": 0,
    "phi": 0,
    "poison_uses": 0,
    "ret": 1,
    "sdiv": 0,
    "select": 0,
    "store": 0,
    "sub": 0,
    "switch": 0,
    "udiv": 0,
    "undef_uses": 0
  },
  "passed": true,
  "sidecar": "docs/audit/fibonacci.audit.json",
  "sidecar_sha256": "4032e56fd1ee0c869bded117fe11d6a7e3d00d3dd7c57edea7991230d7ef6ee6"
}
```

### Native optimization budget

```json
{
  "configured": true,
  "failures": [],
  "format": "weave-loupe-native-budget-result-v1",
  "limits": {
    "functions": {
      "main": {
        "max_backward_conditional_branches": 0,
        "max_direct_calls": 0,
        "max_indirect_calls": 0,
        "max_instructions": 2,
        "max_padding_instructions": 0
      }
    },
    "max_program_owned_functions": 1,
    "max_reachable_program_functions": 1,
    "max_unreachable_program_functions": 0,
    "max_unreachable_program_instructions": 0
  },
  "observed": {
    "functions": {
      "main": {
        "backward_conditional_branches": 0,
        "direct_call_targets": [],
        "direct_calls": 0,
        "indirect_calls": 0,
        "instructions": 2,
        "padding_instructions": 0,
        "present": true
      }
    },
    "program_owned_functions": 1,
    "reachable_program_functions": 1,
    "unreachable_program_functions": 0,
    "unreachable_program_instructions": 0
  },
  "passed": true,
  "sidecar": "docs/audit/fibonacci.audit.json",
  "sidecar_sha256": "4032e56fd1ee0c869bded117fe11d6a7e3d00d3dd7c57edea7991230d7ef6ee6"
}
```

### Runtime execution matrix

```json
{
  "case_count": 1,
  "cases": [
    {
      "actual": {
        "elapsed_seconds": 0.010923,
        "exit_code": 55,
        "process_count_enforcement": "delegated",
        "returncode": 55,
        "signal": null,
        "stderr": "",
        "stderr_bytes": 0,
        "stderr_overflowed": false,
        "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "stderr_stored_bytes": 0,
        "stderr_truncated_bytes": 0,
        "stdout": "",
        "stdout_bytes": 0,
        "stdout_overflowed": false,
        "stdout_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "stdout_stored_bytes": 0,
        "stdout_truncated_bytes": 0,
        "termination_reason": "exited"
      },
      "command": [
        "program"
      ],
      "environment": {},
      "expected": {
        "exit_code": 55,
        "stderr": "",
        "stdout": ""
      },
      "failures": [],
      "name": "constant-fibonacci",
      "passed": true,
      "stdin": "",
      "timed_out": false
    }
  ],
  "configured": true,
  "executable_sha256": "90a568e286f9d2d5ae1873d965c2364f89a46d071136e1cd18a1914f9e95ef89",
  "format": "weave-loupe-runtime-matrix-v1",
  "inherit_environment": false,
  "limits": {
    "address_space_bytes": 536870912,
    "cpu_seconds": 6.0,
    "excerpt_bytes_per_stream": 16384,
    "file_size_bytes": 67108864,
    "format": "weave-loupe-process-limits-v1",
    "output_bytes_per_stream": 1048576,
    "process_count": 118,
    "resource_limits_supported": true,
    "timeout_seconds": 5.0
  },
  "passed": true,
  "sandbox": {
    "active": true,
    "backend": "bubblewrap",
    "environment": "explicit-only",
    "filesystem": "read-only-system-and-declared-inputs",
    "format": "weave-loupe-runtime-sandbox-v1",
    "namespaces": [
      "user",
      "network",
      "pid",
      "ipc",
      "uts",
      "cgroup"
    ],
    "network": "disabled",
    "process_count_enforcement": "sandbox-prlimit",
    "writable_paths": [
      "/tmp",
      "/work"
    ]
  },
  "sidecar": "docs/audit/fibonacci.audit.json",
  "sidecar_sha256": "4032e56fd1ee0c869bded117fe11d6a7e3d00d3dd7c57edea7991230d7ef6ee6",
  "timeout_seconds": 5.0
}
```

### Diagnostics

```json
{
  "diagnostics": [],
  "exit_code": 0,
  "format": "weavec-diagnostics-v1",
  "phase": "complete",
  "raw_exit_code": 0,
  "status": "succeeded"
}
```

### Deterministic analysis

```json
{
  "compiler_exit_code": 0,
  "diagnostics": {
    "available": true,
    "items": 0,
    "severities": {}
  },
  "evidence": {
    "assembly": true,
    "build_manifest": true,
    "diagnostics": true,
    "disassembly": true,
    "llvm": true,
    "optimization_record": true,
    "optimized_llvm": true,
    "trace": true,
    "wir": true
  },
  "format": "weave-loupe-analysis-v1",
  "llvm": {
    "add": 2,
    "alloca": 3,
    "anonymous_ssa_lines": 0,
    "basic_blocks": 7,
    "br": 4,
    "call": 1,
    "functions": 2,
    "icmp": 2,
    "identity_adds": 0,
    "instructions": 27,
    "invoke": 0,
    "load": 6,
    "mul": 0,
    "numeric_blocks": 0,
    "phi": 0,
    "poison_uses": 0,
    "provenance_comments": 14,
    "ret": 3,
    "sdiv": 0,
    "select": 0,
    "store": 6,
    "sub": 0,
    "switch": 0,
    "udiv": 0,
    "undef_uses": 0
  },
  "native": {
    "architecture": "x86_64",
    "available": true,
    "disassembler": "llvm-objdump",
    "disassembler_version": null,
    "entry_point": "main",
    "failure_reason": null,
    "functions": {
      ".plt": {
        "backward_branches": 0,
        "backward_conditional_branches": 0,
        "conditional_branches": 0,
        "direct_branches": 0,
        "direct_calls": [],
        "indirect_branches": 1,
        "indirect_calls": 0,
        "instructions": 2,
        "padding_instructions": 1,
        "returns": 0,
        "unconditional_branches": 1
      },
      "__cxa_finalize@plt": {
        "backward_branches": 0,
        "backward_conditional_branches": 0,
        "conditional_branches": 0,
        "direct_branches": 0,
        "direct_calls": [],
        "indirect_branches": 1,
        "indirect_calls": 0,
        "instructions": 1,
        "padding_instructions": 1,
        "returns": 0,
        "unconditional_branches": 1
      },
      "__do_global_dtors_aux": {
        "backward_branches": 0,
        "backward_conditional_branches": 0,
        "conditional_branches": 2,
        "direct_branches": 2,
        "direct_calls": [
          "__cxa_finalize@plt",
          "deregister_tm_clones"
        ],
        "indirect_branches": 0,
        "indirect_calls": 0,
        "instructions": 14,
        "padding_instructions": 2,
        "returns": 2,
        "unconditional_branches": 0
      },
      "_fini": {
        "backward_branches": 0,
        "backward_conditional_branches": 0,
        "conditional_branches": 0,
        "direct_branches": 0,
        "direct_calls": [],
        "indirect_branches": 0,
        "indirect_calls": 0,
        "instructions": 4,
        "padding_instructions": 0,
        "returns": 1,
        "unconditional_branches": 0
      },
      "_init": {
        "backward_branches": 0,
        "backward_conditional_branches": 0,
        "conditional_branches": 1,
        "direct_branches": 1,
        "direct_calls": [],
        "indirect_branches": 0,
        "indirect_calls": 1,
        "instructions": 8,
        "padding_instructions": 0,
        "returns": 1,
        "unconditional_branches": 0
      },
      "_start": {
        "backward_branches": 0,
        "backward_conditional_branches": 0,
        "conditional_branches": 0,
        "direct_branches": 0,
        "direct_calls": [],
        "indirect_branches": 0,
        "indirect_calls": 1,
        "instructions": 13,
        "padding_instructions": 1,
        "returns": 0,
        "unconditional_branches": 0
      },
      "deregister_tm_clones": {
        "backward_branches": 0,
        "backward_conditional_branches": 0,
        "conditional_branches": 2,
        "direct_branches": 2,
        "direct_calls": [],
        "indirect_branches": 1,
        "indirect_calls": 0,
        "instructions": 9,
        "padding_instructions": 2,
        "returns": 1,
        "unconditional_branches": 1
      },
      "frame_dummy": {
        "backward_branches": 1,
        "backward_conditional_branches": 0,
        "conditional_branches": 0,
        "direct_branches": 1,
        "direct_calls": [],
        "indirect_branches": 0,
        "indirect_calls": 0,
        "instructions": 2,
        "padding_instructions": 1,
        "returns": 0,
        "unconditional_branches": 1
      },
      "main": {
        "backward_branches": 0,
        "backward_conditional_branches": 0,
        "conditional_branches": 0,
        "direct_branches": 0,
        "direct_calls": [],
        "indirect_branches": 0,
        "indirect_calls": 0,
        "instructions": 2,
        "padding_instructions": 0,
        "returns": 1,
        "unconditional_branches": 0
      },
      "register_tm_clones": {
        "backward_branches": 0,
        "backward_conditional_branches": 0,
        "conditional_branches": 2,
        "direct_branches": 2,
        "direct_calls": [],
        "indirect_branches": 1,
        "indirect_calls": 0,
        "instructions": 14,
        "padding_instructions": 2,
        "returns": 1,
        "unconditional_branches": 1
      }
    },
    "llvm_functions": [
      "main"
    ],
    "object_format": "elf",
    "parser_format": "weave-loupe-native-disassembly-v1",
    "program_owned_functions": [
      "main"
    ],
    "reachability_complete": true,
    "reachable_indirect_calls": 0,
    "reachable_program_functions": [
      "main"
    ],
    "runtime_functions": [],
    "supported": true,
    "unreachable_program_functions": [],
    "unreachable_program_instructions": 0
  },
  "native_budget": {
    "configured": true,
    "failures": [],
    "format": "weave-loupe-native-budget-result-v1",
    "limits": {
      "functions": {
        "main": {
          "max_backward_conditional_branches": 0,
          "max_direct_calls": 0,
          "max_indirect_calls": 0,
          "max_instructions": 2,
          "max_padding_instructions": 0
        }
      },
      "max_program_owned_functions": 1,
      "max_reachable_program_functions": 1,
      "max_unreachable_program_functions": 0,
      "max_unreachable_program_instructions": 0
    },
    "observed": {
      "functions": {
        "main": {
          "backward_conditional_branches": 0,
          "direct_call_targets": [],
          "direct_calls": 0,
          "indirect_calls": 0,
          "instructions": 2,
          "padding_instructions": 0,
          "present": true
        }
      },
      "program_owned_functions": 1,
      "reachable_program_functions": 1,
      "unreachable_program_functions": 0,
      "unreachable_program_instructions": 0
    },
    "passed": true,
    "sidecar": "docs/audit/fibonacci.audit.json",
    "sidecar_sha256": "4032e56fd1ee0c869bded117fe11d6a7e3d00d3dd7c57edea7991230d7ef6ee6"
  },
  "optimized_llvm": {
    "add": 0,
    "alloca": 0,
    "anonymous_ssa_lines": 0,
    "basic_blocks": 1,
    "br": 0,
    "call": 0,
    "functions": 1,
    "icmp": 0,
    "identity_adds": 0,
    "instructions": 1,
    "invoke": 0,
    "load": 0,
    "mul": 0,
    "numeric_blocks": 0,
    "phi": 0,
    "poison_uses": 0,
    "provenance_comments": 0,
    "ret": 1,
    "sdiv": 0,
    "select": 0,
    "store": 0,
    "sub": 0,
    "switch": 0,
    "udiv": 0,
    "undef_uses": 0
  },
  "optimized_llvm_budget": {
    "configured": true,
    "failures": [],
    "format": "weave-loupe-optimized-llvm-budget-result-v1",
    "limits": {
      "max_alloca": 0,
      "max_basic_blocks": 1,
      "max_br": 0,
      "max_call": 0,
      "max_functions": 1,
      "max_identity_adds": 0,
      "max_instructions": 1,
      "max_invoke": 0,
      "max_load": 0,
      "max_phi": 0,
      "max_poison_uses": 0,
      "max_ret": 1,
      "max_store": 0,
      "max_switch": 0,
      "max_undef_uses": 0,
      "min_basic_blocks": 1,
      "min_functions": 1,
      "min_instructions": 1,
      "min_ret": 1,
      "required_defined_functions": [
        "main"
      ]
    },
    "observed": {
      "add": 0,
      "alloca": 0,
      "anonymous_ssa_lines": 0,
      "basic_blocks": 1,
      "br": 0,
      "call": 0,
      "call_targets": [],
      "defined_functions": [
        "main"
      ],
      "functions": 1,
      "icmp": 0,
      "identity_adds": 0,
      "instructions": 1,
      "invoke": 0,
      "load": 0,
      "mul": 0,
      "numeric_blocks": 0,
      "phi": 0,
      "poison_uses": 0,
      "ret": 1,
      "sdiv": 0,
      "select": 0,
      "store": 0,
      "sub": 0,
      "switch": 0,
      "udiv": 0,
      "undef_uses": 0
    },
    "passed": true,
    "sidecar": "docs/audit/fibonacci.audit.json",
    "sidecar_sha256": "4032e56fd1ee0c869bded117fe11d6a7e3d00d3dd7c57edea7991230d7ef6ee6"
  },
  "runtime": {
    "case_count": 1,
    "cases": [
      {
        "actual": {
          "elapsed_seconds": 0.010923,
          "exit_code": 55,
          "process_count_enforcement": "delegated",
          "returncode": 55,
          "signal": null,
          "stderr": "",
          "stderr_bytes": 0,
          "stderr_overflowed": false,
          "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
          "stderr_stored_bytes": 0,
          "stderr_truncated_bytes": 0,
          "stdout": "",
          "stdout_bytes": 0,
          "stdout_overflowed": false,
          "stdout_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
          "stdout_stored_bytes": 0,
          "stdout_truncated_bytes": 0,
          "termination_reason": "exited"
        },
        "command": [
          "program"
        ],
        "environment": {},
        "expected": {
          "exit_code": 55,
          "stderr": "",
          "stdout": ""
        },
        "failures": [],
        "name": "constant-fibonacci",
        "passed": true,
        "stdin": "",
        "timed_out": false
      }
    ],
    "configured": true,
    "executable_sha256": "90a568e286f9d2d5ae1873d965c2364f89a46d071136e1cd18a1914f9e95ef89",
    "format": "weave-loupe-runtime-matrix-v1",
    "inherit_environment": false,
    "limits": {
      "address_space_bytes": 536870912,
      "cpu_seconds": 6.0,
      "excerpt_bytes_per_stream": 16384,
      "file_size_bytes": 67108864,
      "format": "weave-loupe-process-limits-v1",
      "output_bytes_per_stream": 1048576,
      "process_count": 118,
      "resource_limits_supported": true,
      "timeout_seconds": 5.0
    },
    "passed": true,
    "sandbox": {
      "active": true,
      "backend": "bubblewrap",
      "environment": "explicit-only",
      "filesystem": "read-only-system-and-declared-inputs",
      "format": "weave-loupe-runtime-sandbox-v1",
      "namespaces": [
        "user",
        "network",
        "pid",
        "ipc",
        "uts",
        "cgroup"
      ],
      "network": "disabled",
      "process_count_enforcement": "sandbox-prlimit",
      "writable_paths": [
        "/tmp",
        "/work"
      ]
    },
    "sidecar": "docs/audit/fibonacci.audit.json",
    "sidecar_sha256": "4032e56fd1ee0c869bded117fe11d6a7e3d00d3dd7c57edea7991230d7ef6ee6",
    "timeout_seconds": 5.0
  },
  "trace": {
    "actions": {},
    "categories": {},
    "events": 0,
    "passes": {}
  }
}
```

### Build manifest

```json
{
  "format": "weavec-build-manifest-v1",
  "status": "succeeded",
  "phase": "complete",
  "target": "x86_64-unknown-linux-gnu",
  "compiler": "/home/runner/work/weave-loupe/weave-loupe/.weave-tools/weavec/build/weavec",
  "runtime": "/home/runner/work/weave-loupe/weave-loupe/.weave-tools/weavec/build/../runtime/program.c",
  "optimizer": "clang",
  "codegen": "llc",
  "linker": "clang",
  "objdump": "llvm-objdump",
  "optimization": {
    "level": "O3",
    "cpu": "native",
    "tune_cpu": "native"
  },
  "output": "/tmp/loupe-audit-i1h1p3_k/.audit.loupe.zg5xfs4r/artifacts/program",
  "sources": [
    "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave"
  ]
}
```

### Compiler trace

```json
{
  "format": "weavec-compilation-trace-v1",
  "status": "succeeded",
  "phase": "complete",
  "sources": [
    "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave"
  ],
  "events": []
}
```

## LLM review

## Summary
The Weave compiler toolchain successfully compiles `docs/audit/fibonacci.weave` into a correct, safe, and ABI-valid native executable. The source computes `fib(10)` iteratively, and the expected signed i32 return value is 55. The cleaned WIR accurately preserves the source semantics, including the base case, iterative loop, and variable updates. The raw LLVM IR is valid, well-typed, and correctly translates the WIR semantics into SSA form with stack-allocated local variables. The LLVM optimizer completely constant-folds the program, inlining `fib` into `main`, deleting the invariant loop, and reducing the program to `ret i32 55`. The target assembly and linked executable disassembly confirm this by emitting a minimal `movl $55, %eax; retq` sequence for `main`. The x86_64 System V ABI is respected: the return value is placed in `%eax`, the stack is 16-byte aligned at the call site by the CRT prologue, and no callee-saved registers are touched. The configured runtime matrix executed the exact linked artifact and observed an exit code of 55, matching the expected sidecar value. Both the optimized LLVM contract and the native optimization budget passed without failures, and no compiler-generated overhead remains in the final code.

## Verification matrix
- Source semantics and expected result: PASS. The Weave source defines an iterative `fib` function and calls it with `10`. The expected return value is 55, as stated in the source comments and verified by the runtime matrix.
- Weave-to-WIR semantic preservation: PASS. The cleaned WIR accurately reflects the source: the `le_i32` condition, `let` bindings, `while` loop, `add_i32` arithmetic, and `set` assignments are all preserved.
- WIR-to-raw-LLVM semantic preservation: PASS. The raw LLVM IR uses `alloca` for local variables, `icmp sle` for the signed comparisons, and `add i32` for the arithmetic, matching the WIR operations exactly.
- Raw LLVM validity, SSA, types, and control flow: PASS. The raw LLVM IR is well-formed, uses correct SSA naming for temporaries, and has valid control-flow edges (`br` instructions matching `if` and `while` logic).
- Optimized LLVM semantic preservation: PASS. The optimized LLVM IR reduces `main` to `ret i32 55`, which is semantically equivalent to the source program's constant-folded result.
- Configured optimized LLVM metrics, functions, calls, and memory traffic: PASS. The optimized LLVM budget passed. The observed metrics (1 function, 1 instruction, 1 basic block, 0 calls, 0 memory traffic) match the contract limits exactly.
- Integer signedness, overflow, shifts, and comparisons: PASS. The IR uses `i32` and signed comparisons (`icmp sle`). For `fib(10)`, the maximum value is 55, which fits safely within a 32-bit signed integer without overflow.
- Calls, return values, ABI, stack alignment, and register use: PASS. The final native code uses `%eax` for the i32 return value, complying with the System V x86_64 ABI. The `main` function uses 0 stack bytes and does not modify callee-saved registers.
- Memory safety, lifetime, leaks, and undefined behavior: PASS. The optimized LLVM module has `0` `undef_uses` and `0` `poison_uses`. The raw LLVM memory traffic is safe and completely optimized away. No leaks or UB are present.
- Target compatibility and native instruction validity: PASS. The target triple is `x86_64-pc-linux-gnu`. The disassembly shows valid x86_64 instructions (`movl`, `retq`) and standard ELF64 CRT structures (`_start`, `_init`, `_fini`).
- Native runtime cases and expected observable behavior: PASS. The runtime matrix executed the linked artifact and observed an exit code of 55, matching the expected sidecar value. No stderr or stdout was produced, as expected.
- Configured native limits, required call targets, and loop backedges: PASS. The native optimization budget passed. `main` has 2 instructions, 0 direct calls, and 0 backward branches, matching the configured limits.
- Compiler-generated overhead remaining in optimized LLVM and final native code: PASS. No overhead remains. The optimizer removed all stack traffic, loops, and function calls, yielding a 2-instruction `main` function.

## Blocking findings
None found.

## Non-blocking opportunities
None found. The compiler successfully eliminated all raw LLVM stack traffic and temporary instructions, producing an optimal 2-instruction native `main` function.

## Suggested verification
- Add a runtime matrix case with a larger input (e.g., `fib(46)`) to verify the loop is preserved and executed correctly when it cannot be constant-folded at compile time.
- Add a runtime matrix case with an input of `0` or `1` to explicitly verify the base-case branch of the `fib` function.

<details>
<summary>Raw model response</summary>

```text
OK
## Summary
The Weave compiler toolchain successfully compiles `docs/audit/fibonacci.weave` into a correct, safe, and ABI-valid native executable. The source computes `fib(10)` iteratively, and the expected signed i32 return value is 55. The cleaned WIR accurately preserves the source semantics, including the base case, iterative loop, and variable updates. The raw LLVM IR is valid, well-typed, and correctly translates the WIR semantics into SSA form with stack-allocated local variables. The LLVM optimizer completely constant-folds the program, inlining `fib` into `main`, deleting the invariant loop, and reducing the program to `ret i32 55`. The target assembly and linked executable disassembly confirm this by emitting a minimal `movl $55, %eax; retq` sequence for `main`. The x86_64 System V ABI is respected: the return value is placed in `%eax`, the stack is 16-byte aligned at the call site by the CRT prologue, and no callee-saved registers are touched. The configured runtime matrix executed the exact linked artifact and observed an exit code of 55, matching the expected sidecar value. Both the optimized LLVM contract and the native optimization budget passed without failures, and no compiler-generated overhead remains in the final code.

## Verification matrix
- Source semantics and expected result: PASS. The Weave source defines an iterative `fib` function and calls it with `10`. The expected return value is 55, as stated in the source comments and verified by the runtime matrix.
- Weave-to-WIR semantic preservation: PASS. The cleaned WIR accurately reflects the source: the `le_i32` condition, `let` bindings, `while` loop, `add_i32` arithmetic, and `set` assignments are all preserved.
- WIR-to-raw-LLVM semantic preservation: PASS. The raw LLVM IR uses `alloca` for local variables, `icmp sle` for the signed comparisons, and `add i32` for the arithmetic, matching the WIR operations exactly.
- Raw LLVM validity, SSA, types, and control flow: PASS. The raw LLVM IR is well-formed, uses correct SSA naming for temporaries, and has valid control-flow edges (`br` instructions matching `if` and `while` logic).
- Optimized LLVM semantic preservation: PASS. The optimized LLVM IR reduces `main` to `ret i32 55`, which is semantically equivalent to the source program's constant-folded result.
- Configured optimized LLVM metrics, functions, calls, and memory traffic: PASS. The optimized LLVM budget passed. The observed metrics (1 function, 1 instruction, 1 basic block, 0 calls, 0 memory traffic) match the contract limits exactly.
- Integer signedness, overflow, shifts, and comparisons: PASS. The IR uses `i32` and signed comparisons (`icmp sle`). For `fib(10)`, the maximum value is 55, which fits safely within a 32-bit signed integer without overflow.
- Calls, return values, ABI, stack alignment, and register use: PASS. The final native code uses `%eax` for the i32 return value, complying with the System V x86_64 ABI. The `main` function uses 0 stack bytes and does not modify callee-saved registers.
- Memory safety, lifetime, leaks, and undefined behavior: PASS. The optimized LLVM module has `0` `undef_uses` and `0` `poison_uses`. The raw LLVM memory traffic is safe and completely optimized away. No leaks or UB are present.
- Target compatibility and native instruction validity: PASS. The target triple is `x86_64-pc-linux-gnu`. The disassembly shows valid x86_64 instructions (`movl`, `retq`) and standard ELF64 CRT structures (`_start`, `_init`, `_fini`).
- Native runtime cases and expected observable behavior: PASS. The runtime matrix executed the linked artifact and observed an exit code of 55, matching the expected sidecar value. No stderr or stdout was produced, as expected.
- Configured native limits, required call targets, and loop backedges: PASS. The native optimization budget passed. `main` has 2 instructions, 0 direct calls, and 0 backward branches, matching the configured limits.
- Compiler-generated overhead remaining in optimized LLVM and final native code: PASS. No overhead remains. The optimizer removed all stack traffic, loops, and function calls, yielding a 2-instruction `main` function.

## Blocking findings
None found.

## Non-blocking opportunities
None found. The compiler successfully eliminated all raw LLVM stack traffic and temporary instructions, producing an optimal 2-instruction native `main` function.

## Suggested verification
- Add a runtime matrix case with a larger input (e.g., `fib(46)`) to verify the loop is preserved and executed correctly when it cannot be constant-folded at compile time.
- Add a runtime matrix case with an input of `0` or `1` to explicitly verify the base-case branch of the `fib` function.
```
</details>
