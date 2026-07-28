# Weave Loupe Audit Report

## Verdict

- **Status:** OK
- **Code:** none
- **Reason:** No blocking defect found.

## Reproducibility

- **Report content SHA-256:** `de7144fa24dd6cd1806bf6daf7379cf3fe8add7b87a843fc0db0e3a31cff09fc`
- **Audit timestamp (UTC):** `2026-07-28T12:30:26+00:00`
- **Re-audit no later than (UTC):** `2026-08-27T12:30:26+00:00`
- **Maximum audit age:** `30` days
- **Audited input invalidation:** `any source or runtime matrix hash change`
- **Compiler binary invalidation:** `any compiler binary hash change`
- **Auditor invalidation:** `any audit implementation fingerprint change`
- **Model invalidation:** `any configured LLM model or endpoint change`
- **Request limit invalidation:** `any configured LLM max-token change`
- **Development compiler invalidation:** `any compiler version change`
- **Identity attestation upgrade:** `required when command identity becomes available`
- **Audited source Git SHA:** `b0759cdee5d55431afa8929075bd5ebfa7a17e80`
- **Source tree state:** `clean`
- **Weave Loupe Git SHA:** `b0759cdee5d55431afa8929075bd5ebfa7a17e80`
- **Auditor content SHA-256:** `fd80e6e3ce16bc498ff05220db32a87bd6f545a2b43eb7c344e9372cffe85c44`
- **weavec Git SHA:** `cb1c96b173d4c6cba89347950468001061321370`
- **weavec binary SHA-256:** `b9b977a6e481f1bd62a4fdd85eed41d2a09499a411acb218d49ef30fa0c49245`
- **weavec version:** `weavec v0.3.0+git.cb1c96b173d4`
- **weavec build kind:** `development`
- **weavec version source:** `command`
- **LLM endpoint:** `https://integrate.api.nvidia.com/v1`
- **LLM model:** `z-ai/glm-5.2`
- **LLM max tokens:** `4096`
- **LLM temperature:** `0.0`
- **LLM prompt SHA-256:** `6f1f1ba2de20f0578541339b06ad1b5d666991b4c4cae8e0af0a83a91fb98d4f`
- **LLM request SHA-256:** `5f3178df1c29e170c5d1019cce16daa19fbc1f49551d31704f5c88e890872afe`
- **Provider-reported model:** `z-ai/glm-5.2`
- **Provider response ID:** `chatcmpl-7dc2cd5c-0a0e-4f29-a764-adf9d5e1f141`
- **Provider system fingerprint:** `unavailable`
- **Provider finish reason:** `stop`
- **Provider created (Unix):** `1785241827`
- **Provider prompt tokens:** `11278`
- **Provider completion tokens:** `1081`
- **Provider total tokens:** `12359`
- **GitHub run ID:** `30359169203`
- **GitHub workflow SHA:** `73d032a316133ab1db58f74901c519b0a6d78d30`

## Machine and running conditions

- **Operating system:** `Ubuntu 24.04.4 LTS`
- **Kernel:** `Linux 6.17.0-1020-azure`
- **Architecture:** `x86_64`
- **CPU:** `INTEL(R) XEON(R) PLATINUM 8573C`
- **Logical CPUs:** `4`
- **Memory:** `16765386752` bytes
- **Python:** `3.12.13`
- **libc:** `glibc 2.39`

## Audited inputs

- Source `docs/audit/fibonacci.weave` — SHA-256 `6cad78b00aaa67b434c4d7a920a3c9065bf7d7a802f5881ef831602e3e48b3d6`
- Runtime matrix `docs/audit/fibonacci.audit.json` — SHA-256 `44d43daa892486a4dde8bf635701bc81efcd350ea06da7b7af2d57009d6e1189`

## Captured evidence

- `assembly` — SHA-256 `c9ada3f9b21f676366d69be9e0d67e8a8db3786a9e4fd3783f3dbe706b368e97`
- `build_manifest` — SHA-256 `3481a6a100cf5564382deb24d65ac199d1886b74f5d377d8c9376c0127e85bed`
- `diagnostics` — SHA-256 `a40b573053cda943c381742ad672108b1c8985ecc97e2f21dfa604094e31ff63`
- `disassembly` — SHA-256 `3cbd74406c2576b10b521535213c7d2d51e0c4ee5a24e490febfdcf8afc0b94b`
- `executable` — SHA-256 `90a568e286f9d2d5ae1873d965c2364f89a46d071136e1cd18a1914f9e95ef89`
- `llvm` — SHA-256 `2b8606df6b5544a25f44567dd423ffe974f54b2ee06a1b58dcf670fab65f387a`
- `optimization_record` — SHA-256 `3521b76a68875746bebe1b706f3129da67abd93aded7e79ead467f4008c16fa3`
- `optimized_llvm` — SHA-256 `057f82c503f63153db2cd05433300ee212c02b0986729d8497760c3595e18a21`
- `trace` — SHA-256 `9e100ae293767539eb406dc28704742846236f6dea99759cf6f731155a44d9ba`
- `wir` — SHA-256 `8f785c53dba0d8708cc32470bb1692ba344d02759f051b13164ef9204710b4ef`

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
; source: /tmp/weavec-build-EhPAVp/program.wir
; core-version: 2

; weave.source kind=function index=0 bytes=836..933 wir-bytes=3294..3880 path="docs/audit/fibonacci.weave"
; function: main
; params: none
; returns: i32
define i32 @main() {
entry:
; weave.source kind=statement index=0 bytes=893..931 wir-bytes=3602..3878 path="docs/audit/fibonacci.weave"
  ; return
  %t0 = call i32 @fib(i32 10)
  ret i32 %t0
}

; weave.source kind=function index=0 bytes=252..833 wir-bytes=134..3255 path="docs/audit/fibonacci.weave"
; function: fib
; params: i32
; returns: i32
define internal i32 @fib(i32 %n) {
entry:
  %previous.addr = alloca i32
  %current.addr = alloca i32
  %index.addr = alloca i32
; weave.source kind=statement index=0 bytes=313..455 wir-bytes=585..1273 path="docs/audit/fibonacci.weave"
  ; if condition
  %t0 = icmp sle i32 %n, 1
  br i1 %t0, label %then, label %endif
then:
  ; then
; weave.source kind=statement index=0 bytes=412..422 wir-bytes=1078..1156 path="docs/audit/fibonacci.weave"
  ; return
  ret i32 %n
endif:
; weave.source kind=statement index=0 bytes=462..494 wir-bytes=1308..1476 path="docs/audit/fibonacci.weave"
  ; let previous
  store i32 0, ptr %previous.addr
; weave.source kind=statement index=0 bytes=501..532 wir-bytes=1511..1678 path="docs/audit/fibonacci.weave"
  ; let current
  store i32 1, ptr %current.addr
; weave.source kind=statement index=0 bytes=539..568 wir-bytes=1713..1878 path="docs/audit/fibonacci.weave"
  ; let index
  store i32 2, ptr %index.addr
; weave.source kind=statement index=0 bytes=575..808 wir-bytes=1913..3134 path="docs/audit/fibonacci.weave"
  ; while condition
  br label %while.cond1
while.cond1:
  %t1 = load i32, ptr %index.addr
  %t2 = icmp sle i32 %t1, %n
  br i1 %t2, label %while.body1, label %while.end1
while.body1:
  ; while body
; weave.source kind=statement index=0 bytes=651..692 wir-bytes=2259..2470 path="docs/audit/fibonacci.weave"
  %t3 = load i32, ptr %previous.addr
  %t4 = load i32, ptr %current.addr
  %t5 = add i32 %t3, %t4
  ; let next
; weave.source kind=statement index=0 bytes=703..725 wir-bytes=2505..2629 path="docs/audit/fibonacci.weave"
  ; set previous
  %t6 = load i32, ptr %current.addr
  store i32 %t6, ptr %previous.addr
; weave.source kind=statement index=0 bytes=736..754 wir-bytes=2664..2784 path="docs/audit/fibonacci.weave"
  ; set current
  store i32 %t5, ptr %current.addr
; weave.source kind=statement index=0 bytes=765..806 wir-bytes=2819..3132 path="docs/audit/fibonacci.weave"
  ; set index
  %t7 = load i32, ptr %index.addr
  %t8 = add i32 %t7, 1
  store i32 %t8, ptr %index.addr
  br label %while.cond1
while.end1:
; weave.source kind=statement index=0 bytes=815..831 wir-bytes=3169..3253 path="docs/audit/fibonacci.weave"
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

### Runtime execution matrix

```json
{
  "case_count": 1,
  "cases": [
    {
      "actual": {
        "exit_code": 55,
        "stderr": "",
        "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "stdout": "",
        "stdout_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
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
  "passed": true,
  "sidecar": "docs/audit/fibonacci.audit.json",
  "sidecar_sha256": "44d43daa892486a4dde8bf635701bc81efcd350ea06da7b7af2d57009d6e1189",
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
        "direct_calls": [],
        "indirect_calls": 0,
        "instructions": 2,
        "padding_instructions": 1
      },
      "__cxa_finalize@plt": {
        "direct_calls": [],
        "indirect_calls": 0,
        "instructions": 1,
        "padding_instructions": 1
      },
      "__do_global_dtors_aux": {
        "direct_calls": [
          "__cxa_finalize@plt",
          "deregister_tm_clones"
        ],
        "indirect_calls": 0,
        "instructions": 14,
        "padding_instructions": 2
      },
      "_fini": {
        "direct_calls": [],
        "indirect_calls": 0,
        "instructions": 4,
        "padding_instructions": 0
      },
      "_init": {
        "direct_calls": [],
        "indirect_calls": 1,
        "instructions": 8,
        "padding_instructions": 0
      },
      "_start": {
        "direct_calls": [],
        "indirect_calls": 1,
        "instructions": 13,
        "padding_instructions": 1
      },
      "deregister_tm_clones": {
        "direct_calls": [],
        "indirect_calls": 0,
        "instructions": 9,
        "padding_instructions": 2
      },
      "frame_dummy": {
        "direct_calls": [],
        "indirect_calls": 0,
        "instructions": 2,
        "padding_instructions": 1
      },
      "main": {
        "direct_calls": [],
        "indirect_calls": 0,
        "instructions": 2,
        "padding_instructions": 0
      },
      "register_tm_clones": {
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
  "runtime": {
    "case_count": 1,
    "cases": [
      {
        "actual": {
          "exit_code": 55,
          "stderr": "",
          "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
          "stdout": "",
          "stdout_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
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
    "passed": true,
    "sidecar": "docs/audit/fibonacci.audit.json",
    "sidecar_sha256": "44d43daa892486a4dde8bf635701bc81efcd350ea06da7b7af2d57009d6e1189",
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
  "optimization": {"level": "O3", "cpu": "native", "tune_cpu": "native"},
  "output": "/tmp/loupe-audit-2_7ha9th/.audit.loupe.id5hz9fe/artifacts/program",
  "sources": ["docs/audit/fibonacci.weave"]
}
```

### Compiler trace

```json
{
  "format": "weavec-compilation-trace-v1",
  "status": "succeeded",
  "phase": "complete",
  "sources": ["docs/audit/fibonacci.weave"],
  "events": []
}
```

## LLM review

## Summary
The final native program for `docs/audit/fibonacci.weave` is correct, safe, ABI-valid, target-compatible, and free from avoidable compiler-generated overhead. The Weave source computes `fib(10)` iteratively with an expected signed i32 return value of 55. The WIR accurately reflects this logic. The raw LLVM IR is valid, well-typed, and uses correct signed comparisons (`icmp sle`). LLVM completely constant-folds the program, as evidenced by the optimized LLVM IR (`ret i32 55`), the optimization record (loop deletion and inlining), and the final linked executable disassembly (`movl $0x37, %eax; retq`). The runtime matrix confirms the exact linked artifact exits with code 55, matching the expected sidecar values. No merge-blocking defects were found.

## Verification matrix
- Source semantics and expected result: PASS. The Weave source defines `fib(n)` returning `n` if `n <= 1`, otherwise iterating to compute the Fibonacci sequence. `main` returns `fib(10)`. The source comments explicitly state the expected result is 55.
- Weave-to-WIR semantic preservation: PASS. The WIR projection preserves the `fib` and `main` functions, the `le_i32` condition, the iterative `while` loop, the `add_i32` operations, and the `call_i32` from `main` to `fib` with constant 10.
- WIR-to-raw-LLVM semantic preservation: PASS. The raw LLVM IR maps the WIR variables to `alloca` slots, uses `icmp sle` for the `le_i32` conditions, and `add i32` for the additions, correctly preserving the control flow and semantics.
- Raw LLVM validity, SSA, types, and control flow: PASS. The raw LLVM IR is valid. It uses correct SSA form, well-typed `i32` operations, and valid control flow edges (`br`, `ret`) with no `undef` or `poison` uses according to the analysis JSON.
- Optimized LLVM semantic preservation: PASS. The optimized LLVM IR reduces the entire program to `define i32 @main() { entry: ret i32 55 }`, which is semantically equivalent to `fib(10)`. The optimization record confirms the loop was deleted as invariant and `fib` was inlined into `main`.
- Integer signedness, overflow, shifts, and comparisons: PASS. The IR uses `i32` throughout and `icmp sle` (signed less-than-or-equal) for comparisons, matching the `le_i32` WIR tokens. No shifts are present. The constant 55 does not overflow i32.
- Calls, return values, ABI, stack alignment, and register use: PASS. The final `main` function uses the System V AMD64 ABI correctly by placing the return value 55 in `%eax` (`movl $0x37, %eax`) and returns via `retq`. The prologue/epilogue analysis confirms 0 stack bytes are used.
- Memory safety, lifetime, leaks, and undefined behavior: PASS. The raw LLVM IR uses `alloca` for local variables, which are safe and automatically reclaimed. The optimized LLVM IR has no memory operations. No undefined behavior is present.
- Target compatibility and native instruction validity: PASS. The target triple is `x86_64-pc-linux-gnu`. The assembly and disassembly show valid x86_64 instructions (`movl`, `retq`) and standard ELF64 structure compatible with the specified target environment.
- Native runtime cases and expected observable behavior: PASS. The runtime matrix executed the exact linked artifact (SHA `90a568...`). The `constant-fibonacci` case passed, returning an exit code of 55 with no stdout/stderr, matching the expected sidecar values exactly.
- Compiler-generated overhead remaining in final native code: PASS. The final `main` function consists of exactly 2 instructions (`movl`, `retq`) with no padding, no stack manipulation, and no overhead. The `fib` function was completely optimized out.

## Blocking findings
None found.

## Non-blocking opportunities
- The raw LLVM IR uses `alloca` and `load`/`store` for local variables, which is a known, non-blocking overhead that is completely eliminated by the LLVM optimizer. No action is required.
- The Weave source algorithm for `fib` is iterative and handles `n <= 1` by returning `n`. For `n=0`, this returns 0, and for `n=1`, it returns 1. This is standard, but a source-level comment documenting the specific definition of `fib(0)` could improve clarity for edge cases. This is a style preference and not a defect.

## Suggested verification
- Add runtime matrix cases for edge values such as `fib(0)`, `fib(1)`, and `fib(2)` to explicitly verify the base case logic across the compiler pipeline.
- Add a runtime matrix case for a non-constant `fib` input (e.g., reading from stdin) to test the iterative loop in native execution without constant-folding masking potential loop bugs.

<details>
<summary>Raw model response</summary>

```text
OK
## Summary
The final native program for `docs/audit/fibonacci.weave` is correct, safe, ABI-valid, target-compatible, and free from avoidable compiler-generated overhead. The Weave source computes `fib(10)` iteratively with an expected signed i32 return value of 55. The WIR accurately reflects this logic. The raw LLVM IR is valid, well-typed, and uses correct signed comparisons (`icmp sle`). LLVM completely constant-folds the program, as evidenced by the optimized LLVM IR (`ret i32 55`), the optimization record (loop deletion and inlining), and the final linked executable disassembly (`movl $0x37, %eax; retq`). The runtime matrix confirms the exact linked artifact exits with code 55, matching the expected sidecar values. No merge-blocking defects were found.

## Verification matrix
- Source semantics and expected result: PASS. The Weave source defines `fib(n)` returning `n` if `n <= 1`, otherwise iterating to compute the Fibonacci sequence. `main` returns `fib(10)`. The source comments explicitly state the expected result is 55.
- Weave-to-WIR semantic preservation: PASS. The WIR projection preserves the `fib` and `main` functions, the `le_i32` condition, the iterative `while` loop, the `add_i32` operations, and the `call_i32` from `main` to `fib` with constant 10.
- WIR-to-raw-LLVM semantic preservation: PASS. The raw LLVM IR maps the WIR variables to `alloca` slots, uses `icmp sle` for the `le_i32` conditions, and `add i32` for the additions, correctly preserving the control flow and semantics.
- Raw LLVM validity, SSA, types, and control flow: PASS. The raw LLVM IR is valid. It uses correct SSA form, well-typed `i32` operations, and valid control flow edges (`br`, `ret`) with no `undef` or `poison` uses according to the analysis JSON.
- Optimized LLVM semantic preservation: PASS. The optimized LLVM IR reduces the entire program to `define i32 @main() { entry: ret i32 55 }`, which is semantically equivalent to `fib(10)`. The optimization record confirms the loop was deleted as invariant and `fib` was inlined into `main`.
- Integer signedness, overflow, shifts, and comparisons: PASS. The IR uses `i32` throughout and `icmp sle` (signed less-than-or-equal) for comparisons, matching the `le_i32` WIR tokens. No shifts are present. The constant 55 does not overflow i32.
- Calls, return values, ABI, stack alignment, and register use: PASS. The final `main` function uses the System V AMD64 ABI correctly by placing the return value 55 in `%eax` (`movl $0x37, %eax`) and returns via `retq`. The prologue/epilogue analysis confirms 0 stack bytes are used.
- Memory safety, lifetime, leaks, and undefined behavior: PASS. The raw LLVM IR uses `alloca` for local variables, which are safe and automatically reclaimed. The optimized LLVM IR has no memory operations. No undefined behavior is present.
- Target compatibility and native instruction validity: PASS. The target triple is `x86_64-pc-linux-gnu`. The assembly and disassembly show valid x86_64 instructions (`movl`, `retq`) and standard ELF64 structure compatible with the specified target environment.
- Native runtime cases and expected observable behavior: PASS. The runtime matrix executed the exact linked artifact (SHA `90a568...`). The `constant-fibonacci` case passed, returning an exit code of 55 with no stdout/stderr, matching the expected sidecar values exactly.
- Compiler-generated overhead remaining in final native code: PASS. The final `main` function consists of exactly 2 instructions (`movl`, `retq`) with no padding, no stack manipulation, and no overhead. The `fib` function was completely optimized out.

## Blocking findings
None found.

## Non-blocking opportunities
- The raw LLVM IR uses `alloca` and `load`/`store` for local variables, which is a known, non-blocking overhead that is completely eliminated by the LLVM optimizer. No action is required.
- The Weave source algorithm for `fib` is iterative and handles `n <= 1` by returning `n`. For `n=0`, this returns 0, and for `n=1`, it returns 1. This is standard, but a source-level comment documenting the specific definition of `fib(0)` could improve clarity for edge cases. This is a style preference and not a defect.

## Suggested verification
- Add runtime matrix cases for edge values such as `fib(0)`, `fib(1)`, and `fib(2)` to explicitly verify the base case logic across the compiler pipeline.
- Add a runtime matrix case for a non-constant `fib` input (e.g., reading from stdin) to test the iterative loop in native execution without constant-folding masking potential loop bugs.
```
</details>
