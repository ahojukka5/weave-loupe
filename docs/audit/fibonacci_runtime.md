# Weave Loupe Audit Report

## Verdict

- **Status:** OK
- **Code:** none
- **Reason:** No blocking defect found.

## Reproducibility

- **Report content SHA-256:** `c8b34bce4bbe8501abdbe0f33f6dba50561fd4488779dc24f38cb3eccb9752aa`
- **Audit timestamp (UTC):** `2026-07-31T16:09:45+00:00`
- **Re-audit no later than (UTC):** `2026-08-30T16:09:45+00:00`
- **Maximum audit age:** `30` days
- **Audited input invalidation:** `any source or runtime matrix hash change`
- **Compiler binary invalidation:** `any compiler binary hash change`
- **Auditor invalidation:** `any audit implementation fingerprint change`
- **Model invalidation:** `any configured LLM model or endpoint change`
- **Request limit invalidation:** `any configured LLM max-token change`
- **Development compiler invalidation:** `any compiler version change`
- **Identity attestation upgrade:** `required when command identity becomes available`
- **Audited source Git SHA:** `a177f1a19dcfe90f16a64d49109ae23236131203`
- **Source tree state:** `clean`
- **Weave Loupe Git SHA:** `a177f1a19dcfe90f16a64d49109ae23236131203`
- **Auditor content SHA-256:** `25d12000d9a3bbecec23e741728e9ba052d8b59e513496506be72c784c76660c`
- **weavec Git SHA:** `05368ac8733928bdceb27f333881094f167decd3`
- **weavec binary SHA-256:** `ad08fea62fec184941dfdf5d0c77b22ccbac9597cfa1c598c594acbb37cc29cb`
- **weavec version:** `weavec v0.3.0+git.05368ac87339`
- **weavec build kind:** `development`
- **weavec version source:** `command`
- **LLM endpoint:** `https://integrate.api.nvidia.com/v1`
- **LLM model:** `z-ai/glm-5.2`
- **LLM max tokens:** `4096`
- **LLM temperature:** `0.0`
- **LLM prompt SHA-256:** `0214705ef015a92ea22447b9815cdf142ffea9cf2727038b1f2c2ce50d5d84ab`
- **LLM request SHA-256:** `56022440d31d973eff123fc603391b1be82d6d16ce90e9b92cb307ba50949c5a`
- **Provider-reported model:** `z-ai/glm-5.2`
- **Provider response ID:** `chatcmpl-4dcccd74-00e4-4671-8a34-87c442e80d28`
- **Provider system fingerprint:** `unavailable`
- **Provider finish reason:** `stop`
- **Provider created (Unix):** `1785514193`
- **Provider prompt tokens:** `19421`
- **Provider completion tokens:** `1329`
- **Provider total tokens:** `20750`
- **GitHub run ID:** `30645885093`
- **GitHub workflow SHA:** `d0d9cfb17fd961922121e71b8bef0ca53ecae1b1`

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

- Source `docs/audit/fibonacci_runtime.weave` — SHA-256 `a0df013d2e54ac1426498c7fda686d113ae4ca4f7371fe3836c490ccf9343ba4`
- Runtime matrix `docs/audit/fibonacci_runtime.audit.json` — SHA-256 `79cca05fe96a1cb52dfba6fb0d47b1f1ba44196ca11a4b6319d0619a08eb1ede`

## Captured evidence

- `assembly` — SHA-256 `355551c6d11759a2137d794f6154bee9f187aff00d09f7f13887d82a052f3bf1`
- `build_manifest` — SHA-256 `3055dd81fbe7409f4de35afe0ba0a47fd33233844fceb689c2308a613c9ddb8a`
- `diagnostics` — SHA-256 `a40b573053cda943c381742ad672108b1c8985ecc97e2f21dfa604094e31ff63`
- `disassembly` — SHA-256 `fc79aff611b518050aabf8fba9f4e4d9206bbb333c222fa01363938355cb582a`
- `executable` — SHA-256 `8096a9e86313b02d5038903d99f134a5e00416c11de2752492f204fc927fec8d`
- `llvm` — SHA-256 `5966e6216c6d4e680533752eb6968cac27dea9f47aebcd6fa7ea6cff5a0a1270`
- `optimization_record` — SHA-256 `c1eed531ffbbd0e9d7c3558ecea6e951283dcb7e51ce4ebf7c1144aa66d37c6d`
- `optimized_llvm` — SHA-256 `7bda6a3ae32ec72bf1ac4f39971bba88d5f34fff09f56798c9cdbbf76414598e`
- `trace` — SHA-256 `74f29e7980500aae038a421b7f50c70b9b9fedbb0bfa84905f01b67e9e9e52d4`
- `wir` — SHA-256 `b445fa2581f956373545ab1445c95bbff55703e82fd7d0fc7bd0f53645e3a697`

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
; source: /tmp/weavec-build-ItBnTf/program.wir
; core-version: 2

; declarations

declare ptr @getenv(ptr)
declare i32 @atoi(ptr)

; string literals

@.str0 = private unnamed_addr constant [14 x i8] c"WEAVE_AUDIT_N\00"

; weave.source kind=function index=0 bytes=1100..1778 wir-bytes=3911..7408 path="docs/audit/fibonacci_runtime.weave"
; function: main
; params: none
; returns: i32
define i32 @main() {
entry:
  %n.addr = alloca i32
; weave.source kind=statement index=0 bytes=1157..1243 wir-bytes=4235..4555 path="docs/audit/fibonacci_runtime.weave"
  %t0 = getelementptr [14 x i8], ptr @.str0, i64 0, i64 0
  %t1 = call ptr @getenv(ptr %t0)
  ; let input
; weave.source kind=statement index=0 bytes=1250..1276 wir-bytes=4592..4762 path="docs/audit/fibonacci_runtime.weave"
  ; let n
  store i32 10, ptr %n.addr
; weave.source kind=statement index=0 bytes=1284..1438 wir-bytes=4799..5581 path="docs/audit/fibonacci_runtime.weave"
  ; if condition
  %t2 = icmp ne ptr %t1, null
  br i1 %t2, label %then, label %endif
then:
  ; then
; weave.source kind=statement index=0 bytes=1376..1405 wir-bytes=5285..5458 path="docs/audit/fibonacci_runtime.weave"
  ; set n
  %t3 = call i32 @atoi(ptr %t1)
  store i32 %t3, ptr %n.addr
  br label %endif
endif:
; weave.source kind=statement index=0 bytes=1446..1590 wir-bytes=5618..6390 path="docs/audit/fibonacci_runtime.weave"
  ; if condition
  %t4 = load i32, ptr %n.addr
  %t5 = icmp slt i32 %t4, 0
  br i1 %t5, label %then1, label %endif1
then1:
  ; then
; weave.source kind=statement index=0 bytes=1535..1557 wir-bytes=6137..6267 path="docs/audit/fibonacci_runtime.weave"
  ; set n
  store i32 10, ptr %n.addr
  br label %endif1
endif1:
; weave.source kind=statement index=0 bytes=1598..1743 wir-bytes=6427..7200 path="docs/audit/fibonacci_runtime.weave"
  ; if condition
  %t6 = load i32, ptr %n.addr
  %t7 = icmp sgt i32 %t6, 46
  br i1 %t7, label %then2, label %endif2
then2:
  ; then
; weave.source kind=statement index=0 bytes=1688..1710 wir-bytes=6947..7077 path="docs/audit/fibonacci_runtime.weave"
  ; set n
  store i32 10, ptr %n.addr
  br label %endif2
endif2:
; weave.source kind=statement index=0 bytes=1751..1776 wir-bytes=7237..7406 path="docs/audit/fibonacci_runtime.weave"
  ; return
  %t8 = load i32, ptr %n.addr
  %t9 = call i32 @fib(i32 %t8)
  ret i32 %t9
}

; weave.source kind=function index=0 bytes=532..1096 wir-bytes=997..3870 path="docs/audit/fibonacci_runtime.weave"
; function: fib
; params: i32
; returns: i32
define internal i32 @fib(i32 %n) {
entry:
  %previous.addr = alloca i32
  %current.addr = alloca i32
  %index.addr = alloca i32
; weave.source kind=statement index=0 bytes=593..725 wir-bytes=1449..2103 path="docs/audit/fibonacci_runtime.weave"
  ; if condition
  %t0 = icmp sle i32 %n, 1
  br i1 %t0, label %then, label %endif
then:
  ; then
; weave.source kind=statement index=0 bytes=682..692 wir-bytes=1942..1986 path="docs/audit/fibonacci_runtime.weave"
  ; return
  ret i32 %n
endif:
; weave.source kind=statement index=0 bytes=733..765 wir-bytes=2138..2306 path="docs/audit/fibonacci_runtime.weave"
  ; let previous
  store i32 0, ptr %previous.addr
; weave.source kind=statement index=0 bytes=772..803 wir-bytes=2341..2508 path="docs/audit/fibonacci_runtime.weave"
  ; let current
  store i32 1, ptr %current.addr
; weave.source kind=statement index=0 bytes=810..839 wir-bytes=2543..2708 path="docs/audit/fibonacci_runtime.weave"
  ; let index
  store i32 2, ptr %index.addr
; weave.source kind=statement index=0 bytes=847..1070 wir-bytes=2744..3779 path="docs/audit/fibonacci_runtime.weave"
  ; while condition
  br label %while.cond1
while.cond1:
  %t1 = load i32, ptr %index.addr
  %t2 = icmp sle i32 %t1, %n
  br i1 %t2, label %while.body1, label %while.end1
while.body1:
  ; while body
; weave.source kind=statement index=0 bytes=913..954 wir-bytes=3091..3302 path="docs/audit/fibonacci_runtime.weave"
  %t3 = load i32, ptr %previous.addr
  %t4 = load i32, ptr %current.addr
  %t5 = add i32 %t3, %t4
  ; let next
; weave.source kind=statement index=0 bytes=965..987 wir-bytes=3337..3393 path="docs/audit/fibonacci_runtime.weave"
  ; set previous
  %t6 = load i32, ptr %current.addr
  store i32 %t6, ptr %previous.addr
; weave.source kind=statement index=0 bytes=998..1016 wir-bytes=3429..3483 path="docs/audit/fibonacci_runtime.weave"
  ; set current
  store i32 %t5, ptr %current.addr
; weave.source kind=statement index=0 bytes=1027..1068 wir-bytes=3520..3777 path="docs/audit/fibonacci_runtime.weave"
  ; set index
  %t7 = load i32, ptr %index.addr
  %t8 = add i32 %t7, 1
  store i32 %t8, ptr %index.addr
  br label %while.cond1
while.end1:
; weave.source kind=statement index=0 bytes=1078..1094 wir-bytes=3816..3868 path="docs/audit/fibonacci_runtime.weave"
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
  "sidecar_sha256": "79cca05fe96a1cb52dfba6fb0d47b1f1ba44196ca11a4b6319d0619a08eb1ede"
}
```

### Runtime execution matrix

```json
{
  "case_count": 9,
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
      "name": "missing-input-defaults-to-ten",
      "passed": true,
      "stdin": "",
      "timed_out": false
    },
    {
      "actual": {
        "exit_code": 0,
        "stderr": "",
        "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "stdout": "",
        "stdout_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
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
        "exit_code": 1,
        "stderr": "",
        "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "stdout": "",
        "stdout_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
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
        "exit_code": 1,
        "stderr": "",
        "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "stdout": "",
        "stdout_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
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
        "exit_code": 55,
        "stderr": "",
        "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "stdout": "",
        "stdout_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
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
        "exit_code": 144,
        "stderr": "",
        "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "stdout": "",
        "stdout_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
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
        "exit_code": 55,
        "stderr": "",
        "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "stdout": "",
        "stdout_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
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
        "exit_code": 55,
        "stderr": "",
        "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "stdout": "",
        "stdout_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
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
        "exit_code": 0,
        "stderr": "",
        "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "stdout": "",
        "stdout_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
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
    "writable_paths": [
      "/tmp",
      "/work"
    ]
  },
  "sidecar": "docs/audit/fibonacci_runtime.audit.json",
  "sidecar_sha256": "79cca05fe96a1cb52dfba6fb0d47b1f1ba44196ca11a4b6319d0619a08eb1ede",
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
      "atoi@plt": {
        "backward_branches": 1,
        "backward_conditional_branches": 0,
        "conditional_branches": 0,
        "direct_calls": [],
        "indirect_calls": 0,
        "instructions": 3,
        "padding_instructions": 0
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
      "getenv@plt": {
        "backward_branches": 1,
        "backward_conditional_branches": 0,
        "conditional_branches": 0,
        "direct_calls": [],
        "indirect_calls": 0,
        "instructions": 3,
        "padding_instructions": 0
      },
      "main": {
        "backward_branches": 1,
        "backward_conditional_branches": 1,
        "conditional_branches": 4,
        "direct_calls": [
          "atoi@plt",
          "getenv@plt"
        ],
        "indirect_calls": 0,
        "instructions": 25,
        "padding_instructions": 1
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
    "sidecar_sha256": "79cca05fe96a1cb52dfba6fb0d47b1f1ba44196ca11a4b6319d0619a08eb1ede"
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
  "runtime": {
    "case_count": 9,
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
        "name": "missing-input-defaults-to-ten",
        "passed": true,
        "stdin": "",
        "timed_out": false
      },
      {
        "actual": {
          "exit_code": 0,
          "stderr": "",
          "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
          "stdout": "",
          "stdout_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
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
          "exit_code": 1,
          "stderr": "",
          "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
          "stdout": "",
          "stdout_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
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
          "exit_code": 1,
          "stderr": "",
          "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
          "stdout": "",
          "stdout_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
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
          "exit_code": 55,
          "stderr": "",
          "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
          "stdout": "",
          "stdout_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
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
          "exit_code": 144,
          "stderr": "",
          "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
          "stdout": "",
          "stdout_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
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
          "exit_code": 55,
          "stderr": "",
          "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
          "stdout": "",
          "stdout_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
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
          "exit_code": 55,
          "stderr": "",
          "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
          "stdout": "",
          "stdout_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
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
          "exit_code": 0,
          "stderr": "",
          "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
          "stdout": "",
          "stdout_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
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
      "writable_paths": [
        "/tmp",
        "/work"
      ]
    },
    "sidecar": "docs/audit/fibonacci_runtime.audit.json",
    "sidecar_sha256": "79cca05fe96a1cb52dfba6fb0d47b1f1ba44196ca11a4b6319d0619a08eb1ede",
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
  "output": "/tmp/loupe-audit-5h16a17t/.audit.loupe.7ui3ff9m/artifacts/program",
  "sources": [
    "docs/audit/fibonacci_runtime.weave"
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
    "docs/audit/fibonacci_runtime.weave"
  ],
  "events": []
}
```

## LLM review

## Summary
The final native program for `fibonacci-runtime` is correct, safe, ABI-valid, target-compatible, and free from avoidable compiler-generated overhead. The Weave source semantics are preserved through the WIR and raw LLVM IR. The LLVM optimizer successfully inlines the `fib` function and promotes stack allocations to registers, producing an optimized LLVM IR that matches the source logic. The final x86_64 assembly is compact, uses correct signed comparisons for the loop condition, adheres to the System V ABI for external calls (`getenv`, `atoi`), and returns the result in `%eax`. All 9 configured runtime matrix cases passed successfully, confirming the observable behavior matches the expected values. The native optimization budget constraints are satisfied without violations, and no substantial compiler-generated overhead remains in the final machine code.

## Verification matrix
- Source semantics and expected result: PASS
  The Weave source defines a runtime Fibonacci calculation with input clamping between 0 and 46. The runtime matrix in the complete analysis JSON shows all 9 cases passing with expected exit codes (e.g., `WEAVE_AUDIT_N=10` yields exit code 55, `WEAVE_AUDIT_N=0` yields 0).
- Weave-to-WIR semantic preservation: PASS
  The WIR review projection accurately reflects the source structure, including the `fib` function logic, the `main` entry point, external calls to `getenv` and `atoi`, and the input clamping conditions.
- WIR-to-raw-LLVM semantic preservation: PASS
  The raw LLVM IR correctly translates the WIR, using `alloca` for local variables, `icmp` for conditions, and `br` for control flow. The `fib` function is marked `internal`, and its logic matches the WIR.
- Raw LLVM validity, SSA, types, and control flow: PASS
  The raw LLVM IR is valid, with correct SSA form, typed instructions, and well-formed basic blocks. The complete analysis JSON confirms 0 `poison_uses` and 0 `undef_uses`.
- Optimized LLVM semantic preservation: PASS
  The optimized LLVM IR inlines the `fib` function into `main`, promotes stack variables to registers (0 `alloca`, 0 `load`, 0 `store`), and preserves the loop logic with `phi` nodes for `index`, `current`, and `previous`.
- Integer signedness, overflow, shifts, and comparisons: PASS
  The source uses `i32` for Fibonacci calculations. The optimized LLVM IR uses `icmp ult` for the input range check (0..46) and `icmp sgt` for the loop condition, which is correctly translated to `ja` (unsigned above) and `jle` (signed less-or-equal) in the final assembly. The maximum Fibonacci value for n=46 is 1836311903, which fits within a 32-bit signed integer, avoiding overflow.
- Calls, return values, ABI, stack alignment, and register use: PASS
  The final assembly correctly uses `rdi` for the `getenv` argument and `rax` for its return value, and `rdi` for the `atoi` argument and `eax` for its return value, adhering to the System V ABI. The stack is 16-byte aligned (`pushq %rbx` saves the callee-saved register and provides 8-byte stack adjustment, ensuring alignment before external calls). The program returns the result in `eax`.
- Memory safety, lifetime, leaks, and undefined behavior: PASS
  The program uses a string literal for the `getenv` call and does not perform dynamic memory allocation. The `getenv` return value is checked for null before being passed to `atoi`. The optimized LLVM IR has 0 `poison_uses` and 0 `undef_uses`.
- Target compatibility and native instruction validity: PASS
  The target assembly is valid x86_64 instructions. The target triple is `x86_64-pc-linux-gnu`, and the linked executable disassembly confirms correct linking with glibc (`getenv@plt`, `atoi@plt`).
- Native runtime cases and expected observable behavior: PASS
  All 9 runtime cases in the complete analysis JSON passed, including missing input, zero, one, two, ten, twelve, negative, too-large, and non-numeric inputs. The exit codes match the expected values from the versioned sidecar.
- Configured native limits, required call targets, and loop backedges: PASS
  The native budget in the complete analysis JSON shows `passed: true` with no failures. The `main` function has 25 instructions (max 32), 2 direct calls (max 2), 1 backward conditional branch (min 1, max 1), and 0 indirect calls (max 0). The required direct calls (`atoi@plt`, `getenv@plt`) are present.
- Compiler-generated overhead remaining in final native code: PASS
  The final assembly is compact with no unnecessary instructions. The loop body uses `movl`, `addl`, `incl`, and `cmpl` efficiently. The optimization record shows the loop was not vectorized due to the nature of the Fibonacci recurrence, which is expected and not a defect. The `nopw` instruction is standard alignment padding and within the allowed budget (1 padding instruction).

## Blocking findings
None found.

## Non-blocking opportunities
- The loop in the final assembly uses a counter (`%ecx`) and compares it against the input `n` (`%ebx`) on every iteration. A slightly more optimized loop could decrement `%ecx` towards zero or use a dedicated loop instruction, though the current implementation is already efficient and within the native optimization budget.
- The `freeze i32` instruction in the optimized LLVM IR is used to halt propagation of undefined values from `atoi`, which is a good defensive practice but adds a small amount of IR complexity that disappears in the final assembly.

## Suggested verification
- Add a runtime case for `WEAVE_AUDIT_N=46` to verify the maximum allowed input and ensure no integer overflow occurs in the Fibonacci calculation.
- Add a runtime case for `WEAVE_AUDIT_N=47` to verify the upper bound clamping.
- Add a runtime case for `WEAVE_AUDIT_N=3` to verify the first non-trivial Fibonacci calculation (expected result 2).

<details>
<summary>Raw model response</summary>

```text
OK

## Summary
The final native program for `fibonacci-runtime` is correct, safe, ABI-valid, target-compatible, and free from avoidable compiler-generated overhead. The Weave source semantics are preserved through the WIR and raw LLVM IR. The LLVM optimizer successfully inlines the `fib` function and promotes stack allocations to registers, producing an optimized LLVM IR that matches the source logic. The final x86_64 assembly is compact, uses correct signed comparisons for the loop condition, adheres to the System V ABI for external calls (`getenv`, `atoi`), and returns the result in `%eax`. All 9 configured runtime matrix cases passed successfully, confirming the observable behavior matches the expected values. The native optimization budget constraints are satisfied without violations, and no substantial compiler-generated overhead remains in the final machine code.

## Verification matrix
- Source semantics and expected result: PASS
  The Weave source defines a runtime Fibonacci calculation with input clamping between 0 and 46. The runtime matrix in the complete analysis JSON shows all 9 cases passing with expected exit codes (e.g., `WEAVE_AUDIT_N=10` yields exit code 55, `WEAVE_AUDIT_N=0` yields 0).
- Weave-to-WIR semantic preservation: PASS
  The WIR review projection accurately reflects the source structure, including the `fib` function logic, the `main` entry point, external calls to `getenv` and `atoi`, and the input clamping conditions.
- WIR-to-raw-LLVM semantic preservation: PASS
  The raw LLVM IR correctly translates the WIR, using `alloca` for local variables, `icmp` for conditions, and `br` for control flow. The `fib` function is marked `internal`, and its logic matches the WIR.
- Raw LLVM validity, SSA, types, and control flow: PASS
  The raw LLVM IR is valid, with correct SSA form, typed instructions, and well-formed basic blocks. The complete analysis JSON confirms 0 `poison_uses` and 0 `undef_uses`.
- Optimized LLVM semantic preservation: PASS
  The optimized LLVM IR inlines the `fib` function into `main`, promotes stack variables to registers (0 `alloca`, 0 `load`, 0 `store`), and preserves the loop logic with `phi` nodes for `index`, `current`, and `previous`.
- Integer signedness, overflow, shifts, and comparisons: PASS
  The source uses `i32` for Fibonacci calculations. The optimized LLVM IR uses `icmp ult` for the input range check (0..46) and `icmp sgt` for the loop condition, which is correctly translated to `ja` (unsigned above) and `jle` (signed less-or-equal) in the final assembly. The maximum Fibonacci value for n=46 is 1836311903, which fits within a 32-bit signed integer, avoiding overflow.
- Calls, return values, ABI, stack alignment, and register use: PASS
  The final assembly correctly uses `rdi` for the `getenv` argument and `rax` for its return value, and `rdi` for the `atoi` argument and `eax` for its return value, adhering to the System V ABI. The stack is 16-byte aligned (`pushq %rbx` saves the callee-saved register and provides 8-byte stack adjustment, ensuring alignment before external calls). The program returns the result in `eax`.
- Memory safety, lifetime, leaks, and undefined behavior: PASS
  The program uses a string literal for the `getenv` call and does not perform dynamic memory allocation. The `getenv` return value is checked for null before being passed to `atoi`. The optimized LLVM IR has 0 `poison_uses` and 0 `undef_uses`.
- Target compatibility and native instruction validity: PASS
  The target assembly is valid x86_64 instructions. The target triple is `x86_64-pc-linux-gnu`, and the linked executable disassembly confirms correct linking with glibc (`getenv@plt`, `atoi@plt`).
- Native runtime cases and expected observable behavior: PASS
  All 9 runtime cases in the complete analysis JSON passed, including missing input, zero, one, two, ten, twelve, negative, too-large, and non-numeric inputs. The exit codes match the expected values from the versioned sidecar.
- Configured native limits, required call targets, and loop backedges: PASS
  The native budget in the complete analysis JSON shows `passed: true` with no failures. The `main` function has 25 instructions (max 32), 2 direct calls (max 2), 1 backward conditional branch (min 1, max 1), and 0 indirect calls (max 0). The required direct calls (`atoi@plt`, `getenv@plt`) are present.
- Compiler-generated overhead remaining in final native code: PASS
  The final assembly is compact with no unnecessary instructions. The loop body uses `movl`, `addl`, `incl`, and `cmpl` efficiently. The optimization record shows the loop was not vectorized due to the nature of the Fibonacci recurrence, which is expected and not a defect. The `nopw` instruction is standard alignment padding and within the allowed budget (1 padding instruction).

## Blocking findings
None found.

## Non-blocking opportunities
- The loop in the final assembly uses a counter (`%ecx`) and compares it against the input `n` (`%ebx`) on every iteration. A slightly more optimized loop could decrement `%ecx` towards zero or use a dedicated loop instruction, though the current implementation is already efficient and within the native optimization budget.
- The `freeze i32` instruction in the optimized LLVM IR is used to halt propagation of undefined values from `atoi`, which is a good defensive practice but adds a small amount of IR complexity that disappears in the final assembly.

## Suggested verification
- Add a runtime case for `WEAVE_AUDIT_N=46` to verify the maximum allowed input and ensure no integer overflow occurs in the Fibonacci calculation.
- Add a runtime case for `WEAVE_AUDIT_N=47` to verify the upper bound clamping.
- Add a runtime case for `WEAVE_AUDIT_N=3` to verify the first non-trivial Fibonacci calculation (expected result 2).
```
</details>
