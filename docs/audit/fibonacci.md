# Weave Loupe Audit Report

## Verdict

- **Status:** OK
- **Code:** none
- **Reason:** No blocking defect found.

## Reproducibility

- **Report content SHA-256:** `645ab9044174a78e66567f634bc40e03fab6aca4bc614dabb51fee8eef71d2e7`
- **Audit timestamp (UTC):** `2026-07-31T19:54:15+00:00`
- **Re-audit no later than (UTC):** `2026-08-30T19:54:15+00:00`
- **Maximum audit age:** `30` days
- **Audited input invalidation:** `any source or runtime matrix hash change`
- **Compiler binary invalidation:** `any compiler binary hash change`
- **Auditor invalidation:** `any audit implementation fingerprint change`
- **Model invalidation:** `any configured LLM model or endpoint change`
- **Request limit invalidation:** `any configured LLM max-token change`
- **Development compiler invalidation:** `any compiler version change`
- **Identity attestation upgrade:** `required when command identity becomes available`
- **Audited source Git SHA:** `ae692928f6e6cd76a0194ac809595ace76f67802`
- **Source tree state:** `clean`
- **Weave Loupe Git SHA:** `ae692928f6e6cd76a0194ac809595ace76f67802`
- **Auditor content SHA-256:** `9fc360c21266287d26bd290a01ff552ba59c5a40a51967f1ef17335a4c59630f`
- **weavec Git SHA:** `3d865013f2c65d327f8f3bf508ec741e4f7b5c22`
- **weavec binary SHA-256:** `1d4ea5e53e69754b4db409d702e5f9d5303f2f45753537d2e858af0340513a31`
- **weavec version:** `weavec v0.3.0+git.3d865013f2c6`
- **weavec build kind:** `development`
- **weavec version source:** `command`
- **LLM endpoint:** `https://integrate.api.nvidia.com/v1`
- **LLM model:** `z-ai/glm-5.2`
- **LLM max tokens:** `4096`
- **LLM temperature:** `0.0`
- **LLM prompt SHA-256:** `4532c3bc97441c60c07225d04e5c9ad7230531ce6bf703453ca59d13b853450f`
- **LLM request SHA-256:** `dd54a712a9be298bfee9793c3a8d9f08957c7cc8f1409f67fb8248d820e1d85c`
- **Provider-reported model:** `z-ai/glm-5.2`
- **Provider response ID:** `chatcmpl-687141f6-b415-441c-943a-39aff7f4d5e6`
- **Provider system fingerprint:** `unavailable`
- **Provider finish reason:** `stop`
- **Provider created (Unix):** `1785527656`
- **Provider prompt tokens:** `13774`
- **Provider completion tokens:** `875`
- **Provider total tokens:** `14649`
- **GitHub run ID:** `30660804249`
- **GitHub workflow SHA:** `0b88cfec827ce188fb8ce37b067c3295bc2ee894`

## Machine and running conditions

- **Operating system:** `Ubuntu 24.04.4 LTS`
- **Kernel:** `Linux 6.17.0-1020-azure`
- **Architecture:** `x86_64`
- **CPU:** `AMD EPYC 9V74 80-Core Processor`
- **Logical CPUs:** `4`
- **Memory:** `16766418944` bytes
- **Python:** `3.12.13`
- **libc:** `glibc 2.39`

## Audited inputs

- Source `docs/audit/fibonacci.weave` — SHA-256 `6cad78b00aaa67b434c4d7a920a3c9065bf7d7a802f5881ef831602e3e48b3d6`
- Runtime matrix `docs/audit/fibonacci.audit.json` — SHA-256 `4032e56fd1ee0c869bded117fe11d6a7e3d00d3dd7c57edea7991230d7ef6ee6`

## Captured evidence

- `assembly` — SHA-256 `c9ada3f9b21f676366d69be9e0d67e8a8db3786a9e4fd3783f3dbe706b368e97`
- `build_manifest` — SHA-256 `7cddf363ce874f99f6f4c08d4ef6db50a78caf941adb81c2b3ef5de8441c36a2`
- `diagnostics` — SHA-256 `a40b573053cda943c381742ad672108b1c8985ecc97e2f21dfa604094e31ff63`
- `disassembly` — SHA-256 `3cbd74406c2576b10b521535213c7d2d51e0c4ee5a24e490febfdcf8afc0b94b`
- `executable` — SHA-256 `90a568e286f9d2d5ae1873d965c2364f89a46d071136e1cd18a1914f9e95ef89`
- `llvm` — SHA-256 `c3807dfd8f9121f374bb97d4ab750d663093ebd55ef0691bbd93de7d543d0aab`
- `optimization_record` — SHA-256 `3521b76a68875746bebe1b706f3129da67abd93aded7e79ead467f4008c16fa3`
- `optimized_llvm` — SHA-256 `057f82c503f63153db2cd05433300ee212c02b0986729d8497760c3595e18a21`
- `trace` — SHA-256 `973c782fd9436e06f7203fea9af0c26a62e0973bd46db644f14c0bb8e4e4f0c5`
- `wir` — SHA-256 `5f6b3cf1a951ae4c972e0a00c44122739c0f7eb4c7fae78985792863fadea102`

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
; source: /tmp/weavec-build-bG4WuD/program.wir
; core-version: 2

; weave.source kind=function index=0 bytes=836..933 wir-bytes=3064..3616 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave"
; function: main
; params: none
; returns: i32
define i32 @main() {
entry:
; weave.source kind=statement index=0 bytes=893..931 wir-bytes=3372..3614 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave"
  ; return
  %t0 = call i32 @fib(i32 10)
  ret i32 %t0
}

; weave.source kind=function index=0 bytes=252..833 wir-bytes=176..3025 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave"
; function: fib
; params: i32
; returns: i32
define internal i32 @fib(i32 %n) {
entry:
  %previous.addr = alloca i32
  %current.addr = alloca i32
  %index.addr = alloca i32
; weave.source kind=statement index=0 bytes=313..455 wir-bytes=627..1281 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave"
  ; if condition
  %t0 = icmp sle i32 %n, 1
  br i1 %t0, label %then, label %endif
then:
  ; then
; weave.source kind=statement index=0 bytes=412..422 wir-bytes=1120..1164 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave"
  ; return
  ret i32 %n
endif:
; weave.source kind=statement index=0 bytes=462..494 wir-bytes=1316..1484 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave"
  ; let previous
  store i32 0, ptr %previous.addr
; weave.source kind=statement index=0 bytes=501..532 wir-bytes=1519..1686 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave"
  ; let current
  store i32 1, ptr %current.addr
; weave.source kind=statement index=0 bytes=539..568 wir-bytes=1721..1886 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave"
  ; let index
  store i32 2, ptr %index.addr
; weave.source kind=statement index=0 bytes=575..808 wir-bytes=1921..2938 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave"
  ; while condition
  br label %while.cond1
while.cond1:
  %t1 = load i32, ptr %index.addr
  %t2 = icmp sle i32 %t1, %n
  br i1 %t2, label %while.body1, label %while.end1
while.body1:
  ; while body
; weave.source kind=statement index=0 bytes=651..692 wir-bytes=2267..2478 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave"
  %t3 = load i32, ptr %previous.addr
  %t4 = load i32, ptr %current.addr
  %t5 = add i32 %t3, %t4
  ; let next
; weave.source kind=statement index=0 bytes=703..725 wir-bytes=2513..2569 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave"
  ; set previous
  %t6 = load i32, ptr %current.addr
  store i32 %t6, ptr %previous.addr
; weave.source kind=statement index=0 bytes=736..754 wir-bytes=2604..2656 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave"
  ; set current
  store i32 %t5, ptr %current.addr
; weave.source kind=statement index=0 bytes=765..806 wir-bytes=2691..2936 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave"
  ; set index
  %t7 = load i32, ptr %index.addr
  %t8 = add i32 %t7, 1
  store i32 %t8, ptr %index.addr
  br label %while.cond1
while.end1:
; weave.source kind=statement index=0 bytes=815..831 wir-bytes=2973..3023 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci.weave"
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
        "elapsed_seconds": 0.011178,
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
    "process_count": 117,
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
    "available": true,
    "entry_point": "main",
    "functions": {
      ".plt": {
        "backward_branches": 0,
        "backward_conditional_branches": 0,
        "conditional_branches": 0,
        "direct_calls": [],
        "indirect_calls": 0,
        "instructions": 2,
        "padding_instructions": 1
      },
      "__cxa_finalize@plt": {
        "backward_branches": 0,
        "backward_conditional_branches": 0,
        "conditional_branches": 0,
        "direct_calls": [],
        "indirect_calls": 0,
        "instructions": 1,
        "padding_instructions": 1
      },
      "__do_global_dtors_aux": {
        "backward_branches": 0,
        "backward_conditional_branches": 0,
        "conditional_branches": 2,
        "direct_calls": [
          "__cxa_finalize@plt",
          "deregister_tm_clones"
        ],
        "indirect_calls": 0,
        "instructions": 14,
        "padding_instructions": 2
      },
      "_fini": {
        "backward_branches": 0,
        "backward_conditional_branches": 0,
        "conditional_branches": 0,
        "direct_calls": [],
        "indirect_calls": 0,
        "instructions": 4,
        "padding_instructions": 0
      },
      "_init": {
        "backward_branches": 0,
        "backward_conditional_branches": 0,
        "conditional_branches": 1,
        "direct_calls": [],
        "indirect_calls": 1,
        "instructions": 8,
        "padding_instructions": 0
      },
      "_start": {
        "backward_branches": 0,
        "backward_conditional_branches": 0,
        "conditional_branches": 0,
        "direct_calls": [],
        "indirect_calls": 1,
        "instructions": 13,
        "padding_instructions": 1
      },
      "deregister_tm_clones": {
        "backward_branches": 0,
        "backward_conditional_branches": 0,
        "conditional_branches": 2,
        "direct_calls": [],
        "indirect_calls": 0,
        "instructions": 9,
        "padding_instructions": 2
      },
      "frame_dummy": {
        "backward_branches": 1,
        "backward_conditional_branches": 0,
        "conditional_branches": 0,
        "direct_calls": [],
        "indirect_calls": 0,
        "instructions": 2,
        "padding_instructions": 1
      },
      "main": {
        "backward_branches": 0,
        "backward_conditional_branches": 0,
        "conditional_branches": 0,
        "direct_calls": [],
        "indirect_calls": 0,
        "instructions": 2,
        "padding_instructions": 0
      },
      "register_tm_clones": {
        "backward_branches": 0,
        "backward_conditional_branches": 0,
        "conditional_branches": 2,
        "direct_calls": [],
        "indirect_calls": 0,
        "instructions": 14,
        "padding_instructions": 2
      }
    },
    "llvm_functions": [
      "main"
    ],
    "program_owned_functions": [
      "main"
    ],
    "reachability_complete": true,
    "reachable_indirect_calls": 0,
    "reachable_program_functions": [
      "main"
    ],
    "runtime_functions": [],
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
          "elapsed_seconds": 0.011178,
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
      "process_count": 117,
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
  "output": "/tmp/loupe-audit-8ew6nsxb/.audit.loupe.55b431_v/artifacts/program",
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
The Weave compiler toolchain successfully translates the `fibonacci.weave` source into a correct, ABI-valid, and fully optimized native executable. The source computes `fib(10)` iteratively, which is constant-folded by the LLVM optimizer into a direct return of the constant `55`. The semantic behavior is preserved across all stages: from Weave source to WIR, raw LLVM IR, optimized LLVM IR, target assembly, and the final linked executable. The runtime matrix confirms the exact linked artifact exits with code `55`. Both the optimized LLVM contract and the native optimization budget pass without exceeding any structural or instruction limits. No compiler-generated overhead remains in the final native code.

## Verification matrix
- Source semantics and expected result: PASS. The Weave source defines an iterative `fib` function and calls it with `10`. The expected return value is `55` as per the source comments and standard Fibonacci sequence.
- Weave-to-WIR semantic preservation: PASS. The WIR projection accurately reflects the source structure, including the `le_i32` condition, `while` loop, and `add_i32` operations.
- WIR-to-raw-LLVM semantic preservation: PASS. The raw LLVM IR correctly maps WIR variables to `alloca`s, uses `icmp sle` for the `le_i32` condition, and implements the loop and additions as specified.
- Raw LLVM validity, SSA, types, and control flow: PASS. The raw LLVM IR is valid, uses correct SSA form for temporaries, correctly typed `i32` operations, and valid control flow branches.
- Optimized LLVM semantic preservation: PASS. The optimized LLVM IR reduces the entire program to `define i32 @main() { entry: ret i32 55 }`, correctly constant-folding the iterative loop.
- Configured optimized LLVM metrics, functions, calls, and memory traffic: PASS. The analysis JSON shows the optimized LLVM contract passed with 1 function, 1 instruction, 1 basic block, and 0 memory traffic, matching the limits exactly.
- Integer signedness, overflow, shifts, and comparisons: PASS. The `fib(10)` computation does not overflow `i32`, and signed comparisons (`icmp sle`) are correctly translated and folded.
- Calls, return values, ABI, stack alignment, and register use: PASS. The final assembly uses `movl $55, %eax` and `retq`, strictly adhering to the System V AMD64 ABI for returning 32-bit integers in `%eax`.
- Memory safety, lifetime, leaks, and undefined behavior: PASS. The optimized LLVM is marked `nofree norecurse nosync nounwind willreturn memory(none)`, and the final native code contains no memory accesses or allocations.
- Target compatibility and native instruction validity: PASS. The target assembly and disassembly show valid x86_64 instructions (`movl`, `retq`) compatible with the `x86_64-pc-linux-gnu` target.
- Native runtime cases and expected observable behavior: PASS. The runtime matrix executed the exact linked artifact and observed an exit code of `55`, matching the expected value.
- Configured native limits, required call targets, and loop backedges: PASS. The native budget passed with `main` containing exactly 2 instructions, 0 calls, and 0 backedges, meeting all configured limits.
- Compiler-generated overhead remaining in optimized LLVM and final native code: PASS. No overhead remains. The `fib` function was inlined and deleted, and the loop was constant-folded, leaving only the minimal `mov` and `ret` instructions.

## Blocking findings
None found.

## Non-blocking opportunities
None found. The compiler successfully eliminated all stack traffic, temporary variables, and control flow overhead during the LLVM optimization stage, achieving the theoretical minimum for this specific program.

## Suggested verification
- Test with a non-constant input to `fib` (e.g., reading from standard input or command line arguments) to verify the iterative loop and control flow are correctly compiled without constant-folding.
- Test with a larger Fibonacci number (e.g., `fib(47)`) to ensure signed 32-bit overflow behavior is handled predictably if such semantics are intended by the language specification.

<details>
<summary>Raw model response</summary>

```text
OK
## Summary
The Weave compiler toolchain successfully translates the `fibonacci.weave` source into a correct, ABI-valid, and fully optimized native executable. The source computes `fib(10)` iteratively, which is constant-folded by the LLVM optimizer into a direct return of the constant `55`. The semantic behavior is preserved across all stages: from Weave source to WIR, raw LLVM IR, optimized LLVM IR, target assembly, and the final linked executable. The runtime matrix confirms the exact linked artifact exits with code `55`. Both the optimized LLVM contract and the native optimization budget pass without exceeding any structural or instruction limits. No compiler-generated overhead remains in the final native code.

## Verification matrix
- Source semantics and expected result: PASS. The Weave source defines an iterative `fib` function and calls it with `10`. The expected return value is `55` as per the source comments and standard Fibonacci sequence.
- Weave-to-WIR semantic preservation: PASS. The WIR projection accurately reflects the source structure, including the `le_i32` condition, `while` loop, and `add_i32` operations.
- WIR-to-raw-LLVM semantic preservation: PASS. The raw LLVM IR correctly maps WIR variables to `alloca`s, uses `icmp sle` for the `le_i32` condition, and implements the loop and additions as specified.
- Raw LLVM validity, SSA, types, and control flow: PASS. The raw LLVM IR is valid, uses correct SSA form for temporaries, correctly typed `i32` operations, and valid control flow branches.
- Optimized LLVM semantic preservation: PASS. The optimized LLVM IR reduces the entire program to `define i32 @main() { entry: ret i32 55 }`, correctly constant-folding the iterative loop.
- Configured optimized LLVM metrics, functions, calls, and memory traffic: PASS. The analysis JSON shows the optimized LLVM contract passed with 1 function, 1 instruction, 1 basic block, and 0 memory traffic, matching the limits exactly.
- Integer signedness, overflow, shifts, and comparisons: PASS. The `fib(10)` computation does not overflow `i32`, and signed comparisons (`icmp sle`) are correctly translated and folded.
- Calls, return values, ABI, stack alignment, and register use: PASS. The final assembly uses `movl $55, %eax` and `retq`, strictly adhering to the System V AMD64 ABI for returning 32-bit integers in `%eax`.
- Memory safety, lifetime, leaks, and undefined behavior: PASS. The optimized LLVM is marked `nofree norecurse nosync nounwind willreturn memory(none)`, and the final native code contains no memory accesses or allocations.
- Target compatibility and native instruction validity: PASS. The target assembly and disassembly show valid x86_64 instructions (`movl`, `retq`) compatible with the `x86_64-pc-linux-gnu` target.
- Native runtime cases and expected observable behavior: PASS. The runtime matrix executed the exact linked artifact and observed an exit code of `55`, matching the expected value.
- Configured native limits, required call targets, and loop backedges: PASS. The native budget passed with `main` containing exactly 2 instructions, 0 calls, and 0 backedges, meeting all configured limits.
- Compiler-generated overhead remaining in optimized LLVM and final native code: PASS. No overhead remains. The `fib` function was inlined and deleted, and the loop was constant-folded, leaving only the minimal `mov` and `ret` instructions.

## Blocking findings
None found.

## Non-blocking opportunities
None found. The compiler successfully eliminated all stack traffic, temporary variables, and control flow overhead during the LLVM optimization stage, achieving the theoretical minimum for this specific program.

## Suggested verification
- Test with a non-constant input to `fib` (e.g., reading from standard input or command line arguments) to verify the iterative loop and control flow are correctly compiled without constant-folding.
- Test with a larger Fibonacci number (e.g., `fib(47)`) to ensure signed 32-bit overflow behavior is handled predictably if such semantics are intended by the language specification.
```
</details>
