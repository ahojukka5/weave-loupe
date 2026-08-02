# Weave Loupe Audit Report

## Verdict

- **Status:** OK
- **Code:** none
- **Reason:** No blocking defect found.

## Reproducibility

- **Report content SHA-256:** `ed9d22d7862f68a9550781bef7583dcdf8313b388046919cb6b6ae802cba49da`
- **Audit timestamp (UTC):** `2026-08-02T06:17:57+00:00`
- **Re-audit no later than (UTC):** `2026-09-01T06:17:57+00:00`
- **Maximum audit age:** `30` days
- **Audited input invalidation:** `any source or runtime matrix hash change`
- **Compiler binary invalidation:** `any compiler binary hash change`
- **Auditor invalidation:** `any audit implementation fingerprint change`
- **Model invalidation:** `any configured LLM model or endpoint change`
- **Request limit invalidation:** `any configured LLM max-token change`
- **Development compiler invalidation:** `any compiler version change`
- **Identity attestation upgrade:** `required when command identity becomes available`
- **Audited source Git SHA:** `58e1ff007e8fd543650858db26400378c1d9877c`
- **Source tree state:** `clean`
- **Weave Loupe Git SHA:** `58e1ff007e8fd543650858db26400378c1d9877c`
- **Auditor content SHA-256:** `feb6f4b141181eeb0982aa71215cd4a860bd581043365fd1da9ee6d64a54afe6`
- **weavec Git SHA:** `ccf2ac6a3b22cf88461793ea6c4f64287cfc743c`
- **weavec binary SHA-256:** `950e57c792ac4a98da89ca5049719ef964a39870ef384cb20a4e8027aaf3c870`
- **weavec version:** `weavec v0.3.0+git.ccf2ac6a3b22`
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
- **LLM prompt SHA-256:** `8eb1066c8c52000e932a36fef83f073796656dc0751d2ab98b3ad336e6fb355b`
- **LLM request SHA-256:** `d6ee047018d38f9667270956d3b9fa07842682340aeb1cabd38c7c92cb9106c2`
- **Provider-reported model:** `z-ai/glm-5.2`
- **Provider response ID:** `chatcmpl-34f7f23c-138f-4b42-bbb9-cbedec72c003`
- **Provider system fingerprint:** `unavailable`
- **Provider finish reason:** `stop`
- **Provider created (Unix):** `1785651479`
- **Provider prompt tokens:** `14587`
- **Provider completion tokens:** `886`
- **Provider total tokens:** `15473`
- **GitHub run ID:** `30735421228`
- **GitHub workflow SHA:** `58e1ff007e8fd543650858db26400378c1d9877c`

## Machine and running conditions

- **Operating system:** `Ubuntu 24.04.4 LTS`
- **Kernel:** `Linux 6.17.0-1020-azure`
- **Architecture:** `x86_64`
- **CPU:** `AMD EPYC 7763 64-Core Processor`
- **Logical CPUs:** `4`
- **Memory:** `16766418944` bytes
- **Python:** `3.12.13`
- **libc:** `glibc 2.39`

## Audited inputs

- Source `/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave` — SHA-256 `6cad78b00aaa67b434c4d7a920a3c9065bf7d7a802f5881ef831602e3e48b3d6` — 935 bytes
- Runtime matrix `/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.audit.json` — SHA-256 `4032e56fd1ee0c869bded117fe11d6a7e3d00d3dd7c57edea7991230d7ef6ee6`

## Captured evidence

- `assembly` — SHA-256 `c9ada3f9b21f676366d69be9e0d67e8a8db3786a9e4fd3783f3dbe706b368e97`
- `build_manifest` — SHA-256 `a34af8ef363ea87914bf6b17793ac4228a1c38479a1e8220c1c3b9483c888144`
- `diagnostics` — SHA-256 `a40b573053cda943c381742ad672108b1c8985ecc97e2f21dfa604094e31ff63`
- `disassembly` — SHA-256 `3cbd74406c2576b10b521535213c7d2d51e0c4ee5a24e490febfdcf8afc0b94b`
- `executable` — SHA-256 `90a568e286f9d2d5ae1873d965c2364f89a46d071136e1cd18a1914f9e95ef89`
- `llvm` — SHA-256 `dbd6f8240640856cde856177d4c1228bf16c72c11c2aa2279569227429935ddf`
- `optimization_record` — SHA-256 `3521b76a68875746bebe1b706f3129da67abd93aded7e79ead467f4008c16fa3`
- `optimized_llvm` — SHA-256 `057f82c503f63153db2cd05433300ee212c02b0986729d8497760c3595e18a21`
- `trace` — SHA-256 `973c782fd9436e06f7203fea9af0c26a62e0973bd46db644f14c0bb8e4e4f0c5`
- `wir` — SHA-256 `1dee19643aecdad282706b636fe965940cd06be29860f07d8352286514b354d9`

## Model review coverage and requests

- **Review format:** `weave-loupe-review-plan-v1`
- **Review mode:** `single`
- **Token estimator:** `utf8-byte-upper-bound-v1`
- **Estimated complete review tokens:** `47368`
- **Request count:** `1`
- **Maximum total tokens:** `524288`
- **Maximum request tokens:** `98304`
- **Maximum artifact tokens:** `262144`
- **Artifact-review completion tokens:** `512`

### Artifact coverage

#### `metadata` — Reproducibility metadata

- Language: `json`
- UTF-8 bytes: `9267`
- Estimated tokens: `9283`
- SHA-256: `5b7b2454d41ff246241b02fc6c15d212a0aaad6df884a6982972e2a82223ee25`
- Complete coverage: `True`
- Covered ranges: `metadata:[0, 9267)@5b7b2454d41ff246241b02fc6c15d212a0aaad6df884a6982972e2a82223ee25`

#### `source` — Weave source

- Language: `lisp`
- UTF-8 bytes: `1012`
- Estimated tokens: `1028`
- SHA-256: `41cd5a472a0b1465554484040ebce72df9dd6abb7323c19d7436d8bd0649b9fa`
- Complete coverage: `True`
- Covered ranges: `source:[0, 1012)@41cd5a472a0b1465554484040ebce72df9dd6abb7323c19d7436d8bd0649b9fa`

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
- SHA-256: `dbd6f8240640856cde856177d4c1228bf16c72c11c2aa2279569227429935ddf`
- Complete coverage: `True`
- Covered ranges: `raw_llvm:[0, 3418)@dbd6f8240640856cde856177d4c1228bf16c72c11c2aa2279569227429935ddf`

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
- UTF-8 bytes: `11181`
- Estimated tokens: `11197`
- SHA-256: `dbdd9e722af6fceb767852b5f3d76ef2d3dd2c8aef2235994e9904a024170117`
- Complete coverage: `True`
- Covered ranges: `analysis:[0, 11181)@dbdd9e722af6fceb767852b5f3d76ef2d3dd2c8aef2235994e9904a024170117`

#### `build_manifest` — Compiler build manifest

- Language: `json`
- UTF-8 bytes: `688`
- Estimated tokens: `704`
- SHA-256: `a34af8ef363ea87914bf6b17793ac4228a1c38479a1e8220c1c3b9483c888144`
- Complete coverage: `True`
- Covered ranges: `build_manifest:[0, 688)@a34af8ef363ea87914bf6b17793ac4228a1c38479a1e8220c1c3b9483c888144`

#### `trace` — Compiler trace

- Language: `json`
- UTF-8 bytes: `205`
- Estimated tokens: `221`
- SHA-256: `973c782fd9436e06f7203fea9af0c26a62e0973bd46db644f14c0bb8e4e4f0c5`
- Complete coverage: `True`
- Covered ranges: `trace:[0, 205)@973c782fd9436e06f7203fea9af0c26a62e0973bd46db644f14c0bb8e4e4f0c5`


### Review requests

#### `single-0001` — single

- Estimated input tokens: `43272`
- Reserved output tokens: `4096`
- Depends on: none
- Covered ranges: `metadata:[0, 9267)@5b7b2454d41ff246241b02fc6c15d212a0aaad6df884a6982972e2a82223ee25`, `source:[0, 1012)@41cd5a472a0b1465554484040ebce72df9dd6abb7323c19d7436d8bd0649b9fa`, `wir:[0, 670)@725de77fa242cc92db08ca66c30d686c2c1264a3e59555bcf0da5c88347dc34c`, `raw_llvm:[0, 3418)@dbd6f8240640856cde856177d4c1228bf16c72c11c2aa2279569227429935ddf`, `optimized_llvm:[0, 444)@057f82c503f63153db2cd05433300ee212c02b0986729d8497760c3595e18a21`, `assembly:[0, 390)@c9ada3f9b21f676366d69be9e0d67e8a8db3786a9e4fd3783f3dbe706b368e97`, `disassembly:[0, 5681)@3cbd74406c2576b10b521535213c7d2d51e0c4ee5a24e490febfdcf8afc0b94b`, `optimization_record:[0, 2406)@3521b76a68875746bebe1b706f3129da67abd93aded7e79ead467f4008c16fa3`, `diagnostics:[0, 148)@9683b322333373cb4d9534fef10e27edba462e771e2b03e02108d5c6a7fc71ca`, `analysis:[0, 11181)@dbdd9e722af6fceb767852b5f3d76ef2d3dd2c8aef2235994e9904a024170117`, `build_manifest:[0, 688)@a34af8ef363ea87914bf6b17793ac4228a1c38479a1e8220c1c3b9483c888144`, `trace:[0, 205)@973c782fd9436e06f7203fea9af0c26a62e0973bd46db644f14c0bb8e4e4f0c5`
- Prompt SHA-256: `8eb1066c8c52000e932a36fef83f073796656dc0751d2ab98b3ad336e6fb355b`
- Request SHA-256: `d6ee047018d38f9667270956d3b9fa07842682340aeb1cabd38c7c92cb9106c2`
- Requested model: `z-ai/glm-5.2`
- Provider model: `z-ai/glm-5.2`
- Provider response ID: `chatcmpl-34f7f23c-138f-4b42-bbb9-cbedec72c003`
- Finish reason: `stop`
- Provider prompt tokens: `14587`
- Provider completion tokens: `886`
- Provider total tokens: `15473`

## Complete compiler evidence

This section contains the exact evidence reviewed by the model so that the
source-to-native lowering can also be inspected manually.

### Weave source

```lisp
--- /home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave ---
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
; source: /tmp/weavec-build-Vd0nFy/program.wir
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
  "sidecar": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.audit.json",
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
  "sidecar": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.audit.json",
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
        "elapsed_seconds": 0.01109,
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
  "sidecar": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.audit.json",
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
    "sidecar": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.audit.json",
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
    "sidecar": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.audit.json",
    "sidecar_sha256": "4032e56fd1ee0c869bded117fe11d6a7e3d00d3dd7c57edea7991230d7ef6ee6"
  },
  "runtime": {
    "case_count": 1,
    "cases": [
      {
        "actual": {
          "elapsed_seconds": 0.01109,
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
    "sidecar": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.audit.json",
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
  "output": "/tmp/loupe-audit-jgd3x7e_/.audit.loupe.w5dbeiwo/artifacts/program",
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
The Weave compiler toolchain successfully compiles, optimizes, and links the `fibonacci.weave` program. The source computes `fib(10)` iteratively, which is constant-folded by the LLVM optimizer into a direct return of the constant `55`. The final native executable contains a minimal `main` function (`movl $55, %eax; retq`) that correctly implements the source semantics. All configured runtime matrix cases pass, and the optimized LLVM and native code budgets are strictly respected without any remaining compiler-generated overhead.

## Verification matrix
- Source semantics and expected result: PASS. The Weave source defines an iterative `fib` function and calls it with `10`. The expected return value is `55` (as noted in the source comments and runtime sidecar).
- Weave-to-WIR semantic preservation: PASS. The WIR projection accurately reflects the source structure, including the `fib` function, the `le_i32` condition, the iterative `while` loop, and the `main` entry point calling `fib` with `10`.
- WIR-to-raw-LLVM semantic preservation: PASS. The raw LLVM IR correctly translates the WIR. It uses `alloca` for local variables, `icmp sle` for signed comparisons, and `add i32` for arithmetic, matching the `i32` types and control flow of the WIR.
- Raw LLVM validity, SSA, types, and control flow: PASS. The raw LLVM IR is well-formed, uses valid SSA instructions, and correctly implements the branching and looping logic of the source.
- Optimized LLVM semantic preservation: PASS. The optimized LLVM IR reduces the entire program to `define i32 @main() { ret i32 55 }`. This is semantically equivalent to executing `fib(10)` at compile-time.
- Configured optimized LLVM metrics, functions, calls, and memory traffic: PASS. The analysis JSON shows the optimized LLVM contract passed with 1 function (`main`), 1 instruction (`ret`), 0 calls, 0 memory traffic, and 0 poison/undef uses.
- Integer signedness, overflow, shifts, and comparisons: PASS. The raw LLVM uses `icmp sle` (signed less-than-or-equal) matching `le_i32`, and `add i32` for arithmetic. `fib(10)` does not overflow `i32`.
- Calls, return values, ABI, stack alignment, and register use: PASS. The final assembly uses `movl $55, %eax` to set the return value in the correct ABI register (`%eax` for `i32` return on x86_64) and uses `retq`. Stack alignment is handled by the standard prologue/epilogue.
- Memory safety, lifetime, leaks, and undefined behavior: PASS. The raw LLVM uses `alloca` safely. The optimized LLVM has `memory(none)` and `willreturn`, indicating no memory leaks or undefined behavior.
- Target compatibility and native instruction validity: PASS. The target is `x86_64-pc-linux-gnu`. The instructions `movl` and `retq` are valid x86_64 instructions.
- Native runtime cases and expected observable behavior: PASS. The runtime matrix executed the linked artifact and observed `exit_code: 55`, matching the expected value.
- Configured native limits, required call targets, and loop backedges: PASS. The native budget passed. `main` has 2 instructions, 0 direct calls, 0 indirect calls, and 0 backward branches, all within the configured limits.
- Compiler-generated overhead remaining in optimized LLVM and final native code: PASS. All overhead from the raw LLVM (allocas, loops, branches) was completely eliminated by the optimizer. The final code is optimally minimal.

## Blocking findings
None found.

## Non-blocking opportunities
None found. The compiler successfully eliminated all temporary stack traffic and control flow overhead, producing optimal constant-folded native code.

## Suggested verification
- Add a runtime test case with a non-constant input (if the language supports dynamic input) to verify the iterative loop logic in native code.
- Add a test case for `fib(0)` and `fib(1)` to verify the `le_i32 n 1` early return path.

<details>
<summary>Raw model response</summary>

```text
OK
## Summary
The Weave compiler toolchain successfully compiles, optimizes, and links the `fibonacci.weave` program. The source computes `fib(10)` iteratively, which is constant-folded by the LLVM optimizer into a direct return of the constant `55`. The final native executable contains a minimal `main` function (`movl $55, %eax; retq`) that correctly implements the source semantics. All configured runtime matrix cases pass, and the optimized LLVM and native code budgets are strictly respected without any remaining compiler-generated overhead.

## Verification matrix
- Source semantics and expected result: PASS. The Weave source defines an iterative `fib` function and calls it with `10`. The expected return value is `55` (as noted in the source comments and runtime sidecar).
- Weave-to-WIR semantic preservation: PASS. The WIR projection accurately reflects the source structure, including the `fib` function, the `le_i32` condition, the iterative `while` loop, and the `main` entry point calling `fib` with `10`.
- WIR-to-raw-LLVM semantic preservation: PASS. The raw LLVM IR correctly translates the WIR. It uses `alloca` for local variables, `icmp sle` for signed comparisons, and `add i32` for arithmetic, matching the `i32` types and control flow of the WIR.
- Raw LLVM validity, SSA, types, and control flow: PASS. The raw LLVM IR is well-formed, uses valid SSA instructions, and correctly implements the branching and looping logic of the source.
- Optimized LLVM semantic preservation: PASS. The optimized LLVM IR reduces the entire program to `define i32 @main() { ret i32 55 }`. This is semantically equivalent to executing `fib(10)` at compile-time.
- Configured optimized LLVM metrics, functions, calls, and memory traffic: PASS. The analysis JSON shows the optimized LLVM contract passed with 1 function (`main`), 1 instruction (`ret`), 0 calls, 0 memory traffic, and 0 poison/undef uses.
- Integer signedness, overflow, shifts, and comparisons: PASS. The raw LLVM uses `icmp sle` (signed less-than-or-equal) matching `le_i32`, and `add i32` for arithmetic. `fib(10)` does not overflow `i32`.
- Calls, return values, ABI, stack alignment, and register use: PASS. The final assembly uses `movl $55, %eax` to set the return value in the correct ABI register (`%eax` for `i32` return on x86_64) and uses `retq`. Stack alignment is handled by the standard prologue/epilogue.
- Memory safety, lifetime, leaks, and undefined behavior: PASS. The raw LLVM uses `alloca` safely. The optimized LLVM has `memory(none)` and `willreturn`, indicating no memory leaks or undefined behavior.
- Target compatibility and native instruction validity: PASS. The target is `x86_64-pc-linux-gnu`. The instructions `movl` and `retq` are valid x86_64 instructions.
- Native runtime cases and expected observable behavior: PASS. The runtime matrix executed the linked artifact and observed `exit_code: 55`, matching the expected value.
- Configured native limits, required call targets, and loop backedges: PASS. The native budget passed. `main` has 2 instructions, 0 direct calls, 0 indirect calls, and 0 backward branches, all within the configured limits.
- Compiler-generated overhead remaining in optimized LLVM and final native code: PASS. All overhead from the raw LLVM (allocas, loops, branches) was completely eliminated by the optimizer. The final code is optimally minimal.

## Blocking findings
None found.

## Non-blocking opportunities
None found. The compiler successfully eliminated all temporary stack traffic and control flow overhead, producing optimal constant-folded native code.

## Suggested verification
- Add a runtime test case with a non-constant input (if the language supports dynamic input) to verify the iterative loop logic in native code.
- Add a test case for `fib(0)` and `fib(1)` to verify the `le_i32 n 1` early return path.
```
</details>
