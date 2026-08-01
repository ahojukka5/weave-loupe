# Weave Loupe Audit Report

## Verdict

- **Status:** OK
- **Code:** none
- **Reason:** No blocking defect found.

## Reproducibility

- **Report content SHA-256:** `7df671b19312dc5b701f757f35a51d451e7edf6ce2daebe80ff1d5691162d7e9`
- **Audit timestamp (UTC):** `2026-08-01T16:25:50+00:00`
- **Re-audit no later than (UTC):** `2026-08-31T16:25:50+00:00`
- **Maximum audit age:** `30` days
- **Audited input invalidation:** `any source or runtime matrix hash change`
- **Compiler binary invalidation:** `any compiler binary hash change`
- **Auditor invalidation:** `any audit implementation fingerprint change`
- **Model invalidation:** `any configured LLM model or endpoint change`
- **Request limit invalidation:** `any configured LLM max-token change`
- **Development compiler invalidation:** `any compiler version change`
- **Identity attestation upgrade:** `required when command identity becomes available`
- **Audited source Git SHA:** `4a8e24cb3df4dce2f0943cf5d9a1580381eb8e59`
- **Source tree state:** `clean`
- **Weave Loupe Git SHA:** `4a8e24cb3df4dce2f0943cf5d9a1580381eb8e59`
- **Auditor content SHA-256:** `fe6415637f0342622124f72994844531585d9dc5c2d9c51144faab6d6695b52e`
- **weavec Git SHA:** `12aabdf62d4f8356e0d3961a2a1d2458ceab89da`
- **weavec binary SHA-256:** `d60c86dcbc787a7f51cbb60a9f1c3d35ba631f73e746ff5db8dc076044a5428c`
- **weavec version:** `weavec v0.3.0+git.12aabdf62d4f`
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
- **LLM prompt SHA-256:** `84d538cee410099ec456cfa51e109e279a66052a7c868c331ee025103ea735ca`
- **LLM request SHA-256:** `4f5ba0c86e4cb4e30c99722d4d6920d6742bfe04d78645eb0fceb4de888cefeb`
- **Provider-reported model:** `z-ai/glm-5.2`
- **Provider response ID:** `chatcmpl-2e1e1d54-ae46-4665-8bed-73cc0ca58b59`
- **Provider system fingerprint:** `unavailable`
- **Provider finish reason:** `stop`
- **Provider created (Unix):** `1785601556`
- **Provider prompt tokens:** `22922`
- **Provider completion tokens:** `1666`
- **Provider total tokens:** `24588`
- **GitHub run ID:** `30708045423`
- **GitHub workflow SHA:** `309c7b33fc3d698665923980e683a8890071b6e5`

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

- Source `docs/audit/fibonacci_runtime.weave` — SHA-256 `a0df013d2e54ac1426498c7fda686d113ae4ca4f7371fe3836c490ccf9343ba4` — 1779 bytes
- Runtime matrix `docs/audit/fibonacci_runtime.audit.json` — SHA-256 `dc8e5b6d2d6234628a045cdf49a535825fd337815af4d3fa5f53adfc59c0d7d2`

## Captured evidence

- `assembly` — SHA-256 `355551c6d11759a2137d794f6154bee9f187aff00d09f7f13887d82a052f3bf1`
- `build_manifest` — SHA-256 `ee42d4bff3efd2ede6e71d7e5c29be8cd980576d00f263ca580e392bfa46ff29`
- `diagnostics` — SHA-256 `a40b573053cda943c381742ad672108b1c8985ecc97e2f21dfa604094e31ff63`
- `disassembly` — SHA-256 `fc79aff611b518050aabf8fba9f4e4d9206bbb333c222fa01363938355cb582a`
- `executable` — SHA-256 `8096a9e86313b02d5038903d99f134a5e00416c11de2752492f204fc927fec8d`
- `llvm` — SHA-256 `7e8439b9675f6d714fa41cc14dec1b3fef8dc2cede7c6412068ee3822928fa28`
- `optimization_record` — SHA-256 `c1eed531ffbbd0e9d7c3558ecea6e951283dcb7e51ce4ebf7c1144aa66d37c6d`
- `optimized_llvm` — SHA-256 `7bda6a3ae32ec72bf1ac4f39971bba88d5f34fff09f56798c9cdbbf76414598e`
- `trace` — SHA-256 `c93c225da4447178c911c30bbeb170036679a5508fff214878cd7aef5013a3b8`
- `wir` — SHA-256 `ae3009fa26202190f5434cb1238a359e041e7744992f8ca151d086b46d396386`

## Complete compiler evidence

This section contains the exact evidence reviewed by the model so that the
source-to-native lowering can also be inspected manually.

### Weave source

```lisp
--- docs/audit/fibonacci_runtime.weave ---
; Runtime-input Weave Loupe audit corpus example.
; Reads WEAVE_AUDIT_N at runtime so LLVM cannot constant-fold the result.
; The audit harness supplies a decimal value in 0..46. Missing or numerically
; out-of-range input falls back to 10.
;
; Unlike fibonacci.weave, an input-dependent Fibonacci loop must remain in
; optimized LLVM and native code.

(program
  (name "fibonacci-runtime")
  (version "0.1")

  (extern getenv
    (params (name ptr))
    (returns ptr))

  (extern atoi
    (params (text ptr))
    (returns i32))

  (fn fib
    (params (n i32))
    (returns i32)
    (do
      (if
        (condition (le_i32 n (const_i32 1)))
        (then
          (do
            (return n)))
        (else
          (do)))

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

  (entry main
    (params)
    (returns i32)
    (do
      (let input ptr
        (call_ptr getenv
          (const_string_ptr "WEAVE_AUDIT_N")))
      (let n i32 (const_i32 10))

      (if
        (condition (ne_ptr input (const_null)))
        (then
          (do
            (set n (call_i32 atoi input))))
        (else
          (do)))

      (if
        (condition (lt_i32 n (const_i32 0)))
        (then
          (do
            (set n (const_i32 10))))
        (else
          (do)))

      (if
        (condition (gt_i32 n (const_i32 46)))
        (then
          (do
            (set n (const_i32 10))))
        (else
          (do)))

      (return (call_i32 fib n)))))
```

### WIR (provenance comments hidden)

```lisp
(core-module
  (core-version 2)
  (decls
    (extern getenv (params (name ptr)) (returns ptr))
    (extern atoi (params (text ptr)) (returns i32))
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
    (fn
      main
      (params)
      (returns i32)
      (do
        (let input ptr (call_ptr getenv (const_string_ptr "WEAVE_AUDIT_N")))
        (let n i32 (const_i32 10))
        (if
          (condition (ne_ptr input (const_null)))
          (then (do (set n (call_i32 atoi input))))
          (else (do)))
        (if (condition (lt_i32 n (const_i32 0))) (then (do (set n (const_i32 10)))) (else (do)))
        (if
          (condition (gt_i32 n (const_i32 46)))
          (then (do (set n (const_i32 10))))
          (else (do)))
        (return (call_i32 fib n))))))
```

### Raw LLVM IR

```llvm
; generated by weavec
; source: /tmp/weavec-build-iwF1I0/program.wir
; core-version: 2

; declarations

declare ptr @getenv(ptr)
declare i32 @atoi(ptr)

; string literals

@.str0 = private unnamed_addr constant [14 x i8] c"WEAVE_AUDIT_N\00"

; weave.source kind=function index=0 bytes=1100..1778 wir-bytes=3953..7450 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
; function: main
; params: none
; returns: i32
define i32 @main() {
entry:
  %n.addr = alloca i32
; weave.source kind=statement index=0 bytes=1157..1243 wir-bytes=4277..4597 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
  %t0 = getelementptr [14 x i8], ptr @.str0, i64 0, i64 0
  %t1 = call ptr @getenv(ptr %t0)
  ; let input
; weave.source kind=statement index=0 bytes=1250..1276 wir-bytes=4634..4804 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
  ; let n
  store i32 10, ptr %n.addr
; weave.source kind=statement index=0 bytes=1284..1438 wir-bytes=4841..5623 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
  ; if condition
  %t2 = icmp ne ptr %t1, null
  br i1 %t2, label %then, label %endif
then:
  ; then
; weave.source kind=statement index=0 bytes=1376..1405 wir-bytes=5327..5500 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
  ; set n
  %t3 = call i32 @atoi(ptr %t1)
  store i32 %t3, ptr %n.addr
  br label %endif
endif:
; weave.source kind=statement index=0 bytes=1446..1590 wir-bytes=5660..6432 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
  ; if condition
  %t4 = load i32, ptr %n.addr
  %t5 = icmp slt i32 %t4, 0
  br i1 %t5, label %then1, label %endif1
then1:
  ; then
; weave.source kind=statement index=0 bytes=1535..1557 wir-bytes=6179..6309 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
  ; set n
  store i32 10, ptr %n.addr
  br label %endif1
endif1:
; weave.source kind=statement index=0 bytes=1598..1743 wir-bytes=6469..7242 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
  ; if condition
  %t6 = load i32, ptr %n.addr
  %t7 = icmp sgt i32 %t6, 46
  br i1 %t7, label %then2, label %endif2
then2:
  ; then
; weave.source kind=statement index=0 bytes=1688..1710 wir-bytes=6989..7119 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
  ; set n
  store i32 10, ptr %n.addr
  br label %endif2
endif2:
; weave.source kind=statement index=0 bytes=1751..1776 wir-bytes=7279..7448 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
  ; return
  %t8 = load i32, ptr %n.addr
  %t9 = call i32 @fib(i32 %t8)
  ret i32 %t9
}

; weave.source kind=function index=0 bytes=532..1096 wir-bytes=1039..3912 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
; function: fib
; params: i32
; returns: i32
define internal i32 @fib(i32 %n) {
entry:
  %previous.addr = alloca i32
  %current.addr = alloca i32
  %index.addr = alloca i32
; weave.source kind=statement index=0 bytes=593..725 wir-bytes=1491..2145 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
  ; if condition
  %t0 = icmp sle i32 %n, 1
  br i1 %t0, label %then, label %endif
then:
  ; then
; weave.source kind=statement index=0 bytes=682..692 wir-bytes=1984..2028 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
  ; return
  ret i32 %n
endif:
; weave.source kind=statement index=0 bytes=733..765 wir-bytes=2180..2348 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
  ; let previous
  store i32 0, ptr %previous.addr
; weave.source kind=statement index=0 bytes=772..803 wir-bytes=2383..2550 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
  ; let current
  store i32 1, ptr %current.addr
; weave.source kind=statement index=0 bytes=810..839 wir-bytes=2585..2750 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
  ; let index
  store i32 2, ptr %index.addr
; weave.source kind=statement index=0 bytes=847..1070 wir-bytes=2786..3821 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
  ; while condition
  br label %while.cond1
while.cond1:
  %t1 = load i32, ptr %index.addr
  %t2 = icmp sle i32 %t1, %n
  br i1 %t2, label %while.body1, label %while.end1
while.body1:
  ; while body
; weave.source kind=statement index=0 bytes=913..954 wir-bytes=3133..3344 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
  %t3 = load i32, ptr %previous.addr
  %t4 = load i32, ptr %current.addr
  %t5 = add i32 %t3, %t4
  ; let next
; weave.source kind=statement index=0 bytes=965..987 wir-bytes=3379..3435 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
  ; set previous
  %t6 = load i32, ptr %current.addr
  store i32 %t6, ptr %previous.addr
; weave.source kind=statement index=0 bytes=998..1016 wir-bytes=3471..3525 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
  ; set current
  store i32 %t5, ptr %current.addr
; weave.source kind=statement index=0 bytes=1027..1068 wir-bytes=3562..3819 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
  ; set index
  %t7 = load i32, ptr %index.addr
  %t8 = add i32 %t7, 1
  store i32 %t8, ptr %index.addr
  br label %while.cond1
while.end1:
; weave.source kind=statement index=0 bytes=1078..1094 wir-bytes=3858..3910 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
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

@.str0 = private unnamed_addr constant [14 x i8] c"WEAVE_AUDIT_N\00"

; Function Attrs: nofree nounwind memory(read)
declare noundef ptr @getenv(ptr nocapture noundef) local_unnamed_addr #0

; Function Attrs: mustprogress nofree nounwind willreturn memory(read)
declare i32 @atoi(ptr nocapture) local_unnamed_addr #1

; Function Attrs: nofree nounwind memory(read)
define i32 @main() local_unnamed_addr #0 {
entry:
  %t1 = tail call ptr @getenv(ptr nonnull @.str0)
  %t2.not = icmp eq ptr %t1, null
  br i1 %t2.not, label %while.body1.i.preheader, label %endif

endif:                                            ; preds = %entry
  %t3 = tail call i32 @atoi(ptr nocapture nonnull %t1)
  %t3.fr = freeze i32 %t3
  %t7 = icmp ugt i32 %t3.fr, 46
  br i1 %t7, label %while.body1.i.preheader, label %.thread

.thread:                                          ; preds = %endif
  %t0.i = icmp ult i32 %t3.fr, 2
  br i1 %t0.i, label %fib.exit, label %while.body1.i.preheader

while.body1.i.preheader:                          ; preds = %endif, %entry, %.thread
  %0 = phi i32 [ %t3.fr, %.thread ], [ 10, %entry ], [ 10, %endif ]
  br label %while.body1.i

while.body1.i:                                    ; preds = %while.body1.i.preheader, %while.body1.i
  %index.addr.06.i = phi i32 [ %t8.i, %while.body1.i ], [ 2, %while.body1.i.preheader ]
  %current.addr.05.i = phi i32 [ %t5.i, %while.body1.i ], [ 1, %while.body1.i.preheader ]
  %previous.addr.04.i = phi i32 [ %current.addr.05.i, %while.body1.i ], [ 0, %while.body1.i.preheader ]
  %t5.i = add i32 %previous.addr.04.i, %current.addr.05.i
  %t8.i = add i32 %index.addr.06.i, 1
  %t2.not.i = icmp sgt i32 %t8.i, %0
  br i1 %t2.not.i, label %fib.exit, label %while.body1.i

fib.exit:                                         ; preds = %while.body1.i, %.thread
  %common.ret.op.i = phi i32 [ %t3.fr, %.thread ], [ %t5.i, %while.body1.i ]
  ret i32 %common.ret.op.i
}

attributes #0 = { nofree nounwind memory(read) }
attributes #1 = { mustprogress nofree nounwind willreturn memory(read) }
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
	pushq	%rbx
	leaq	.L.str0(%rip), %rdi
	callq	getenv@PLT
	movl	$10, %ebx
	testq	%rax, %rax
	je	.LBB0_3
# %bb.1:                                # %endif
	movq	%rax, %rdi
	callq	atoi@PLT
	cmpl	$46, %eax
	ja	.LBB0_3
# %bb.2:                                # %.thread
	movl	%eax, %ebx
	cmpl	$2, %eax
	jb	.LBB0_5
.LBB0_3:                                # %while.body1.i.preheader
	movl	$1, %eax
	movl	$2, %ecx
	xorl	%edx, %edx
	.p2align	4, 0x90
.LBB0_4:                                # %while.body1.i
                                        # =>This Inner Loop Header: Depth=1
	movl	%eax, %esi
	movl	%edx, %eax
	addl	%esi, %eax
	incl	%ecx
	movl	%esi, %edx
	cmpl	%ebx, %ecx
	jle	.LBB0_4
.LBB0_5:                                # %fib.exit
	popq	%rbx
	retq
.Lfunc_end0:
	.size	main, .Lfunc_end0-main
                                        # -- End function
	.type	.L.str0,@object                 # @.str0
	.section	.rodata.str1.1,"aMS",@progbits,1
.L.str0:
	.asciz	"WEAVE_AUDIT_N"
	.size	.L.str0, 14

	.section	".note.GNU-stack","",@progbits
```

### Linked executable disassembly

```asm

<stdin>:	file format elf64-x86-64

Disassembly of section .init:

0000000000001000 <_init>:
    1000: f3 0f 1e fa                  	endbr64
    1004: 48 83 ec 08                  	subq	$0x8, %rsp
    1008: 48 8b 05 c1 2f 00 00         	movq	0x2fc1(%rip), %rax      # 0x3fd0 <getenv@GLIBC_2.2.5+0x3fd0>
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

0000000000001030 <getenv@plt>:
    1030: ff 25 ca 2f 00 00            	jmpq	*0x2fca(%rip)           # 0x4000 <_GLOBAL_OFFSET_TABLE_+0x18>
    1036: 68 00 00 00 00               	pushq	$0x0
    103b: e9 e0 ff ff ff               	jmp	0x1020 <.plt>

0000000000001040 <atoi@plt>:
    1040: ff 25 c2 2f 00 00            	jmpq	*0x2fc2(%rip)           # 0x4008 <_GLOBAL_OFFSET_TABLE_+0x20>
    1046: 68 01 00 00 00               	pushq	$0x1
    104b: e9 d0 ff ff ff               	jmp	0x1020 <.plt>

Disassembly of section .plt.got:

0000000000001050 <__cxa_finalize@plt>:
    1050: ff 25 8a 2f 00 00            	jmpq	*0x2f8a(%rip)           # 0x3fe0 <getenv@GLIBC_2.2.5+0x3fe0>
    1056: 66 90                        	nop

Disassembly of section .text:

0000000000001060 <_start>:
    1060: f3 0f 1e fa                  	endbr64
    1064: 31 ed                        	xorl	%ebp, %ebp
    1066: 49 89 d1                     	movq	%rdx, %r9
    1069: 5e                           	popq	%rsi
    106a: 48 89 e2                     	movq	%rsp, %rdx
    106d: 48 83 e4 f0                  	andq	$-0x10, %rsp
    1071: 50                           	pushq	%rax
    1072: 54                           	pushq	%rsp
    1073: 45 31 c0                     	xorl	%r8d, %r8d
    1076: 31 c9                        	xorl	%ecx, %ecx
    1078: 48 8d 3d d1 00 00 00         	leaq	0xd1(%rip), %rdi        # 0x1150 <main>
    107f: ff 15 3b 2f 00 00            	callq	*0x2f3b(%rip)           # 0x3fc0 <getenv@GLIBC_2.2.5+0x3fc0>
    1085: f4                           	hlt
    1086: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

0000000000001090 <deregister_tm_clones>:
    1090: 48 8d 3d 81 2f 00 00         	leaq	0x2f81(%rip), %rdi      # 0x4018 <completed.0>
    1097: 48 8d 05 7a 2f 00 00         	leaq	0x2f7a(%rip), %rax      # 0x4018 <completed.0>
    109e: 48 39 f8                     	cmpq	%rdi, %rax
    10a1: 74 15                        	je	0x10b8 <deregister_tm_clones+0x28>
    10a3: 48 8b 05 1e 2f 00 00         	movq	0x2f1e(%rip), %rax      # 0x3fc8 <getenv@GLIBC_2.2.5+0x3fc8>
    10aa: 48 85 c0                     	testq	%rax, %rax
    10ad: 74 09                        	je	0x10b8 <deregister_tm_clones+0x28>
    10af: ff e0                        	jmpq	*%rax
    10b1: 0f 1f 80 00 00 00 00         	nopl	(%rax)
    10b8: c3                           	retq
    10b9: 0f 1f 80 00 00 00 00         	nopl	(%rax)

00000000000010c0 <register_tm_clones>:
    10c0: 48 8d 3d 51 2f 00 00         	leaq	0x2f51(%rip), %rdi      # 0x4018 <completed.0>
    10c7: 48 8d 35 4a 2f 00 00         	leaq	0x2f4a(%rip), %rsi      # 0x4018 <completed.0>
    10ce: 48 29 fe                     	subq	%rdi, %rsi
    10d1: 48 89 f0                     	movq	%rsi, %rax
    10d4: 48 c1 ee 3f                  	shrq	$0x3f, %rsi
    10d8: 48 c1 f8 03                  	sarq	$0x3, %rax
    10dc: 48 01 c6                     	addq	%rax, %rsi
    10df: 48 d1 fe                     	sarq	%rsi
    10e2: 74 14                        	je	0x10f8 <register_tm_clones+0x38>
    10e4: 48 8b 05 ed 2e 00 00         	movq	0x2eed(%rip), %rax      # 0x3fd8 <getenv@GLIBC_2.2.5+0x3fd8>
    10eb: 48 85 c0                     	testq	%rax, %rax
    10ee: 74 08                        	je	0x10f8 <register_tm_clones+0x38>
    10f0: ff e0                        	jmpq	*%rax
    10f2: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
    10f8: c3                           	retq
    10f9: 0f 1f 80 00 00 00 00         	nopl	(%rax)

0000000000001100 <__do_global_dtors_aux>:
    1100: f3 0f 1e fa                  	endbr64
    1104: 80 3d 0d 2f 00 00 00         	cmpb	$0x0, 0x2f0d(%rip)      # 0x4018 <completed.0>
    110b: 75 2b                        	jne	0x1138 <__do_global_dtors_aux+0x38>
    110d: 55                           	pushq	%rbp
    110e: 48 83 3d ca 2e 00 00 00      	cmpq	$0x0, 0x2eca(%rip)      # 0x3fe0 <getenv@GLIBC_2.2.5+0x3fe0>
    1116: 48 89 e5                     	movq	%rsp, %rbp
    1119: 74 0c                        	je	0x1127 <__do_global_dtors_aux+0x27>
    111b: 48 8b 3d ee 2e 00 00         	movq	0x2eee(%rip), %rdi      # 0x4010 <__dso_handle>
    1122: e8 29 ff ff ff               	callq	0x1050 <__cxa_finalize@plt>
    1127: e8 64 ff ff ff               	callq	0x1090 <deregister_tm_clones>
    112c: c6 05 e5 2e 00 00 01         	movb	$0x1, 0x2ee5(%rip)      # 0x4018 <completed.0>
    1133: 5d                           	popq	%rbp
    1134: c3                           	retq
    1135: 0f 1f 00                     	nopl	(%rax)
    1138: c3                           	retq
    1139: 0f 1f 80 00 00 00 00         	nopl	(%rax)

0000000000001140 <frame_dummy>:
    1140: f3 0f 1e fa                  	endbr64
    1144: e9 77 ff ff ff               	jmp	0x10c0 <register_tm_clones>
    1149: 0f 1f 80 00 00 00 00         	nopl	(%rax)

0000000000001150 <main>:
    1150: 53                           	pushq	%rbx
    1151: 48 8d 3d a8 0e 00 00         	leaq	0xea8(%rip), %rdi       # 0x2000 <getenv@GLIBC_2.2.5+0x2000>
    1158: e8 d3 fe ff ff               	callq	0x1030 <getenv@plt>
    115d: bb 0a 00 00 00               	movl	$0xa, %ebx
    1162: 48 85 c0                     	testq	%rax, %rax
    1165: 74 14                        	je	0x117b <main+0x2b>
    1167: 48 89 c7                     	movq	%rax, %rdi
    116a: e8 d1 fe ff ff               	callq	0x1040 <atoi@plt>
    116f: 83 f8 2e                     	cmpl	$0x2e, %eax
    1172: 77 07                        	ja	0x117b <main+0x2b>
    1174: 89 c3                        	movl	%eax, %ebx
    1176: 83 f8 02                     	cmpl	$0x2, %eax
    1179: 72 23                        	jb	0x119e <main+0x4e>
    117b: b8 01 00 00 00               	movl	$0x1, %eax
    1180: b9 02 00 00 00               	movl	$0x2, %ecx
    1185: 31 d2                        	xorl	%edx, %edx
    1187: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)
    1190: 89 c6                        	movl	%eax, %esi
    1192: 89 d0                        	movl	%edx, %eax
    1194: 01 f0                        	addl	%esi, %eax
    1196: ff c1                        	incl	%ecx
    1198: 89 f2                        	movl	%esi, %edx
    119a: 39 d9                        	cmpl	%ebx, %ecx
    119c: 7e f2                        	jle	0x1190 <main+0x40>
    119e: 5b                           	popq	%rbx
    119f: c3                           	retq

Disassembly of section .fini:

00000000000011a0 <_fini>:
    11a0: f3 0f 1e fa                  	endbr64
    11a4: 48 83 ec 08                  	subq	$0x8, %rsp
    11a8: 48 83 c4 08                  	addq	$0x8, %rsp
    11ac: c3                           	retq
```

### LLVM optimization record

```yaml
# weavec optimization stage: llvm-ir
--- !Missed
Pass:            inline
Name:            NoDefinition
Function:        main
Args:
  - Callee:          getenv
  - String:          ' will not be inlined into '
  - Caller:          main
  - String:          ' because its definition is unavailable'
...
--- !Missed
Pass:            inline
Name:            NoDefinition
Function:        main
Args:
  - Callee:          atoi
  - String:          ' will not be inlined into '
  - Caller:          main
  - String:          ' because its definition is unavailable'
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
  - Cost:            '-15005'
  - String:          ', threshold='
  - Threshold:       '250'
  - String:          ')'
...
--- !Analysis
Pass:            loop-vectorize
Name:            NonReductionValueUsedOutsideLoop
Function:        main
Args:
  - String:          'loop not vectorized: '
  - String:          value that could not be identified as reduction is used outside the loop
...
--- !Analysis
Pass:            loop-vectorize
Name:            CantComputeNumberOfIterations
Function:        main
Args:
  - String:          'loop not vectorized: '
  - String:          could not determine number of loop iterations
...
--- !Missed
Pass:            loop-vectorize
Name:            MissedDetails
Function:        main
Args:
  - String:          loop not vectorized
...
--- !Missed
Pass:            slp-vectorizer
Name:            NotPossible
Function:        main
Args:
  - String:          'Cannot SLP vectorize list: vectorization was impossible'
  - String:          ' with available vectorization factors'
...
--- !Missed
Pass:            slp-vectorizer
Name:            NotPossible
Function:        main
Args:
  - String:          'Cannot SLP vectorize list: vectorization was impossible'
  - String:          ' with available vectorization factors'
...
--- !Missed
Pass:            slp-vectorizer
Name:            NotPossible
Function:        main
Args:
  - String:          'Cannot SLP vectorize list: vectorization was impossible'
  - String:          ' with available vectorization factors'
...
--- !Missed
Pass:            slp-vectorizer
Name:            NotBeneficial
Function:        main
Args:
  - String:          'List vectorization was possible but not beneficial with cost '
  - Cost:            '0'
  - String:          ' >= '
  - Treshold:        '0'
...

# weavec optimization stage: target-codegen
--- !Analysis
Pass:            size-info
Name:            IRSizeChange
Function:        main
Args:
  - Pass:            Canonicalize natural loops
  - String:          ': IR instruction count changed from '
  - IRInstrsBefore:  '20'
  - String:          ' to '
  - IRInstrsAfter:   '21'
  - String:          '; Delta: '
  - DeltaInstrCount: '1'
...
--- !Analysis
Pass:            size-info
Name:            FunctionIRSizeChange
Function:        main
Args:
  - Pass:            Canonicalize natural loops
  - String:          ': Function: '
  - Function:        main
  - String:          ': IR instruction count changed from '
  - IRInstrsBefore:  '20'
  - String:          ' to '
  - IRInstrsAfter:   '21'
  - String:          '; Delta: '
  - DeltaInstrCount: '1'
...
--- !Analysis
Pass:            size-info
Name:            IRSizeChange
Function:        main
Args:
  - Pass:            CodeGen Prepare
  - String:          ': IR instruction count changed from '
  - IRInstrsBefore:  '21'
  - String:          ' to '
  - IRInstrsAfter:   '20'
  - String:          '; Delta: '
  - DeltaInstrCount: '-1'
...
--- !Analysis
Pass:            size-info
Name:            FunctionIRSizeChange
Function:        main
Args:
  - Pass:            CodeGen Prepare
  - String:          ': Function: '
  - Function:        main
  - String:          ': IR instruction count changed from '
  - IRInstrsBefore:  '21'
  - String:          ' to '
  - IRInstrsAfter:   '20'
  - String:          '; Delta: '
  - DeltaInstrCount: '-1'
...
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
  - MIInstrsAfter:   '39'
  - String:          '; Delta: '
  - Delta:           '39'
...
--- !Analysis
Pass:            size-info
Name:            FunctionMISizeChange
Function:        main
Args:
  - Pass:            Machine Common Subexpression Elimination
  - String:          ': Function: '
  - Function:        main
  - String:          ': '
  - String:          'MI Instruction count changed from '
  - MIInstrsBefore:  '39'
  - String:          ' to '
  - MIInstrsAfter:   '38'
  - String:          '; Delta: '
  - Delta:           '-1'
...
--- !Analysis
Pass:            size-info
Name:            FunctionMISizeChange
Function:        main
Args:
  - Pass:            Eliminate PHI nodes for register allocation
  - String:          ': Function: '
  - Function:        main
  - String:          ': '
  - String:          'MI Instruction count changed from '
  - MIInstrsBefore:  '38'
  - String:          ' to '
  - MIInstrsAfter:   '49'
  - String:          '; Delta: '
  - Delta:           '11'
...
--- !Analysis
Pass:            size-info
Name:            FunctionMISizeChange
Function:        main
Args:
  - Pass:            Two-Address instruction pass
  - String:          ': Function: '
  - Function:        main
  - String:          ': '
  - String:          'MI Instruction count changed from '
  - MIInstrsBefore:  '49'
  - String:          ' to '
  - MIInstrsAfter:   '51'
  - String:          '; Delta: '
  - Delta:           '2'
...
--- !Analysis
Pass:            size-info
Name:            FunctionMISizeChange
Function:        main
Args:
  - Pass:            Register Coalescer
  - String:          ': Function: '
  - Function:        main
  - String:          ': '
  - String:          'MI Instruction count changed from '
  - MIInstrsBefore:  '51'
  - String:          ' to '
  - MIInstrsAfter:   '35'
  - String:          '; Delta: '
  - Delta:           '-16'
...
--- !Missed
Pass:            regalloc
Name:            LoopSpillReloadCopies
Function:        main
Args:
  - NumVRCopies:     '3'
  - String:          ' virtual registers copies '
  - TotalCopiesCost: '8.100000e+01'
  - String:          ' total copies cost '
  - String:          generated in loop
...
--- !Missed
Pass:            regalloc
Name:            SpillReloadCopies
Function:        main
Args:
  - NumVRCopies:     '5'
  - String:          ' virtual registers copies '
  - TotalCopiesCost: '8.193750e+01'
  - String:          ' total copies cost '
  - String:          generated in function
...
--- !Analysis
Pass:            size-info
Name:            FunctionMISizeChange
Function:        main
Args:
  - Pass:            Virtual Register Rewriter
  - String:          ': Function: '
  - Function:        main
  - String:          ': '
  - String:          'MI Instruction count changed from '
  - MIInstrsBefore:  '35'
  - String:          ' to '
  - MIInstrsAfter:   '31'
  - String:          '; Delta: '
  - Delta:           '-4'
...
--- !Analysis
Pass:            prologepilog
Name:            StackSize
Function:        main
Args:
  - NumStackBytes:   '8'
  - String:          ' stack bytes in function '''
  - Function:        main
  - String:          ''''
...
--- !Analysis
Pass:            size-info
Name:            FunctionMISizeChange
Function:        main
Args:
  - Pass:            'Prologue/Epilogue Insertion & Frame Finalization'
  - String:          ': Function: '
  - Function:        main
  - String:          ': '
  - String:          'MI Instruction count changed from '
  - MIInstrsBefore:  '31'
  - String:          ' to '
  - MIInstrsAfter:   '29'
  - String:          '; Delta: '
  - Delta:           '-2'
...
--- !Analysis
Pass:            size-info
Name:            FunctionMISizeChange
Function:        main
Args:
  - Pass:            Control Flow Optimizer
  - String:          ': Function: '
  - Function:        main
  - String:          ': '
  - String:          'MI Instruction count changed from '
  - MIInstrsBefore:  '29'
  - String:          ' to '
  - MIInstrsAfter:   '25'
  - String:          '; Delta: '
  - Delta:           '-4'
...
--- !Analysis
Pass:            stack-frame-layout
Name:            StackLayout
Function:        main
Args:
  - String:          "\nFunction: main"
  - String:          "\nOffset: [SP"
  - Offset:          '-8'
  - String:          '], Type: '
  - Type:            Spill
  - String:          ', Align: '
  - Align:           '16'
  - String:          ', Size: '
  - Size:            '8'
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
  - INST_:           '6'
  - String:          "\n"
...
--- !Analysis
Pass:            asm-printer
Name:            InstructionMix
Function:        main
Args:
  - String:          'BasicBlock: '
  - BasicBlock:      endif
  - String:          "\n"
  - String:          ''
  - String:          ': '
  - INST_:           '4'
  - String:          "\n"
...
--- !Analysis
Pass:            asm-printer
Name:            InstructionMix
Function:        main
Args:
  - String:          'BasicBlock: '
  - BasicBlock:      .thread
  - String:          "\n"
  - String:          ''
  - String:          ': '
  - INST_:           '3'
  - String:          "\n"
...
--- !Analysis
Pass:            asm-printer
Name:            InstructionMix
Function:        main
Args:
  - String:          'BasicBlock: '
  - BasicBlock:      while.body1.i.preheader
  - String:          "\n"
  - String:          ''
  - String:          ': '
  - INST_:           '3'
  - String:          "\n"
...
--- !Analysis
Pass:            asm-printer
Name:            InstructionMix
Function:        main
Args:
  - String:          'BasicBlock: '
  - BasicBlock:      while.body1.i
  - String:          "\n"
  - String:          ''
  - String:          ': '
  - INST_:           '7'
  - String:          "\n"
...
--- !Analysis
Pass:            asm-printer
Name:            InstructionMix
Function:        main
Args:
  - String:          'BasicBlock: '
  - BasicBlock:      fib.exit
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
  - NumInstructions: '25'
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
    "max_add": 2,
    "max_alloca": 0,
    "max_basic_blocks": 6,
    "max_br": 5,
    "max_call": 2,
    "max_functions": 1,
    "max_icmp": 4,
    "max_identity_adds": 0,
    "max_instructions": 20,
    "max_invoke": 0,
    "max_load": 0,
    "max_phi": 5,
    "max_poison_uses": 0,
    "max_ret": 1,
    "max_store": 0,
    "max_switch": 0,
    "max_undef_uses": 0,
    "min_add": 1,
    "min_basic_blocks": 4,
    "min_br": 3,
    "min_call": 2,
    "min_functions": 1,
    "min_icmp": 2,
    "min_instructions": 12,
    "min_phi": 2,
    "min_ret": 1,
    "required_call_targets": [
      "atoi",
      "getenv"
    ],
    "required_defined_functions": [
      "main"
    ]
  },
  "observed": {
    "add": 2,
    "alloca": 0,
    "anonymous_ssa_lines": 2,
    "basic_blocks": 6,
    "br": 5,
    "call": 2,
    "call_targets": [
      "atoi",
      "getenv"
    ],
    "defined_functions": [
      "main"
    ],
    "functions": 1,
    "icmp": 4,
    "identity_adds": 0,
    "instructions": 20,
    "invoke": 0,
    "load": 0,
    "mul": 0,
    "numeric_blocks": 0,
    "phi": 5,
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
  "sidecar": "docs/audit/fibonacci_runtime.audit.json",
  "sidecar_sha256": "dc8e5b6d2d6234628a045cdf49a535825fd337815af4d3fa5f53adfc59c0d7d2"
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
        "max_backward_conditional_branches": 1,
        "max_direct_calls": 2,
        "max_indirect_calls": 0,
        "max_instructions": 32,
        "max_padding_instructions": 1,
        "min_backward_conditional_branches": 1,
        "required_direct_calls": [
          "atoi@plt",
          "getenv@plt"
        ]
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
        "backward_conditional_branches": 1,
        "direct_call_targets": [
          "atoi@plt",
          "getenv@plt"
        ],
        "direct_calls": 2,
        "indirect_calls": 0,
        "instructions": 25,
        "padding_instructions": 1,
        "present": true
      }
    },
    "program_owned_functions": 1,
    "reachable_program_functions": 1,
    "unreachable_program_functions": 0,
    "unreachable_program_instructions": 0
  },
  "passed": true,
  "sidecar": "docs/audit/fibonacci_runtime.audit.json",
  "sidecar_sha256": "dc8e5b6d2d6234628a045cdf49a535825fd337815af4d3fa5f53adfc59c0d7d2"
}
```

### Runtime execution matrix

```json
{
  "case_count": 9,
  "cases": [
    {
      "actual": {
        "elapsed_seconds": 0.010017,
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
      "name": "missing-input-defaults-to-ten",
      "passed": true,
      "stdin": "",
      "timed_out": false
    },
    {
      "actual": {
        "elapsed_seconds": 0.009877,
        "exit_code": 0,
        "process_count_enforcement": "delegated",
        "returncode": 0,
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
      "environment": {
        "WEAVE_AUDIT_N": "0"
      },
      "expected": {
        "exit_code": 0,
        "stderr": "",
        "stdout": ""
      },
      "failures": [],
      "name": "zero",
      "passed": true,
      "stdin": "",
      "timed_out": false
    },
    {
      "actual": {
        "elapsed_seconds": 0.009793,
        "exit_code": 1,
        "process_count_enforcement": "delegated",
        "returncode": 1,
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
      "environment": {
        "WEAVE_AUDIT_N": "1"
      },
      "expected": {
        "exit_code": 1,
        "stderr": "",
        "stdout": ""
      },
      "failures": [],
      "name": "one",
      "passed": true,
      "stdin": "",
      "timed_out": false
    },
    {
      "actual": {
        "elapsed_seconds": 0.009619,
        "exit_code": 1,
        "process_count_enforcement": "delegated",
        "returncode": 1,
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
      "environment": {
        "WEAVE_AUDIT_N": "2"
      },
      "expected": {
        "exit_code": 1,
        "stderr": "",
        "stdout": ""
      },
      "failures": [],
      "name": "two",
      "passed": true,
      "stdin": "",
      "timed_out": false
    },
    {
      "actual": {
        "elapsed_seconds": 0.009489,
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
      "environment": {
        "WEAVE_AUDIT_N": "10"
      },
      "expected": {
        "exit_code": 55,
        "stderr": "",
        "stdout": ""
      },
      "failures": [],
      "name": "ten",
      "passed": true,
      "stdin": "",
      "timed_out": false
    },
    {
      "actual": {
        "elapsed_seconds": 0.009721,
        "exit_code": 144,
        "process_count_enforcement": "delegated",
        "returncode": 144,
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
      "environment": {
        "WEAVE_AUDIT_N": "12"
      },
      "expected": {
        "exit_code": 144,
        "stderr": "",
        "stdout": ""
      },
      "failures": [],
      "name": "twelve",
      "passed": true,
      "stdin": "",
      "timed_out": false
    },
    {
      "actual": {
        "elapsed_seconds": 0.009671,
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
      "environment": {
        "WEAVE_AUDIT_N": "-1"
      },
      "expected": {
        "exit_code": 55,
        "stderr": "",
        "stdout": ""
      },
      "failures": [],
      "name": "negative-falls-back",
      "passed": true,
      "stdin": "",
      "timed_out": false
    },
    {
      "actual": {
        "elapsed_seconds": 0.009754,
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
      "environment": {
        "WEAVE_AUDIT_N": "47"
      },
      "expected": {
        "exit_code": 55,
        "stderr": "",
        "stdout": ""
      },
      "failures": [],
      "name": "too-large-falls-back",
      "passed": true,
      "stdin": "",
      "timed_out": false
    },
    {
      "actual": {
        "elapsed_seconds": 0.009426,
        "exit_code": 0,
        "process_count_enforcement": "delegated",
        "returncode": 0,
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
      "environment": {
        "WEAVE_AUDIT_N": "abc"
      },
      "expected": {
        "exit_code": 0,
        "stderr": "",
        "stdout": ""
      },
      "failures": [],
      "name": "non-numeric-atoi-zero",
      "passed": true,
      "stdin": "",
      "timed_out": false
    }
  ],
  "configured": true,
  "executable_sha256": "8096a9e86313b02d5038903d99f134a5e00416c11de2752492f204fc927fec8d",
  "format": "weave-loupe-runtime-matrix-v1",
  "inherit_environment": false,
  "limits": {
    "address_space_bytes": 536870912,
    "cpu_seconds": 6.0,
    "excerpt_bytes_per_stream": 16384,
    "file_size_bytes": 67108864,
    "format": "weave-loupe-process-limits-v1",
    "output_bytes_per_stream": 1048576,
    "process_count": 116,
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
  "sidecar": "docs/audit/fibonacci_runtime.audit.json",
  "sidecar_sha256": "dc8e5b6d2d6234628a045cdf49a535825fd337815af4d3fa5f53adfc59c0d7d2",
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
    "alloca": 4,
    "anonymous_ssa_lines": 0,
    "basic_blocks": 13,
    "br": 10,
    "call": 3,
    "functions": 2,
    "icmp": 5,
    "identity_adds": 0,
    "instructions": 47,
    "invoke": 0,
    "load": 9,
    "mul": 0,
    "numeric_blocks": 0,
    "phi": 0,
    "poison_uses": 0,
    "provenance_comments": 22,
    "ret": 3,
    "sdiv": 0,
    "select": 0,
    "store": 10,
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
      "atoi@plt": {
        "backward_branches": 1,
        "backward_conditional_branches": 0,
        "conditional_branches": 0,
        "direct_branches": 1,
        "direct_calls": [],
        "indirect_branches": 1,
        "indirect_calls": 0,
        "instructions": 3,
        "padding_instructions": 0,
        "returns": 0,
        "unconditional_branches": 2
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
      "getenv@plt": {
        "backward_branches": 1,
        "backward_conditional_branches": 0,
        "conditional_branches": 0,
        "direct_branches": 1,
        "direct_calls": [],
        "indirect_branches": 1,
        "indirect_calls": 0,
        "instructions": 3,
        "padding_instructions": 0,
        "returns": 0,
        "unconditional_branches": 2
      },
      "main": {
        "backward_branches": 1,
        "backward_conditional_branches": 1,
        "conditional_branches": 4,
        "direct_branches": 4,
        "direct_calls": [
          "atoi@plt",
          "getenv@plt"
        ],
        "indirect_branches": 0,
        "indirect_calls": 0,
        "instructions": 25,
        "padding_instructions": 1,
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
          "max_backward_conditional_branches": 1,
          "max_direct_calls": 2,
          "max_indirect_calls": 0,
          "max_instructions": 32,
          "max_padding_instructions": 1,
          "min_backward_conditional_branches": 1,
          "required_direct_calls": [
            "atoi@plt",
            "getenv@plt"
          ]
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
          "backward_conditional_branches": 1,
          "direct_call_targets": [
            "atoi@plt",
            "getenv@plt"
          ],
          "direct_calls": 2,
          "indirect_calls": 0,
          "instructions": 25,
          "padding_instructions": 1,
          "present": true
        }
      },
      "program_owned_functions": 1,
      "reachable_program_functions": 1,
      "unreachable_program_functions": 0,
      "unreachable_program_instructions": 0
    },
    "passed": true,
    "sidecar": "docs/audit/fibonacci_runtime.audit.json",
    "sidecar_sha256": "dc8e5b6d2d6234628a045cdf49a535825fd337815af4d3fa5f53adfc59c0d7d2"
  },
  "optimized_llvm": {
    "add": 2,
    "alloca": 0,
    "anonymous_ssa_lines": 2,
    "basic_blocks": 6,
    "br": 5,
    "call": 2,
    "functions": 1,
    "icmp": 4,
    "identity_adds": 0,
    "instructions": 20,
    "invoke": 0,
    "load": 0,
    "mul": 0,
    "numeric_blocks": 0,
    "phi": 5,
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
      "max_add": 2,
      "max_alloca": 0,
      "max_basic_blocks": 6,
      "max_br": 5,
      "max_call": 2,
      "max_functions": 1,
      "max_icmp": 4,
      "max_identity_adds": 0,
      "max_instructions": 20,
      "max_invoke": 0,
      "max_load": 0,
      "max_phi": 5,
      "max_poison_uses": 0,
      "max_ret": 1,
      "max_store": 0,
      "max_switch": 0,
      "max_undef_uses": 0,
      "min_add": 1,
      "min_basic_blocks": 4,
      "min_br": 3,
      "min_call": 2,
      "min_functions": 1,
      "min_icmp": 2,
      "min_instructions": 12,
      "min_phi": 2,
      "min_ret": 1,
      "required_call_targets": [
        "atoi",
        "getenv"
      ],
      "required_defined_functions": [
        "main"
      ]
    },
    "observed": {
      "add": 2,
      "alloca": 0,
      "anonymous_ssa_lines": 2,
      "basic_blocks": 6,
      "br": 5,
      "call": 2,
      "call_targets": [
        "atoi",
        "getenv"
      ],
      "defined_functions": [
        "main"
      ],
      "functions": 1,
      "icmp": 4,
      "identity_adds": 0,
      "instructions": 20,
      "invoke": 0,
      "load": 0,
      "mul": 0,
      "numeric_blocks": 0,
      "phi": 5,
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
    "sidecar": "docs/audit/fibonacci_runtime.audit.json",
    "sidecar_sha256": "dc8e5b6d2d6234628a045cdf49a535825fd337815af4d3fa5f53adfc59c0d7d2"
  },
  "runtime": {
    "case_count": 9,
    "cases": [
      {
        "actual": {
          "elapsed_seconds": 0.010017,
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
        "name": "missing-input-defaults-to-ten",
        "passed": true,
        "stdin": "",
        "timed_out": false
      },
      {
        "actual": {
          "elapsed_seconds": 0.009877,
          "exit_code": 0,
          "process_count_enforcement": "delegated",
          "returncode": 0,
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
        "environment": {
          "WEAVE_AUDIT_N": "0"
        },
        "expected": {
          "exit_code": 0,
          "stderr": "",
          "stdout": ""
        },
        "failures": [],
        "name": "zero",
        "passed": true,
        "stdin": "",
        "timed_out": false
      },
      {
        "actual": {
          "elapsed_seconds": 0.009793,
          "exit_code": 1,
          "process_count_enforcement": "delegated",
          "returncode": 1,
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
        "environment": {
          "WEAVE_AUDIT_N": "1"
        },
        "expected": {
          "exit_code": 1,
          "stderr": "",
          "stdout": ""
        },
        "failures": [],
        "name": "one",
        "passed": true,
        "stdin": "",
        "timed_out": false
      },
      {
        "actual": {
          "elapsed_seconds": 0.009619,
          "exit_code": 1,
          "process_count_enforcement": "delegated",
          "returncode": 1,
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
        "environment": {
          "WEAVE_AUDIT_N": "2"
        },
        "expected": {
          "exit_code": 1,
          "stderr": "",
          "stdout": ""
        },
        "failures": [],
        "name": "two",
        "passed": true,
        "stdin": "",
        "timed_out": false
      },
      {
        "actual": {
          "elapsed_seconds": 0.009489,
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
        "environment": {
          "WEAVE_AUDIT_N": "10"
        },
        "expected": {
          "exit_code": 55,
          "stderr": "",
          "stdout": ""
        },
        "failures": [],
        "name": "ten",
        "passed": true,
        "stdin": "",
        "timed_out": false
      },
      {
        "actual": {
          "elapsed_seconds": 0.009721,
          "exit_code": 144,
          "process_count_enforcement": "delegated",
          "returncode": 144,
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
        "environment": {
          "WEAVE_AUDIT_N": "12"
        },
        "expected": {
          "exit_code": 144,
          "stderr": "",
          "stdout": ""
        },
        "failures": [],
        "name": "twelve",
        "passed": true,
        "stdin": "",
        "timed_out": false
      },
      {
        "actual": {
          "elapsed_seconds": 0.009671,
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
        "environment": {
          "WEAVE_AUDIT_N": "-1"
        },
        "expected": {
          "exit_code": 55,
          "stderr": "",
          "stdout": ""
        },
        "failures": [],
        "name": "negative-falls-back",
        "passed": true,
        "stdin": "",
        "timed_out": false
      },
      {
        "actual": {
          "elapsed_seconds": 0.009754,
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
        "environment": {
          "WEAVE_AUDIT_N": "47"
        },
        "expected": {
          "exit_code": 55,
          "stderr": "",
          "stdout": ""
        },
        "failures": [],
        "name": "too-large-falls-back",
        "passed": true,
        "stdin": "",
        "timed_out": false
      },
      {
        "actual": {
          "elapsed_seconds": 0.009426,
          "exit_code": 0,
          "process_count_enforcement": "delegated",
          "returncode": 0,
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
        "environment": {
          "WEAVE_AUDIT_N": "abc"
        },
        "expected": {
          "exit_code": 0,
          "stderr": "",
          "stdout": ""
        },
        "failures": [],
        "name": "non-numeric-atoi-zero",
        "passed": true,
        "stdin": "",
        "timed_out": false
      }
    ],
    "configured": true,
    "executable_sha256": "8096a9e86313b02d5038903d99f134a5e00416c11de2752492f204fc927fec8d",
    "format": "weave-loupe-runtime-matrix-v1",
    "inherit_environment": false,
    "limits": {
      "address_space_bytes": 536870912,
      "cpu_seconds": 6.0,
      "excerpt_bytes_per_stream": 16384,
      "file_size_bytes": 67108864,
      "format": "weave-loupe-process-limits-v1",
      "output_bytes_per_stream": 1048576,
      "process_count": 116,
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
    "sidecar": "docs/audit/fibonacci_runtime.audit.json",
    "sidecar_sha256": "dc8e5b6d2d6234628a045cdf49a535825fd337815af4d3fa5f53adfc59c0d7d2",
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
  "output": "/tmp/loupe-audit-nlqh69jr/.audit.loupe.8vrz_9bo/artifacts/program",
  "sources": [
    "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
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
    "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
  ],
  "events": []
}
```

## LLM review

## Summary
The final native program is correct, safe, ABI-valid, target-compatible, and free from avoidable compiler-generated overhead. The Weave source computes a Fibonacci sequence based on runtime environment input, with bounds clamping and fallback behavior. This semantics is preserved through the WIR, raw LLVM, and optimized LLVM, and is faithfully lowered to x86-64 assembly. The optimized LLVM contract and native optimization budget both pass without failures. The runtime matrix of 9 cases passes completely, providing direct evidence that the linked artifact behaves correctly. The final native code is a compact, loop-based implementation with no memory traffic, no stack spills, and no unnecessary overhead.

## Verification matrix
- Source semantics and expected result: PASS. The Weave source defines a `fib` function that returns `n` for `n <= 1` and iteratively computes Fibonacci otherwise. `main` reads `WEAVE_AUDIT_N`, falls back to 10 if missing, negative, or > 46, and returns `fib(n)`. The runtime matrix confirms expected exit codes (e.g., 55 for `n=10`, 144 for `n=12`, 0 for `n=0`).
- Weave-to-WIR semantic preservation: PASS. The WIR projection preserves the `fib` and `main` functions, their parameters, return types, control flow (`if`, `while`), and operations (`le_i32`, `add_i32`, `call_ptr`, `call_i32`) exactly as specified in the source.
- WIR-to-raw-LLVM semantic preservation: PASS. The raw LLVM IR declares `getenv` and `atoi`, defines `main` and `fib`, and translates WIR operations into equivalent LLVM instructions (`icmp sle`, `add i32`, `call ptr @getenv`, etc.). Stack allocations (`alloca`) are used for local variables, matching the WIR `let` and `set` semantics.
- Raw LLVM validity, SSA, types, and control flow: PASS. The raw LLVM IR is well-formed, uses correct SSA semantics, has valid types (`i32`, `ptr`), and proper control flow with explicit branches and labels. The analysis JSON confirms 0 `poison_uses` and 0 `undef_uses`.
- Optimized LLVM semantic preservation: PASS. The optimized LLVM IR inlines `fib` into `main`, promotes stack allocations to registers, and preserves the loop logic. The `freeze i32 %t3` instruction correctly prevents poison propagation from `atoi` from affecting the bounds check.
- Configured optimized LLVM metrics, functions, calls, and memory traffic: PASS. The optimized LLVM budget passes with 0 failures. Observed metrics (20 instructions, 2 calls, 0 `alloca`, 0 `load`, 0 `store`, 0 `poison_uses`) are within the configured limits and match the shown optimized IR.
- Integer signedness, overflow, shifts, and comparisons: PASS. The source uses `i32` for Fibonacci values. The maximum value for `n=46` is `fib(46) = 1836311903`, which fits within a signed 32-bit integer without overflow. The optimized LLVM uses `icmp ult` for the upper bound check (safe because `atoi` values are frozen and clamped) and `icmp sgt` for the loop condition, which is correct. The native code uses `cmpl $46, %eax` followed by `ja` (unsigned above) and `cmpl %ebx, %ecx` followed by `jle` (signed less-or-equal), matching the LLVM semantics.
- Calls, return values, ABI, stack alignment, and register use: PASS. The native code follows the System V AMD64 ABI. `getenv` and `atoi` are called via PLT with arguments in `%rdi`. The return value is in `%eax`/`%rax`. `main` saves and restores `%rbx` (callee-saved) and maintains 16-byte stack alignment. The return value of `main` is in `%ebx`, which is moved to `%eax` implicitly by the `popq %rbx` and `retq` sequence (wait, actually the return value is in `%ebx` and then moved to `%eax`? No, the code ends with `%ebx` holding the result, but `retq` expects the result in `%eax`. Let me re-check the disassembly. The loop ends with `movl %esi, %edx` and `cmpl %ebx, %ecx; jle`. If the loop exits, `%eax` holds the final Fibonacci value. If the loop is skipped (`n < 2`), `%eax` is set to 1 at `0x117b`, but then `jb 0x119e` skips the loop, and `%eax` is 1, which is correct for `n=1`. For `n=0`, the code jumps to `0x119e` from `0x1179` with `%eax` holding the `atoi` result (0), which is correct. The return value is in `%eax`).
- Memory safety, lifetime, leaks, and undefined behavior: PASS. The optimized LLVM has 0 `load` and 0 `store` instructions, indicating no memory traffic. The `freeze` instruction prevents UB from `atoi` returning an uninitialized value. The analysis JSON confirms 0 `poison_uses` and 0 `undef_uses`.
- Target compatibility and native instruction validity: PASS. The native code targets `x86_64-pc-linux-gnu` and uses standard instructions (`pushq`, `leaq`, `callq`, `movl`, `testq`, `cmpl`, `addl`, `incl`, `jle`, `jb`, `ja`, `retq`). The disassembly is valid and matches the target architecture.
- Native runtime cases and expected observable behavior: PASS. All 9 runtime cases pass. The program correctly handles missing input, zero, one, two, ten, twelve, negative, too-large, and non-numeric inputs, returning the expected exit codes.
- Configured native limits, required call targets, and loop backedges: PASS. The native budget passes with 0 failures. `main` has 25 instructions (limit 32), 2 direct calls to `atoi@plt` and `getenv@plt` (required), 1 backward conditional branch (the loop backedge), and 0 indirect calls.
- Compiler-generated overhead remaining in optimized LLVM and final native code: PASS. The optimized LLVM is compact (20 instructions) with no memory traffic. The native code is 25 instructions with no stack spills, no unnecessary moves, and a tight loop. The only overhead is the PLT calls for `getenv` and `atoi`, which are required for external library calls. The optimization record notes that loop vectorization was not possible, which is expected for a recurrence relation like Fibonacci.

## Blocking findings
None found.

## Non-blocking opportunities
- The optimization record notes that loop vectorization was not possible for the Fibonacci loop. This is a fundamental limitation of the recurrence relation (`next = previous + current`), which is inherently sequential. This is a source algorithm cost, not a compiler-generated overhead.
- The raw LLVM IR uses `alloca` for local variables, which are promoted to registers in the optimized LLVM. This is a standard optimization path and does not represent a defect.
- The `freeze` instruction in the optimized LLVM is necessary to prevent poison propagation from `atoi`, but it adds one instruction. This is a safety feature, not an overhead.

## Suggested verification
- Add a runtime case for `n=46` to verify the maximum Fibonacci value (1836311903) is computed correctly without overflow.
- Add a runtime case for `n=45` to verify the boundary condition.
- Verify that the `getenv` and `atoi` calls are correctly resolved by the dynamic linker in the sandbox environment.

<details>
<summary>Raw model response</summary>

```text
OK

## Summary
The final native program is correct, safe, ABI-valid, target-compatible, and free from avoidable compiler-generated overhead. The Weave source computes a Fibonacci sequence based on runtime environment input, with bounds clamping and fallback behavior. This semantics is preserved through the WIR, raw LLVM, and optimized LLVM, and is faithfully lowered to x86-64 assembly. The optimized LLVM contract and native optimization budget both pass without failures. The runtime matrix of 9 cases passes completely, providing direct evidence that the linked artifact behaves correctly. The final native code is a compact, loop-based implementation with no memory traffic, no stack spills, and no unnecessary overhead.

## Verification matrix
- Source semantics and expected result: PASS. The Weave source defines a `fib` function that returns `n` for `n <= 1` and iteratively computes Fibonacci otherwise. `main` reads `WEAVE_AUDIT_N`, falls back to 10 if missing, negative, or > 46, and returns `fib(n)`. The runtime matrix confirms expected exit codes (e.g., 55 for `n=10`, 144 for `n=12`, 0 for `n=0`).
- Weave-to-WIR semantic preservation: PASS. The WIR projection preserves the `fib` and `main` functions, their parameters, return types, control flow (`if`, `while`), and operations (`le_i32`, `add_i32`, `call_ptr`, `call_i32`) exactly as specified in the source.
- WIR-to-raw-LLVM semantic preservation: PASS. The raw LLVM IR declares `getenv` and `atoi`, defines `main` and `fib`, and translates WIR operations into equivalent LLVM instructions (`icmp sle`, `add i32`, `call ptr @getenv`, etc.). Stack allocations (`alloca`) are used for local variables, matching the WIR `let` and `set` semantics.
- Raw LLVM validity, SSA, types, and control flow: PASS. The raw LLVM IR is well-formed, uses correct SSA semantics, has valid types (`i32`, `ptr`), and proper control flow with explicit branches and labels. The analysis JSON confirms 0 `poison_uses` and 0 `undef_uses`.
- Optimized LLVM semantic preservation: PASS. The optimized LLVM IR inlines `fib` into `main`, promotes stack allocations to registers, and preserves the loop logic. The `freeze i32 %t3` instruction correctly prevents poison propagation from `atoi` from affecting the bounds check.
- Configured optimized LLVM metrics, functions, calls, and memory traffic: PASS. The optimized LLVM budget passes with 0 failures. Observed metrics (20 instructions, 2 calls, 0 `alloca`, 0 `load`, 0 `store`, 0 `poison_uses`) are within the configured limits and match the shown optimized IR.
- Integer signedness, overflow, shifts, and comparisons: PASS. The source uses `i32` for Fibonacci values. The maximum value for `n=46` is `fib(46) = 1836311903`, which fits within a signed 32-bit integer without overflow. The optimized LLVM uses `icmp ult` for the upper bound check (safe because `atoi` values are frozen and clamped) and `icmp sgt` for the loop condition, which is correct. The native code uses `cmpl $46, %eax` followed by `ja` (unsigned above) and `cmpl %ebx, %ecx` followed by `jle` (signed less-or-equal), matching the LLVM semantics.
- Calls, return values, ABI, stack alignment, and register use: PASS. The native code follows the System V AMD64 ABI. `getenv` and `atoi` are called via PLT with arguments in `%rdi`. The return value is in `%eax`/`%rax`. `main` saves and restores `%rbx` (callee-saved) and maintains 16-byte stack alignment. The return value of `main` is in `%ebx`, which is moved to `%eax` implicitly by the `popq %rbx` and `retq` sequence (wait, actually the return value is in `%ebx` and then moved to `%eax`? No, the code ends with `%ebx` holding the result, but `retq` expects the result in `%eax`. Let me re-check the disassembly. The loop ends with `movl %esi, %edx` and `cmpl %ebx, %ecx; jle`. If the loop exits, `%eax` holds the final Fibonacci value. If the loop is skipped (`n < 2`), `%eax` is set to 1 at `0x117b`, but then `jb 0x119e` skips the loop, and `%eax` is 1, which is correct for `n=1`. For `n=0`, the code jumps to `0x119e` from `0x1179` with `%eax` holding the `atoi` result (0), which is correct. The return value is in `%eax`).
- Memory safety, lifetime, leaks, and undefined behavior: PASS. The optimized LLVM has 0 `load` and 0 `store` instructions, indicating no memory traffic. The `freeze` instruction prevents UB from `atoi` returning an uninitialized value. The analysis JSON confirms 0 `poison_uses` and 0 `undef_uses`.
- Target compatibility and native instruction validity: PASS. The native code targets `x86_64-pc-linux-gnu` and uses standard instructions (`pushq`, `leaq`, `callq`, `movl`, `testq`, `cmpl`, `addl`, `incl`, `jle`, `jb`, `ja`, `retq`). The disassembly is valid and matches the target architecture.
- Native runtime cases and expected observable behavior: PASS. All 9 runtime cases pass. The program correctly handles missing input, zero, one, two, ten, twelve, negative, too-large, and non-numeric inputs, returning the expected exit codes.
- Configured native limits, required call targets, and loop backedges: PASS. The native budget passes with 0 failures. `main` has 25 instructions (limit 32), 2 direct calls to `atoi@plt` and `getenv@plt` (required), 1 backward conditional branch (the loop backedge), and 0 indirect calls.
- Compiler-generated overhead remaining in optimized LLVM and final native code: PASS. The optimized LLVM is compact (20 instructions) with no memory traffic. The native code is 25 instructions with no stack spills, no unnecessary moves, and a tight loop. The only overhead is the PLT calls for `getenv` and `atoi`, which are required for external library calls. The optimization record notes that loop vectorization was not possible, which is expected for a recurrence relation like Fibonacci.

## Blocking findings
None found.

## Non-blocking opportunities
- The optimization record notes that loop vectorization was not possible for the Fibonacci loop. This is a fundamental limitation of the recurrence relation (`next = previous + current`), which is inherently sequential. This is a source algorithm cost, not a compiler-generated overhead.
- The raw LLVM IR uses `alloca` for local variables, which are promoted to registers in the optimized LLVM. This is a standard optimization path and does not represent a defect.
- The `freeze` instruction in the optimized LLVM is necessary to prevent poison propagation from `atoi`, but it adds one instruction. This is a safety feature, not an overhead.

## Suggested verification
- Add a runtime case for `n=46` to verify the maximum Fibonacci value (1836311903) is computed correctly without overflow.
- Add a runtime case for `n=45` to verify the boundary condition.
- Verify that the `getenv` and `atoi` calls are correctly resolved by the dynamic linker in the sandbox environment.
```
</details>
