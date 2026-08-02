# Weave Loupe Audit Report

## Verdict

- **Status:** OK
- **Code:** none
- **Reason:** No blocking defect found.

## Reproducibility

- **Report content SHA-256:** `f7e7ecddfa606c61e938dbcb678ac3128f60b5915fb720044ee6e5aead662cea`
- **Audit timestamp (UTC):** `2026-08-02T23:55:28+00:00`
- **Re-audit no later than (UTC):** `2026-09-01T23:55:28+00:00`
- **Maximum audit age:** `30` days
- **Audited input invalidation:** `any source or runtime matrix hash change`
- **Compiler binary invalidation:** `any compiler binary hash change`
- **Auditor invalidation:** `any audit implementation fingerprint change`
- **Model invalidation:** `any configured LLM model or endpoint change`
- **Request limit invalidation:** `any configured LLM max-token change`
- **Development compiler invalidation:** `any compiler version change`
- **Identity attestation upgrade:** `required when command identity becomes available`
- **Audited source Git SHA:** `6ee1ebaceb48ce6fd4fdb3d1c861984effeff9ab`
- **Source tree state:** `clean`
- **Weave Loupe Git SHA:** `6ee1ebaceb48ce6fd4fdb3d1c861984effeff9ab`
- **Auditor content SHA-256:** `4940836c0bf0207782f0ae03414812a330392722719ac9dca136f9702a0dafb7`
- **weavec Git SHA:** `1ba3dc73a459e0f4d9449225060d580953d74e7d`
- **weavec binary SHA-256:** `afdf6f523342bb5484e43a2d9a0006863b7629217da3d97af4aad0c1417563c4`
- **weavec version:** `weavec v0.3.0+git.1ba3dc73a459`
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
- **LLM prompt SHA-256:** `db2647d890ea47ada464f29a6889395bede250d73533db90a3a9f15404a9d9a1`
- **LLM request SHA-256:** `401b44e0c1f219d3230df18b804bba34686bbf38c588d457b83e9c65c88ae208`
- **Provider-reported model:** `z-ai/glm-5.2`
- **Provider response ID:** `chatcmpl-b026205a-2674-4de5-a9a4-a494b148bc60`
- **Provider system fingerprint:** `unavailable`
- **Provider finish reason:** `stop`
- **Provider created (Unix):** `1785714929`
- **Provider prompt tokens:** `27281`
- **Provider completion tokens:** `974`
- **Provider total tokens:** `28255`
- **GitHub run ID:** `30773238493`
- **GitHub workflow SHA:** `e8cf263960854b3f903e8cf8ba0ab5bcf2bfae79`

## Machine and running conditions

- **Operating system:** `Ubuntu 24.04.4 LTS`
- **Kernel:** `Linux 6.17.0-1020-azure`
- **Architecture:** `x86_64`
- **CPU:** `AMD EPYC 9V74 80-Core Processor`
- **Logical CPUs:** `4`
- **Memory:** `16766414848` bytes
- **Python:** `3.12.13`
- **libc:** `glibc 2.39`

## Audited inputs

- Source `docs/audit/fibonacci.weave` — SHA-256 `6cad78b00aaa67b434c4d7a920a3c9065bf7d7a802f5881ef831602e3e48b3d6` — 935 bytes
- Runtime matrix `docs/audit/fibonacci.audit.json` — SHA-256 `4032e56fd1ee0c869bded117fe11d6a7e3d00d3dd7c57edea7991230d7ef6ee6`

## Captured evidence

- `assembly` — SHA-256 `c9ada3f9b21f676366d69be9e0d67e8a8db3786a9e4fd3783f3dbe706b368e97`
- `build_manifest` — SHA-256 `1bf4ce7fea367d7d0c268ca38ce4427182b74ea8f683a7584c1bdbb8c9db7612`
- `diagnostics` — SHA-256 `a40b573053cda943c381742ad672108b1c8985ecc97e2f21dfa604094e31ff63`
- `disassembly` — SHA-256 `3cbd74406c2576b10b521535213c7d2d51e0c4ee5a24e490febfdcf8afc0b94b`
- `executable` — SHA-256 `90a568e286f9d2d5ae1873d965c2364f89a46d071136e1cd18a1914f9e95ef89`
- `llvm` — SHA-256 `3b6560a897280bf0aeec5a4264ad72d5c1e9e88a832c3e687134248a88bd9670`
- `optimization_record` — SHA-256 `3521b76a68875746bebe1b706f3129da67abd93aded7e79ead467f4008c16fa3`
- `optimized_llvm` — SHA-256 `057f82c503f63153db2cd05433300ee212c02b0986729d8497760c3595e18a21`
- `trace` — SHA-256 `973c782fd9436e06f7203fea9af0c26a62e0973bd46db644f14c0bb8e4e4f0c5`
- `wir` — SHA-256 `1dee19643aecdad282706b636fe965940cd06be29860f07d8352286514b354d9`

## Model review coverage and requests

- **Review format:** `weave-loupe-review-plan-v1`
- **Review mode:** `single`
- **Token estimator:** `utf8-byte-upper-bound-v1`
- **Estimated complete review tokens:** `92152`
- **Request count:** `1`
- **Maximum total tokens:** `524288`
- **Maximum request tokens:** `98304`
- **Maximum artifact tokens:** `262144`
- **Artifact-review completion tokens:** `1024`

### Artifact coverage

#### `metadata` — Reproducibility metadata

- Language: `json`
- UTF-8 bytes: `10606`
- Estimated tokens: `10622`
- SHA-256: `8a14dac0e897c14c56dd3cc56d4f99d1cfb844e5af614c7aae5154e3254b47a2`
- Complete coverage: `True`
- Covered ranges: `metadata:[0, 10606)@8a14dac0e897c14c56dd3cc56d4f99d1cfb844e5af614c7aae5154e3254b47a2`

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
- SHA-256: `3b6560a897280bf0aeec5a4264ad72d5c1e9e88a832c3e687134248a88bd9670`
- Complete coverage: `True`
- Covered ranges: `raw_llvm:[0, 3418)@3b6560a897280bf0aeec5a4264ad72d5c1e9e88a832c3e687134248a88bd9670`

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
- UTF-8 bytes: `54710`
- Estimated tokens: `54726`
- SHA-256: `ba44eb6d3124c5b17e9e1b54513b6c57e348187ffb69402c8f9622a85064ad25`
- Complete coverage: `True`
- Covered ranges: `analysis:[0, 54710)@ba44eb6d3124c5b17e9e1b54513b6c57e348187ffb69402c8f9622a85064ad25`

#### `build_manifest` — Compiler build manifest

- Language: `json`
- UTF-8 bytes: `688`
- Estimated tokens: `704`
- SHA-256: `1bf4ce7fea367d7d0c268ca38ce4427182b74ea8f683a7584c1bdbb8c9db7612`
- Complete coverage: `True`
- Covered ranges: `build_manifest:[0, 688)@1bf4ce7fea367d7d0c268ca38ce4427182b74ea8f683a7584c1bdbb8c9db7612`

#### `trace` — Compiler trace

- Language: `json`
- UTF-8 bytes: `205`
- Estimated tokens: `221`
- SHA-256: `973c782fd9436e06f7203fea9af0c26a62e0973bd46db644f14c0bb8e4e4f0c5`
- Complete coverage: `True`
- Covered ranges: `trace:[0, 205)@973c782fd9436e06f7203fea9af0c26a62e0973bd46db644f14c0bb8e4e4f0c5`


### Review requests

#### `single-0001` — single

- Estimated input tokens: `88056`
- Reserved output tokens: `4096`
- Depends on: none
- Covered ranges: `metadata:[0, 10606)@8a14dac0e897c14c56dd3cc56d4f99d1cfb844e5af614c7aae5154e3254b47a2`, `source:[0, 970)@08cc4b43b17a3614d68ae9fe381c7f33aac01c5ddd56b11efe6c79a9d9593dae`, `wir:[0, 670)@725de77fa242cc92db08ca66c30d686c2c1264a3e59555bcf0da5c88347dc34c`, `raw_llvm:[0, 3418)@3b6560a897280bf0aeec5a4264ad72d5c1e9e88a832c3e687134248a88bd9670`, `optimized_llvm:[0, 444)@057f82c503f63153db2cd05433300ee212c02b0986729d8497760c3595e18a21`, `assembly:[0, 390)@c9ada3f9b21f676366d69be9e0d67e8a8db3786a9e4fd3783f3dbe706b368e97`, `disassembly:[0, 5681)@3cbd74406c2576b10b521535213c7d2d51e0c4ee5a24e490febfdcf8afc0b94b`, `optimization_record:[0, 2406)@3521b76a68875746bebe1b706f3129da67abd93aded7e79ead467f4008c16fa3`, `diagnostics:[0, 148)@9683b322333373cb4d9534fef10e27edba462e771e2b03e02108d5c6a7fc71ca`, `analysis:[0, 54710)@ba44eb6d3124c5b17e9e1b54513b6c57e348187ffb69402c8f9622a85064ad25`, `build_manifest:[0, 688)@1bf4ce7fea367d7d0c268ca38ce4427182b74ea8f683a7584c1bdbb8c9db7612`, `trace:[0, 205)@973c782fd9436e06f7203fea9af0c26a62e0973bd46db644f14c0bb8e4e4f0c5`
- Prompt SHA-256: `db2647d890ea47ada464f29a6889395bede250d73533db90a3a9f15404a9d9a1`
- Request SHA-256: `401b44e0c1f219d3230df18b804bba34686bbf38c588d457b83e9c65c88ae208`
- Requested model: `z-ai/glm-5.2`
- Provider model: `z-ai/glm-5.2`
- Provider response ID: `chatcmpl-b026205a-2674-4de5-a9a4-a494b148bc60`
- Finish reason: `stop`
- Provider prompt tokens: `27281`
- Provider completion tokens: `974`
- Provider total tokens: `28255`

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
; source: /tmp/weavec-build-ghw2ur/program.wir
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
        "elapsed_seconds": 0.008977,
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
  "optimization_remarks": {
    "available": true,
    "documents": 8,
    "errors": [],
    "failure_reason": null,
    "format": "weave-loupe-optimization-remarks-v1",
    "records": [
      {
        "arguments": [
          {
            "String": "Loop deleted because it is invariant"
          }
        ],
        "category": "passed",
        "document_index": 0,
        "function": "fib",
        "hotness": null,
        "identity": "0f7a1e9d81c29c3c18f97d211845f993f61fc7a7066d093e32d0e3a4a893a13f",
        "location": null,
        "message": "Loop deleted because it is invariant",
        "name": "Invariant",
        "pass": "loop-delete",
        "unknown_fields": {}
      },
      {
        "arguments": [
          {
            "Pass": "X86 DAG->DAG Instruction Selection"
          },
          {
            "String": ": Function: "
          },
          {
            "Function": "main"
          },
          {
            "String": ": "
          },
          {
            "String": "MI Instruction count changed from "
          },
          {
            "MIInstrsBefore": "0"
          },
          {
            "String": " to "
          },
          {
            "MIInstrsAfter": "3"
          },
          {
            "String": "; Delta: "
          },
          {
            "Delta": "3"
          }
        ],
        "category": "analysis",
        "document_index": 2,
        "function": "main",
        "hotness": null,
        "identity": "144a7eeb25902a90e760ea9774fa4ae6c8bf91936d234933b69c19634ffb6f87",
        "location": null,
        "message": "X86 DAG->DAG Instruction Selection: Function: main: MI Instruction count changed from 0 to 3; Delta: 3",
        "name": "FunctionMISizeChange",
        "pass": "size-info",
        "unknown_fields": {}
      },
      {
        "arguments": [
          {
            "NumInstructions": "2"
          },
          {
            "String": " instructions in function"
          }
        ],
        "category": "analysis",
        "document_index": 7,
        "function": "main",
        "hotness": null,
        "identity": "3f79f87e51c5c82a1addfd499d73d7d6e8c0a0f83e6aefb62e33c72948b2849c",
        "location": null,
        "message": "2 instructions in function",
        "name": "InstructionCount",
        "pass": "asm-printer",
        "unknown_fields": {}
      },
      {
        "arguments": [
          {
            "Pass": "Peephole Optimizations"
          },
          {
            "String": ": Function: "
          },
          {
            "Function": "main"
          },
          {
            "String": ": "
          },
          {
            "String": "MI Instruction count changed from "
          },
          {
            "MIInstrsBefore": "3"
          },
          {
            "String": " to "
          },
          {
            "MIInstrsAfter": "2"
          },
          {
            "String": "; Delta: "
          },
          {
            "Delta": "-1"
          }
        ],
        "category": "analysis",
        "document_index": 3,
        "function": "main",
        "hotness": null,
        "identity": "5c089021e8999b5ed1e6d5f848be5f593cbc99108f496c278a4b233cec596042",
        "location": null,
        "message": "Peephole Optimizations: Function: main: MI Instruction count changed from 3 to 2; Delta: -1",
        "name": "FunctionMISizeChange",
        "pass": "size-info",
        "unknown_fields": {}
      },
      {
        "arguments": [
          {
            "String": "BasicBlock: "
          },
          {
            "BasicBlock": "entry"
          },
          {
            "String": "\n"
          },
          {
            "String": ""
          },
          {
            "String": ": "
          },
          {
            "INST_": "2"
          },
          {
            "String": "\n"
          }
        ],
        "category": "analysis",
        "document_index": 6,
        "function": "main",
        "hotness": null,
        "identity": "82cb05fc5bac5f36aca98ed3b7116d7c2edc13c06c2cd20dc0a909a1e834646e",
        "location": null,
        "message": "BasicBlock: entry\n: 2",
        "name": "InstructionMix",
        "pass": "asm-printer",
        "unknown_fields": {}
      },
      {
        "arguments": [
          {
            "String": "'"
          },
          {
            "Callee": "fib"
          },
          {
            "String": "' inlined into '"
          },
          {
            "Caller": "main"
          },
          {
            "String": "'"
          },
          {
            "String": " with "
          },
          {
            "String": "(cost="
          },
          {
            "Cost": "-15035"
          },
          {
            "String": ", threshold="
          },
          {
            "Threshold": "375"
          },
          {
            "String": ")"
          }
        ],
        "category": "passed",
        "document_index": 1,
        "function": "main",
        "hotness": null,
        "identity": "9dc1cd0090e8ca92b281cbc0b3ad8aa5dd5cb16f8f265e7fd6099cbcc6109e9f",
        "location": null,
        "message": "'fib' inlined into 'main' with (cost=-15035, threshold=375)",
        "name": "Inlined",
        "pass": "inline",
        "unknown_fields": {}
      },
      {
        "arguments": [
          {
            "String": "\nFunction: main"
          }
        ],
        "category": "analysis",
        "document_index": 5,
        "function": "main",
        "hotness": null,
        "identity": "ab4d8fbbd9ee00b68e61816224cee2bbfa39a61ef97f4b4e20f36c9b6d79daf5",
        "location": null,
        "message": "Function: main",
        "name": "StackLayout",
        "pass": "stack-frame-layout",
        "unknown_fields": {}
      },
      {
        "arguments": [
          {
            "NumStackBytes": "0"
          },
          {
            "String": " stack bytes in function '"
          },
          {
            "Function": "main"
          },
          {
            "String": "'"
          }
        ],
        "category": "analysis",
        "document_index": 4,
        "function": "main",
        "hotness": null,
        "identity": "ebf87dc240e17cac7f0d396a3eff3faf5b9933688f583278d19cff57c8a601b5",
        "location": null,
        "message": "0 stack bytes in function 'main'",
        "name": "StackSize",
        "pass": "prologepilog",
        "unknown_fields": {}
      }
    ],
    "summary": {
      "by_category": {
        "analysis": 6,
        "passed": 2
      },
      "by_function": {
        "fib": 1,
        "main": 7
      },
      "by_pass": {
        "asm-printer": 2,
        "inline": 1,
        "loop-delete": 1,
        "prologepilog": 1,
        "size-info": 2,
        "stack-frame-layout": 1
      },
      "by_pass_and_category": {
        "asm-printer": {
          "analysis": 2
        },
        "inline": {
          "passed": 1
        },
        "loop-delete": {
          "passed": 1
        },
        "prologepilog": {
          "analysis": 1
        },
        "size-info": {
          "analysis": 2
        },
        "stack-frame-layout": {
          "analysis": 1
        }
      },
      "highest_value_missed": [],
      "total": 8
    },
    "valid": true
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
          "elapsed_seconds": 0.008977,
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
  },
  "wir": {
    "anonymous_identifiers": [],
    "available": true,
    "call_graph": {
      "fib": [],
      "main": [
        "fib"
      ]
    },
    "core_version": 2,
    "cross_stage": {
      "duplicate_llvm_declarations": [],
      "duplicate_llvm_definitions": [],
      "functions": {
        "fib": {
          "block_delta": -1,
          "llvm_blocks": 6,
          "wir_blocks": 7
        },
        "main": {
          "block_delta": 0,
          "llvm_blocks": 1,
          "wir_blocks": 1
        }
      },
      "llvm_declarations": [],
      "llvm_definitions": [
        "fib",
        "main"
      ],
      "metrics": {
        "duplicate_llvm_declarations": 0,
        "duplicate_llvm_definitions": 0,
        "missing_definitions": 0,
        "missing_externs": 0,
        "unexpected_definitions": 0
      },
      "missing_definitions": [],
      "missing_externs": [],
      "unexpected_definitions": [],
      "wir_externs": [],
      "wir_functions": [
        "fib",
        "main"
      ]
    },
    "declarations": [
      {
        "kind": "fn",
        "name": "fib",
        "params": [
          {
            "name": "n",
            "type": "i32"
          }
        ],
        "returns": [
          "i32"
        ]
      },
      {
        "kind": "fn",
        "name": "main",
        "params": [],
        "returns": [
          "i32"
        ]
      }
    ],
    "duplicate_declarations": [],
    "failure_reason": null,
    "format": "weave-loupe-wir-analysis-v1",
    "functions": {
      "fib": {
        "anonymous_identifiers": [],
        "blocks": [
          {
            "id": "b0",
            "instructions": 3,
            "opcodes": [
              "if",
              "le_i32",
              "const_i32"
            ],
            "reachable": true,
            "role": "entry"
          },
          {
            "id": "b1",
            "instructions": 1,
            "opcodes": [
              "return"
            ],
            "reachable": true,
            "role": "if-then"
          },
          {
            "id": "b2",
            "instructions": 0,
            "opcodes": [],
            "reachable": true,
            "role": "if-else"
          },
          {
            "id": "b3",
            "instructions": 6,
            "opcodes": [
              "let",
              "const_i32",
              "let",
              "const_i32",
              "let",
              "const_i32"
            ],
            "reachable": true,
            "role": "if-merge"
          },
          {
            "id": "b4",
            "instructions": 2,
            "opcodes": [
              "while",
              "le_i32"
            ],
            "reachable": true,
            "role": "while-condition"
          },
          {
            "id": "b5",
            "instructions": 7,
            "opcodes": [
              "let",
              "add_i32",
              "set",
              "set",
              "set",
              "add_i32",
              "const_i32"
            ],
            "reachable": true,
            "role": "while-body"
          },
          {
            "id": "b6",
            "instructions": 1,
            "opcodes": [
              "return"
            ],
            "reachable": true,
            "role": "while-exit"
          }
        ],
        "calls": [],
        "duplicate_locals": [],
        "edges": [
          {
            "kind": "if-true",
            "source": "b0",
            "target": "b1"
          },
          {
            "kind": "if-false",
            "source": "b0",
            "target": "b2"
          },
          {
            "kind": "fallthrough",
            "source": "b2",
            "target": "b3"
          },
          {
            "kind": "fallthrough",
            "source": "b3",
            "target": "b4"
          },
          {
            "kind": "while-true",
            "source": "b4",
            "target": "b5"
          },
          {
            "kind": "while-false",
            "source": "b4",
            "target": "b6"
          },
          {
            "kind": "backedge",
            "source": "b5",
            "target": "b4"
          }
        ],
        "locals": [
          "current",
          "index",
          "next",
          "previous"
        ],
        "metrics": {
          "backedges": 1,
          "blocks": 7,
          "branches": 2,
          "calls": 0,
          "control_flow_edges": 7,
          "instructions": 20,
          "locals": 4,
          "loops": 1,
          "operands": 38,
          "reachable_blocks": 7,
          "returns": 2,
          "unreachable_blocks": 0,
          "unreachable_instructions": 0
        },
        "opcodes": {
          "add_i32": 2,
          "const_i32": 5,
          "if": 1,
          "le_i32": 2,
          "let": 4,
          "return": 2,
          "set": 3,
          "while": 1
        },
        "params": [
          {
            "name": "n",
            "type": "i32"
          }
        ],
        "provenance": {
          "mapped_instructions": 20,
          "spans": [
            {
              "end_byte": 833,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
              "start_byte": 252
            },
            {
              "end_byte": 259,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
              "start_byte": 256
            },
            {
              "end_byte": 280,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
              "start_byte": 264
            },
            {
              "end_byte": 271,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
              "start_byte": 265
            },
            {
              "end_byte": 279,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
              "start_byte": 272
            },
            {
              "end_byte": 274,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
              "start_byte": 273
            },
            {
              "end_byte": 278,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
              "start_byte": 275
            },
            {
              "end_byte": 298,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
              "start_byte": 285
            },
            {
              "end_byte": 293,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
              "start_byte": 286
            },
            {
              "end_byte": 297,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
              "start_byte": 294
            },
            {
              "end_byte": 832,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
              "start_byte": 303
            },
            {
              "end_byte": 455,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
              "start_byte": 313
            },
            {
              "end_byte": 316,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
              "start_byte": 314
            },
            {
              "end_byte": 371,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
              "start_byte": 325
            },
            {
              "end_byte": 335,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
              "start_byte": 326
            },
            {
              "end_byte": 370,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
              "start_byte": 346
            },
            {
              "end_byte": 353,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
              "start_byte": 347
            },
            {
              "end_byte": 355,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
              "start_byte": 354
            },
            {
              "end_byte": 369,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
              "start_byte": 356
            },
            {
              "end_byte": 366,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
              "start_byte": 357
            },
            {
              "end_byte": 368,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
              "start_byte": 367
            },
            {
              "end_byte": 424,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
              "start_byte": 380
            },
            {
              "end_byte": 385,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
              "start_byte": 381
            },
            {
              "end_byte": 423,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
              "start_byte": 396
            },
            {
              "end_byte": 422,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
              "start_byte": 412
            },
            {
              "end_byte": 421,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
              "start_byte": 420
            },
            {
              "end_byte": 454,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
              "start_byte": 433
            },
            {
              "end_byte": 438,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
              "start_byte": 434
            },
            {
              "end_byte": 453,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
              "start_byte": 449
            },
            {
              "end_byte": 494,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
              "start_byte": 462
            },
            {
              "end_byte": 475,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
              "start_byte": 467
            },
            {
              "end_byte": 493,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
              "start_byte": 480
            }
          ]
        },
        "returns": [
          "i32"
        ],
        "types": {
          "i32": 15
        },
        "unresolved_symbols": []
      },
      "main": {
        "anonymous_identifiers": [],
        "blocks": [
          {
            "id": "b0",
            "instructions": 3,
            "opcodes": [
              "return",
              "call_i32",
              "const_i32"
            ],
            "reachable": true,
            "role": "entry"
          }
        ],
        "calls": [
          "fib"
        ],
        "duplicate_locals": [],
        "edges": [],
        "locals": [],
        "metrics": {
          "backedges": 0,
          "blocks": 1,
          "branches": 0,
          "calls": 1,
          "control_flow_edges": 0,
          "instructions": 3,
          "locals": 0,
          "loops": 0,
          "operands": 4,
          "reachable_blocks": 1,
          "returns": 1,
          "unreachable_blocks": 0,
          "unreachable_instructions": 0
        },
        "opcodes": {
          "call_i32": 1,
          "const_i32": 1,
          "return": 1
        },
        "params": [],
        "provenance": {
          "mapped_instructions": 3,
          "spans": [
            {
              "end_byte": 490,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
              "start_byte": 481
            },
            {
              "end_byte": 492,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
              "start_byte": 491
            },
            {
              "end_byte": 532,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
              "start_byte": 501
            },
            {
              "end_byte": 513,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
              "start_byte": 506
            },
            {
              "end_byte": 531,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
              "start_byte": 518
            },
            {
              "end_byte": 528,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
              "start_byte": 519
            },
            {
              "end_byte": 530,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
              "start_byte": 529
            }
          ]
        },
        "returns": [
          "i32"
        ],
        "types": {
          "i32": 3
        },
        "unresolved_symbols": []
      }
    },
    "metrics": {
      "anonymous_identifiers": 0,
      "backedges": 1,
      "blocks": 8,
      "branches": 2,
      "calls": 1,
      "control_flow_edges": 7,
      "declarations": 2,
      "duplicate_declarations": 0,
      "externs": 0,
      "functions": 2,
      "instructions": 23,
      "locals": 4,
      "loops": 1,
      "malformed_provenance": 48,
      "mapped_functions": 2,
      "mapped_instructions": 23,
      "operands": 42,
      "provenance_files": 1,
      "provenance_spans": 87,
      "reachable_blocks": 8,
      "returns": 3,
      "unknown_declarations": 0,
      "unreachable_blocks": 0,
      "unresolved_symbols": 0
    },
    "opcodes": {
      "add_i32": 2,
      "call_i32": 1,
      "const_i32": 6,
      "if": 1,
      "le_i32": 2,
      "let": 4,
      "return": 3,
      "set": 3,
      "while": 1
    },
    "provenance": {
      "files": [
        {
          "index": 0,
          "path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave"
        }
      ],
      "malformed": [
        "span 539..568: no following WIR form",
        "span 544..549: no following WIR form",
        "span 554..567: no following WIR form",
        "span 555..564: no following WIR form",
        "span 565..566: no following WIR form",
        "span 575..808: no following WIR form",
        "span 576..581: no following WIR form",
        "span 590..628: no following WIR form",
        "span 591..600: no following WIR form",
        "span 611..627: no following WIR form",
        "span 612..618: no following WIR form",
        "span 619..624: no following WIR form",
        "span 625..626: no following WIR form",
        "span 637..807: no following WIR form",
        "span 651..692: no following WIR form",
        "span 656..660: no following WIR form",
        "span 665..691: no following WIR form",
        "span 666..673: no following WIR form",
        "span 674..682: no following WIR form",
        "span 683..690: no following WIR form",
        "span 703..725: no following WIR form",
        "span 717..724: no following WIR form",
        "span 736..754: no following WIR form",
        "span 749..753: no following WIR form",
        "span 765..806: no following WIR form",
        "span 776..805: no following WIR form",
        "span 777..784: no following WIR form",
        "span 785..790: no following WIR form",
        "span 791..804: no following WIR form",
        "span 792..801: no following WIR form",
        "span 802..803: no following WIR form",
        "span 815..831: no following WIR form",
        "span 823..830: no following WIR form",
        "span 836..933: no following WIR form",
        "span 843..847: no following WIR form",
        "span 852..860: no following WIR form",
        "span 853..859: no following WIR form",
        "span 865..878: no following WIR form",
        "span 866..873: no following WIR form",
        "span 874..877: no following WIR form",
        "span 883..932: no following WIR form",
        "span 893..931: no following WIR form",
        "span 901..930: no following WIR form",
        "span 902..910: no following WIR form",
        "span 911..914: no following WIR form",
        "span 915..929: no following WIR form",
        "span 916..925: no following WIR form",
        "span 926..928: no following WIR form"
      ],
      "spans": [
        {
          "end_byte": 833,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 252
        },
        {
          "end_byte": 259,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 256
        },
        {
          "end_byte": 280,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 264
        },
        {
          "end_byte": 271,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 265
        },
        {
          "end_byte": 279,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 272
        },
        {
          "end_byte": 274,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 273
        },
        {
          "end_byte": 278,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 275
        },
        {
          "end_byte": 298,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 285
        },
        {
          "end_byte": 293,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 286
        },
        {
          "end_byte": 297,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 294
        },
        {
          "end_byte": 832,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 303
        },
        {
          "end_byte": 455,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 313
        },
        {
          "end_byte": 316,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 314
        },
        {
          "end_byte": 371,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 325
        },
        {
          "end_byte": 335,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 326
        },
        {
          "end_byte": 370,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 346
        },
        {
          "end_byte": 353,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 347
        },
        {
          "end_byte": 355,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 354
        },
        {
          "end_byte": 369,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 356
        },
        {
          "end_byte": 366,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 357
        },
        {
          "end_byte": 368,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 367
        },
        {
          "end_byte": 424,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 380
        },
        {
          "end_byte": 385,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 381
        },
        {
          "end_byte": 423,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 396
        },
        {
          "end_byte": 422,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 412
        },
        {
          "end_byte": 421,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 420
        },
        {
          "end_byte": 454,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 433
        },
        {
          "end_byte": 438,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 434
        },
        {
          "end_byte": 453,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 449
        },
        {
          "end_byte": 494,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 462
        },
        {
          "end_byte": 475,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 467
        },
        {
          "end_byte": 493,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 480
        },
        {
          "end_byte": 490,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 481
        },
        {
          "end_byte": 492,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 491
        },
        {
          "end_byte": 532,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 501
        },
        {
          "end_byte": 513,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 506
        },
        {
          "end_byte": 531,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 518
        },
        {
          "end_byte": 528,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 519
        },
        {
          "end_byte": 530,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 529
        },
        {
          "end_byte": 568,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 539
        },
        {
          "end_byte": 549,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 544
        },
        {
          "end_byte": 567,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 554
        },
        {
          "end_byte": 564,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 555
        },
        {
          "end_byte": 566,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 565
        },
        {
          "end_byte": 808,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 575
        },
        {
          "end_byte": 581,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 576
        },
        {
          "end_byte": 628,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 590
        },
        {
          "end_byte": 600,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 591
        },
        {
          "end_byte": 627,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 611
        },
        {
          "end_byte": 618,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 612
        },
        {
          "end_byte": 624,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 619
        },
        {
          "end_byte": 626,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 625
        },
        {
          "end_byte": 807,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 637
        },
        {
          "end_byte": 692,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 651
        },
        {
          "end_byte": 660,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 656
        },
        {
          "end_byte": 691,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 665
        },
        {
          "end_byte": 673,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 666
        },
        {
          "end_byte": 682,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 674
        },
        {
          "end_byte": 690,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 683
        },
        {
          "end_byte": 725,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 703
        },
        {
          "end_byte": 724,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 717
        },
        {
          "end_byte": 754,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 736
        },
        {
          "end_byte": 753,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 749
        },
        {
          "end_byte": 806,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 765
        },
        {
          "end_byte": 805,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 776
        },
        {
          "end_byte": 784,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 777
        },
        {
          "end_byte": 790,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 785
        },
        {
          "end_byte": 804,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 791
        },
        {
          "end_byte": 801,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 792
        },
        {
          "end_byte": 803,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 802
        },
        {
          "end_byte": 831,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 815
        },
        {
          "end_byte": 830,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 823
        },
        {
          "end_byte": 933,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 836
        },
        {
          "end_byte": 847,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 843
        },
        {
          "end_byte": 860,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 852
        },
        {
          "end_byte": 859,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 853
        },
        {
          "end_byte": 878,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 865
        },
        {
          "end_byte": 873,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 866
        },
        {
          "end_byte": 877,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 874
        },
        {
          "end_byte": 932,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 883
        },
        {
          "end_byte": 931,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 893
        },
        {
          "end_byte": 930,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 901
        },
        {
          "end_byte": 910,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 902
        },
        {
          "end_byte": 914,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 911
        },
        {
          "end_byte": 929,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 915
        },
        {
          "end_byte": 925,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 916
        },
        {
          "end_byte": 928,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave",
          "start_byte": 926
        }
      ]
    },
    "types": {
      "i32": 18
    },
    "unresolved_symbols": [],
    "valid": true
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
  "output": "/tmp/loupe-audit-2c34w3t7/.audit.loupe.p963llj2/artifacts/program",
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
The final native program is correct, safe, ABI-valid, target-compatible, and free from avoidable compiler-generated overhead. The Weave source computes `fib(10)` iteratively and returns `55`. The WIR and raw LLVM IR preserve this semantics, using signed `i32` comparisons and arithmetic. The LLVM optimizer successfully inlines `fib` into `main` and constant-folds the iterative loop, reducing the optimized LLVM IR to a single `ret i32 55`. The target assembly and linked executable disassembly confirm this, yielding a minimal `movl $55, %eax; retq` sequence for `main`. The runtime matrix verifies that the exact linked artifact exits with code `55`, matching the expected value. All configured optimized LLVM and native optimization budgets pass without violations.

## Verification matrix
- Source semantics and expected result: PASS. The Weave source (`docs/audit/fibonacci.weave`) defines an iterative `fib(10)` with an expected return value of `55`. The runtime matrix confirms the executable exits with code `55`.
- Weave-to-WIR semantic preservation: PASS. The WIR projection matches the source structure, preserving the `fib` function, the `le_i32` base case, the iterative `while` loop, and the `main` entry point calling `fib` with `const_i32 10`.
- WIR-to-raw-LLVM semantic preservation: PASS. The raw LLVM IR implements the WIR structure using `icmp sle` for the `le_i32` conditions, `add i32` for arithmetic, and standard `alloca`/`load`/`store` for the mutable local variables.
- Raw LLVM validity, SSA, types, and control flow: PASS. The raw LLVM IR is well-formed, uses valid SSA values, correct `i32` types, and valid control-flow edges (`br`, `ret`) with no `undef` or `poison` uses.
- Optimized LLVM semantic preservation: PASS. The optimized LLVM IR reduces the entire program to `define noundef i32 @main() { entry: ret i32 55 }`, which is semantically equivalent to evaluating `fib(10)`.
- Configured optimized LLVM metrics, functions, calls, and memory traffic: PASS. The `optimized_llvm_budget` in the analysis JSON shows 1 function (`main`), 1 instruction (`ret`), 0 calls, 0 memory traffic, and 0 poison/undef uses, all within configured limits.
- Integer signedness, overflow, shifts, and comparisons: PASS. The source uses `i32` with `le_i32` (signed less-than-or-equal), correctly lowered to `icmp sle`. `fib(10)` does not overflow `i32`.
- Calls, return values, ABI, stack alignment, and register use: PASS. The final `main` uses `movl $55, %eax; retq`, correctly placing the `i32` return value in `%eax` per the System V x86_64 ABI. Stack size is 0 bytes.
- Memory safety, lifetime, leaks, and undefined behavior: PASS. The optimized LLVM IR has `memory(none)` and `willreturn` attributes, with no allocations or loads. The raw LLVM IR uses valid stack allocations that are completely optimized away.
- Target compatibility and native instruction validity: PASS. The build manifest targets `x86_64-unknown-linux-gnu`. The disassembly shows valid x86_64 instructions.
- Native runtime cases and expected observable behavior: PASS. The runtime matrix executed the linked artifact and observed `exit_code: 55`, matching the expected value.
- Configured native limits, required call targets, and loop backedges: PASS. The `native_budget` shows `main` has 2 instructions, 0 direct calls, and 0 backward branches, meeting all maximum limits.
- Compiler-generated overhead remaining in optimized LLVM and final native code: PASS. No overhead remains. The optimized IR is a single `ret`, and the native code is a 2-instruction `mov`/`ret` pair.

## Blocking findings
None found.

## Non-blocking opportunities
None found. The compiler successfully eliminated all raw LLVM stack traffic and temporary instructions, achieving optimal final code.

## Suggested verification
- Additional runtime cases with varying `n` values (e.g., 0, 1, 20) would increase confidence in the `fib` implementation if the optimizer were less aggressive, though constant-folding makes this redundant for the final artifact.
- Testing with a non-constant input to `fib` would verify the iterative loop's native code generation, which is fully optimized away in this corpus.

<details>
<summary>Raw model response</summary>

```text
OK
## Summary
The final native program is correct, safe, ABI-valid, target-compatible, and free from avoidable compiler-generated overhead. The Weave source computes `fib(10)` iteratively and returns `55`. The WIR and raw LLVM IR preserve this semantics, using signed `i32` comparisons and arithmetic. The LLVM optimizer successfully inlines `fib` into `main` and constant-folds the iterative loop, reducing the optimized LLVM IR to a single `ret i32 55`. The target assembly and linked executable disassembly confirm this, yielding a minimal `movl $55, %eax; retq` sequence for `main`. The runtime matrix verifies that the exact linked artifact exits with code `55`, matching the expected value. All configured optimized LLVM and native optimization budgets pass without violations.

## Verification matrix
- Source semantics and expected result: PASS. The Weave source (`docs/audit/fibonacci.weave`) defines an iterative `fib(10)` with an expected return value of `55`. The runtime matrix confirms the executable exits with code `55`.
- Weave-to-WIR semantic preservation: PASS. The WIR projection matches the source structure, preserving the `fib` function, the `le_i32` base case, the iterative `while` loop, and the `main` entry point calling `fib` with `const_i32 10`.
- WIR-to-raw-LLVM semantic preservation: PASS. The raw LLVM IR implements the WIR structure using `icmp sle` for the `le_i32` conditions, `add i32` for arithmetic, and standard `alloca`/`load`/`store` for the mutable local variables.
- Raw LLVM validity, SSA, types, and control flow: PASS. The raw LLVM IR is well-formed, uses valid SSA values, correct `i32` types, and valid control-flow edges (`br`, `ret`) with no `undef` or `poison` uses.
- Optimized LLVM semantic preservation: PASS. The optimized LLVM IR reduces the entire program to `define noundef i32 @main() { entry: ret i32 55 }`, which is semantically equivalent to evaluating `fib(10)`.
- Configured optimized LLVM metrics, functions, calls, and memory traffic: PASS. The `optimized_llvm_budget` in the analysis JSON shows 1 function (`main`), 1 instruction (`ret`), 0 calls, 0 memory traffic, and 0 poison/undef uses, all within configured limits.
- Integer signedness, overflow, shifts, and comparisons: PASS. The source uses `i32` with `le_i32` (signed less-than-or-equal), correctly lowered to `icmp sle`. `fib(10)` does not overflow `i32`.
- Calls, return values, ABI, stack alignment, and register use: PASS. The final `main` uses `movl $55, %eax; retq`, correctly placing the `i32` return value in `%eax` per the System V x86_64 ABI. Stack size is 0 bytes.
- Memory safety, lifetime, leaks, and undefined behavior: PASS. The optimized LLVM IR has `memory(none)` and `willreturn` attributes, with no allocations or loads. The raw LLVM IR uses valid stack allocations that are completely optimized away.
- Target compatibility and native instruction validity: PASS. The build manifest targets `x86_64-unknown-linux-gnu`. The disassembly shows valid x86_64 instructions.
- Native runtime cases and expected observable behavior: PASS. The runtime matrix executed the linked artifact and observed `exit_code: 55`, matching the expected value.
- Configured native limits, required call targets, and loop backedges: PASS. The `native_budget` shows `main` has 2 instructions, 0 direct calls, and 0 backward branches, meeting all maximum limits.
- Compiler-generated overhead remaining in optimized LLVM and final native code: PASS. No overhead remains. The optimized IR is a single `ret`, and the native code is a 2-instruction `mov`/`ret` pair.

## Blocking findings
None found.

## Non-blocking opportunities
None found. The compiler successfully eliminated all raw LLVM stack traffic and temporary instructions, achieving optimal final code.

## Suggested verification
- Additional runtime cases with varying `n` values (e.g., 0, 1, 20) would increase confidence in the `fib` implementation if the optimizer were less aggressive, though constant-folding makes this redundant for the final artifact.
- Testing with a non-constant input to `fib` would verify the iterative loop's native code generation, which is fully optimized away in this corpus.
```
</details>
