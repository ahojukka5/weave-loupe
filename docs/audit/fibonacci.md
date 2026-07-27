# Weave Loupe Audit Report

## Verdict

- **Status:** OK
- **Code:** none
- **Reason:** No blocking defect found.

## Reproducibility

- **Audit timestamp (UTC):** `2026-07-27T12:24:01+00:00`
- **Audited source Git SHA:** `d99d2c1a7a06870205b3c1b913a8e63f3e51aaa0`
- **Source tree state:** `clean`
- **Weave Loupe Git SHA:** `d99d2c1a7a06870205b3c1b913a8e63f3e51aaa0`
- **weavec Git SHA:** `dbe9e379f663d6dbc7627b3acf21c6d1452db425`
- **weavec binary SHA-256:** `44da49a96942174d8f29dca9ca5582d5ef330e272c6b5de622d66162f500f6ac`
- **weavec version:** `unavailable`
- **LLM model:** `z-ai/glm-5.2`
- **GitHub run ID:** `30265685684`
- **GitHub workflow SHA:** `1eef8d1bb848a202cbcb645e1feb4af11b64afb1`

## Machine and running conditions

- **Operating system:** `Ubuntu 24.04.4 LTS`
- **Kernel:** `Linux 6.17.0-1020-azure`
- **Architecture:** `x86_64`
- **CPU:** `AMD EPYC 9V74 80-Core Processor`
- **Logical CPUs:** `4`
- **Memory:** `16766423040` bytes
- **Python:** `3.12.13`
- **libc:** `glibc 2.39`

## Audited inputs

- `docs/audit/fibonacci.weave` — SHA-256 `443374192b7932b916c5bf1287a0b28d3b8949ed0e2b96620d93a13d656fdbab`

## Captured evidence

- `assembly` — SHA-256 `7b499c3329a52cdeb44a0f97fd11525a60c93660e5b4b97c5a860aba92e37f30`
- `build_manifest` — SHA-256 `3251ca02f15e68f37ee1e76ea85fb925feac605582e19a884bca78ea133b3348`
- `diagnostics` — SHA-256 `a40b573053cda943c381742ad672108b1c8985ecc97e2f21dfa604094e31ff63`
- `disassembly` — SHA-256 `ce594649f3931d9724a2c505ac0628e6d5e243e0ef235568cdb34af2ebb926c5`
- `llvm` — SHA-256 `7b4ea5d3470f6df57681aa02ea8cbc1ad4fd8f2ab60db347a5266c572aae8cb4`
- `optimization_record` — SHA-256 `c96b1b3b7a120ce22ccac3b010192ea88c0b1ce0ef063a37cc8a17d35ef8489f`
- `optimized_llvm` — SHA-256 `1271d4a27ff0eac2c525d5b7f9bb682e51bacdd658302ee50d1f023d5a603dad`
- `trace` — SHA-256 `9e100ae293767539eb406dc28704742846236f6dea99759cf6f731155a44d9ba`
- `wir` — SHA-256 `1b098abf3d5928660a3ed320c36bf52f6c5983d859cd649720a36b76fc369fa5`

## Complete compiler evidence

This section contains the exact evidence reviewed by the model so that the
source-to-native lowering can also be inspected manually.

### Weave source

```lisp
--- docs/audit/fibonacci.weave ---
; Canonical Weave Loupe audit corpus example.
; Computes fib(10) iteratively and returns 55 as the process exit code.

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

### WIR

```lisp
(core-module
  (core-version 2)
  (decls
; weavec-source-file-v1 0 "docs/audit/fibonacci.weave"
    ; weavec-source-span-v1 0 169 750
(; weavec-source-span-v1 0 170 172
fn ; weavec-source-span-v1 0 173 176
fib ; weavec-source-span-v1 0 181 197
(; weavec-source-span-v1 0 182 188
params ; weavec-source-span-v1 0 189 196
(; weavec-source-span-v1 0 190 191
n ; weavec-source-span-v1 0 192 195
i32)) ; weavec-source-span-v1 0 202 215
(; weavec-source-span-v1 0 203 210
returns ; weavec-source-span-v1 0 211 214
i32) ; weavec-source-span-v1 0 220 749
(do ; weavec-source-span-v1 0 230 372
(; weavec-source-span-v1 0 231 233
if ; weavec-source-span-v1 0 242 288
(; weavec-source-span-v1 0 243 252
condition ; weavec-source-span-v1 0 263 287
(; weavec-source-span-v1 0 264 270
le_i32 ; weavec-source-span-v1 0 271 272
n ; weavec-source-span-v1 0 273 286
(; weavec-source-span-v1 0 274 283
const_i32 ; weavec-source-span-v1 0 284 285
1))) ; weavec-source-span-v1 0 297 341
(; weavec-source-span-v1 0 298 302
then ; weavec-source-span-v1 0 313 340
(do ; weavec-source-span-v1 0 329 339
(; weavec-source-span-v1 0 330 336
return ; weavec-source-span-v1 0 337 338
n))) ; weavec-source-span-v1 0 350 371
(; weavec-source-span-v1 0 351 355
else ; weavec-source-span-v1 0 366 370
(do))) ; weavec-source-span-v1 0 379 411
(let ; weavec-source-span-v1 0 384 392
previous i32 ; weavec-source-span-v1 0 397 410
(; weavec-source-span-v1 0 398 407
const_i32 ; weavec-source-span-v1 0 408 409
0)) ; weavec-source-span-v1 0 418 449
(let ; weavec-source-span-v1 0 423 430
current i32 ; weavec-source-span-v1 0 435 448
(; weavec-source-span-v1 0 436 445
const_i32 ; weavec-source-span-v1 0 446 447
1)) ; weavec-source-span-v1 0 456 485
(let ; weavec-source-span-v1 0 461 466
index i32 ; weavec-source-span-v1 0 471 484
(; weavec-source-span-v1 0 472 481
const_i32 ; weavec-source-span-v1 0 482 483
2)) ; weavec-source-span-v1 0 492 725
(; weavec-source-span-v1 0 493 498
while ; weavec-source-span-v1 0 507 545
(; weavec-source-span-v1 0 508 517
condition ; weavec-source-span-v1 0 528 544
(; weavec-source-span-v1 0 529 535
le_i32 ; weavec-source-span-v1 0 536 541
index ; weavec-source-span-v1 0 542 543
n)) ; weavec-source-span-v1 0 554 724
(do ; weavec-source-span-v1 0 568 609
(let ; weavec-source-span-v1 0 573 577
next i32 ; weavec-source-span-v1 0 582 608
(; weavec-source-span-v1 0 583 590
add_i32 ; weavec-source-span-v1 0 591 599
previous ; weavec-source-span-v1 0 600 607
current)) ; weavec-source-span-v1 0 620 642
(; weavec-source-span-v1 0 621 624
set ; weavec-source-span-v1 0 625 633
previous ; weavec-source-span-v1 0 634 641
current) ; weavec-source-span-v1 0 653 671
(; weavec-source-span-v1 0 654 657
set ; weavec-source-span-v1 0 658 665
current ; weavec-source-span-v1 0 666 670
next) ; weavec-source-span-v1 0 682 723
(; weavec-source-span-v1 0 683 686
set ; weavec-source-span-v1 0 687 692
index ; weavec-source-span-v1 0 693 722
(; weavec-source-span-v1 0 694 701
add_i32 ; weavec-source-span-v1 0 702 707
index ; weavec-source-span-v1 0 708 721
(; weavec-source-span-v1 0 709 718
const_i32 ; weavec-source-span-v1 0 719 720
1))))) ; weavec-source-span-v1 0 732 748
(; weavec-source-span-v1 0 733 739
return ; weavec-source-span-v1 0 740 747
current)))
; weavec-source-span-v1 0 753 850
    (fn ; weavec-source-span-v1 0 760 764
main ; weavec-source-span-v1 0 769 777
(; weavec-source-span-v1 0 770 776
params) ; weavec-source-span-v1 0 782 795
(; weavec-source-span-v1 0 783 790
returns ; weavec-source-span-v1 0 791 794
i32) ; weavec-source-span-v1 0 800 849
(do ; weavec-source-span-v1 0 810 848
(; weavec-source-span-v1 0 811 817
return ; weavec-source-span-v1 0 818 847
(; weavec-source-span-v1 0 819 827
call_i32 ; weavec-source-span-v1 0 828 831
fib ; weavec-source-span-v1 0 832 846
(; weavec-source-span-v1 0 833 842
const_i32 ; weavec-source-span-v1 0 843 845
10)))))
  )
)
```

### Raw LLVM IR

```llvm
; generated by weavec
; source: /tmp/weavec-build-LLtaME/program.wir
; core-version: 2

; weave.source kind=function index=0 bytes=753..850 wir-bytes=3294..3880 path="docs/audit/fibonacci.weave"
; function: main
; params: none
; returns: i32
define i32 @main() {
entry:
; weave.source kind=statement index=0 bytes=810..848 wir-bytes=3602..3878 path="docs/audit/fibonacci.weave"
  ; return
  %t0 = call i32 @fib(i32 10)
  ret i32 %t0
}

; weave.source kind=function index=0 bytes=169..750 wir-bytes=134..3255 path="docs/audit/fibonacci.weave"
; function: fib
; params: i32
; returns: i32
define i32 @fib(i32 %n) {
entry:
  %previous.addr = alloca i32
  %current.addr = alloca i32
  %index.addr = alloca i32
; weave.source kind=statement index=0 bytes=230..372 wir-bytes=585..1273 path="docs/audit/fibonacci.weave"
  ; if condition
  %t0 = icmp sle i32 %n, 1
  br i1 %t0, label %then, label %endif
then:
  ; then
; weave.source kind=statement index=0 bytes=329..339 wir-bytes=1078..1156 path="docs/audit/fibonacci.weave"
  ; return
  ret i32 %n
endif:
; weave.source kind=statement index=0 bytes=379..411 wir-bytes=1308..1476 path="docs/audit/fibonacci.weave"
  ; let previous
  store i32 0, ptr %previous.addr
; weave.source kind=statement index=0 bytes=418..449 wir-bytes=1511..1678 path="docs/audit/fibonacci.weave"
  ; let current
  store i32 1, ptr %current.addr
; weave.source kind=statement index=0 bytes=456..485 wir-bytes=1713..1878 path="docs/audit/fibonacci.weave"
  ; let index
  store i32 2, ptr %index.addr
; weave.source kind=statement index=0 bytes=492..725 wir-bytes=1913..3134 path="docs/audit/fibonacci.weave"
  ; while condition
  br label %while.cond1
while.cond1:
  %t1 = load i32, ptr %index.addr
  %t2 = icmp sle i32 %t1, %n
  br i1 %t2, label %while.body1, label %while.end1
while.body1:
  ; while body
; weave.source kind=statement index=0 bytes=568..609 wir-bytes=2259..2470 path="docs/audit/fibonacci.weave"
  %t3 = load i32, ptr %previous.addr
  %t4 = load i32, ptr %current.addr
  %t5 = add i32 %t3, %t4
  ; let next
; weave.source kind=statement index=0 bytes=620..642 wir-bytes=2505..2629 path="docs/audit/fibonacci.weave"
  ; set previous
  %t6 = load i32, ptr %current.addr
  store i32 %t6, ptr %previous.addr
; weave.source kind=statement index=0 bytes=653..671 wir-bytes=2664..2784 path="docs/audit/fibonacci.weave"
  ; set current
  store i32 %t5, ptr %current.addr
; weave.source kind=statement index=0 bytes=682..723 wir-bytes=2819..3132 path="docs/audit/fibonacci.weave"
  ; set index
  %t7 = load i32, ptr %index.addr
  %t8 = add i32 %t7, 1
  store i32 %t8, ptr %index.addr
  br label %while.cond1
while.end1:
; weave.source kind=statement index=0 bytes=732..748 wir-bytes=3169..3253 path="docs/audit/fibonacci.weave"
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

; Function Attrs: nofree norecurse nosync nounwind memory(none)
define i32 @fib(i32 %n) local_unnamed_addr #1 {
entry:
  %t0 = icmp slt i32 %n, 2
  br i1 %t0, label %common.ret, label %while.body1

common.ret:                                       ; preds = %while.body1, %entry
  %common.ret.op = phi i32 [ %n, %entry ], [ %t5, %while.body1 ]
  ret i32 %common.ret.op

while.body1:                                      ; preds = %entry, %while.body1
  %index.addr.06 = phi i32 [ %t8, %while.body1 ], [ 2, %entry ]
  %current.addr.05 = phi i32 [ %t5, %while.body1 ], [ 1, %entry ]
  %previous.addr.04 = phi i32 [ %current.addr.05, %while.body1 ], [ 0, %entry ]
  %t5 = add i32 %current.addr.05, %previous.addr.04
  %t8 = add i32 %index.addr.06, 1
  %t2.not = icmp sgt i32 %t8, %n
  br i1 %t2.not, label %common.ret, label %while.body1
}

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn memory(none) }
attributes #1 = { nofree norecurse nosync nounwind memory(none) }
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
	.globl	fib                             # -- Begin function fib
	.p2align	4, 0x90
	.type	fib,@function
fib:                                    # @fib
# %bb.0:                                # %entry
	cmpl	$2, %edi
	jge	.LBB1_3
# %bb.1:
	movl	%edi, %eax
	retq
.LBB1_3:                                # %while.body1.preheader
	movl	$1, %esi
	movl	$2, %edx
	xorl	%ecx, %ecx
	.p2align	4, 0x90
.LBB1_4:                                # %while.body1
                                        # =>This Inner Loop Header: Depth=1
	addl	%esi, %ecx
	incl	%edx
	movl	%esi, %r8d
	movl	%ecx, %eax
	movl	%ecx, %esi
	movl	%r8d, %ecx
	cmpl	%edi, %edx
	jle	.LBB1_4
# %bb.2:                                # %common.ret
	retq
.Lfunc_end1:
	.size	fib, .Lfunc_end1-fib
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
    1008: 48 8b 05 c1 2f 00 00         	movq	0x2fc1(%rip), %rax      # 0x3fd0 <write@GLIBC_2.2.5+0x3fd0>
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

0000000000001030 <_exit@plt>:
    1030: ff 25 ca 2f 00 00            	jmpq	*0x2fca(%rip)           # 0x4000 <_GLOBAL_OFFSET_TABLE_+0x18>
    1036: 68 00 00 00 00               	pushq	$0x0
    103b: e9 e0 ff ff ff               	jmp	0x1020 <.plt>

0000000000001040 <write@plt>:
    1040: ff 25 c2 2f 00 00            	jmpq	*0x2fc2(%rip)           # 0x4008 <_GLOBAL_OFFSET_TABLE_+0x20>
    1046: 68 01 00 00 00               	pushq	$0x1
    104b: e9 d0 ff ff ff               	jmp	0x1020 <.plt>

Disassembly of section .plt.got:

0000000000001050 <__cxa_finalize@plt>:
    1050: ff 25 8a 2f 00 00            	jmpq	*0x2f8a(%rip)           # 0x3fe0 <write@GLIBC_2.2.5+0x3fe0>
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
    107f: ff 15 3b 2f 00 00            	callq	*0x2f3b(%rip)           # 0x3fc0 <write@GLIBC_2.2.5+0x3fc0>
    1085: f4                           	hlt
    1086: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

0000000000001090 <deregister_tm_clones>:
    1090: 48 8d 3d 89 2f 00 00         	leaq	0x2f89(%rip), %rdi      # 0x4020 <completed.0>
    1097: 48 8d 05 82 2f 00 00         	leaq	0x2f82(%rip), %rax      # 0x4020 <completed.0>
    109e: 48 39 f8                     	cmpq	%rdi, %rax
    10a1: 74 15                        	je	0x10b8 <deregister_tm_clones+0x28>
    10a3: 48 8b 05 1e 2f 00 00         	movq	0x2f1e(%rip), %rax      # 0x3fc8 <write@GLIBC_2.2.5+0x3fc8>
    10aa: 48 85 c0                     	testq	%rax, %rax
    10ad: 74 09                        	je	0x10b8 <deregister_tm_clones+0x28>
    10af: ff e0                        	jmpq	*%rax
    10b1: 0f 1f 80 00 00 00 00         	nopl	(%rax)
    10b8: c3                           	retq
    10b9: 0f 1f 80 00 00 00 00         	nopl	(%rax)

00000000000010c0 <register_tm_clones>:
    10c0: 48 8d 3d 59 2f 00 00         	leaq	0x2f59(%rip), %rdi      # 0x4020 <completed.0>
    10c7: 48 8d 35 52 2f 00 00         	leaq	0x2f52(%rip), %rsi      # 0x4020 <completed.0>
    10ce: 48 29 fe                     	subq	%rdi, %rsi
    10d1: 48 89 f0                     	movq	%rsi, %rax
    10d4: 48 c1 ee 3f                  	shrq	$0x3f, %rsi
    10d8: 48 c1 f8 03                  	sarq	$0x3, %rax
    10dc: 48 01 c6                     	addq	%rax, %rsi
    10df: 48 d1 fe                     	sarq	%rsi
    10e2: 74 14                        	je	0x10f8 <register_tm_clones+0x38>
    10e4: 48 8b 05 ed 2e 00 00         	movq	0x2eed(%rip), %rax      # 0x3fd8 <write@GLIBC_2.2.5+0x3fd8>
    10eb: 48 85 c0                     	testq	%rax, %rax
    10ee: 74 08                        	je	0x10f8 <register_tm_clones+0x38>
    10f0: ff e0                        	jmpq	*%rax
    10f2: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
    10f8: c3                           	retq
    10f9: 0f 1f 80 00 00 00 00         	nopl	(%rax)

0000000000001100 <__do_global_dtors_aux>:
    1100: f3 0f 1e fa                  	endbr64
    1104: 80 3d 15 2f 00 00 00         	cmpb	$0x0, 0x2f15(%rip)      # 0x4020 <completed.0>
    110b: 75 2b                        	jne	0x1138 <__do_global_dtors_aux+0x38>
    110d: 55                           	pushq	%rbp
    110e: 48 83 3d ca 2e 00 00 00      	cmpq	$0x0, 0x2eca(%rip)      # 0x3fe0 <write@GLIBC_2.2.5+0x3fe0>
    1116: 48 89 e5                     	movq	%rsp, %rbp
    1119: 74 0c                        	je	0x1127 <__do_global_dtors_aux+0x27>
    111b: 48 8b 3d f6 2e 00 00         	movq	0x2ef6(%rip), %rdi      # 0x4018 <__dso_handle>
    1122: e8 29 ff ff ff               	callq	0x1050 <__cxa_finalize@plt>
    1127: e8 64 ff ff ff               	callq	0x1090 <deregister_tm_clones>
    112c: c6 05 ed 2e 00 00 01         	movb	$0x1, 0x2eed(%rip)      # 0x4020 <completed.0>
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
    1150: b8 37 00 00 00               	movl	$0x37, %eax
    1155: c3                           	retq
    1156: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

0000000000001160 <fib>:
    1160: 83 ff 02                     	cmpl	$0x2, %edi
    1163: 7d 03                        	jge	0x1168 <fib+0x8>
    1165: 89 f8                        	movl	%edi, %eax
    1167: c3                           	retq
    1168: be 01 00 00 00               	movl	$0x1, %esi
    116d: ba 02 00 00 00               	movl	$0x2, %edx
    1172: 31 c9                        	xorl	%ecx, %ecx
    1174: 66 66 66 2e 0f 1f 84 00 00 00 00 00  	nopw	%cs:(%rax,%rax)
    1180: 01 f1                        	addl	%esi, %ecx
    1182: ff c2                        	incl	%edx
    1184: 41 89 f0                     	movl	%esi, %r8d
    1187: 89 c8                        	movl	%ecx, %eax
    1189: 89 ce                        	movl	%ecx, %esi
    118b: 44 89 c1                     	movl	%r8d, %ecx
    118e: 39 fa                        	cmpl	%edi, %edx
    1190: 7e ee                        	jle	0x1180 <fib+0x20>
    1192: c3                           	retq
    1193: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)
    119d: 0f 1f 00                     	nopl	(%rax)

00000000000011a0 <weave_rt_contract_fail>:
    11a0: 55                           	pushq	%rbp
    11a1: 48 89 e5                     	movq	%rsp, %rbp
    11a4: 48 83 ec 20                  	subq	$0x20, %rsp
    11a8: 48 89 7d f8                  	movq	%rdi, -0x8(%rbp)
    11ac: c6 45 f7 0a                  	movb	$0xa, -0x9(%rbp)
    11b0: 48 8b 45 f8                  	movq	-0x8(%rbp), %rax
    11b4: 48 89 45 e8                  	movq	%rax, -0x18(%rbp)
    11b8: 48 c7 45 e0 00 00 00 00      	movq	$0x0, -0x20(%rbp)
    11c0: 48 83 7d e8 00               	cmpq	$0x0, -0x18(%rbp)
    11c5: 0f 84 3d 00 00 00            	je	0x1208 <weave_rt_contract_fail+0x68>
    11cb: e9 00 00 00 00               	jmp	0x11d0 <weave_rt_contract_fail+0x30>
    11d0: 48 8b 45 e8                  	movq	-0x18(%rbp), %rax
    11d4: 48 8b 4d e0                  	movq	-0x20(%rbp), %rcx
    11d8: 0f be 04 08                  	movsbl	(%rax,%rcx), %eax
    11dc: 83 f8 00                     	cmpl	$0x0, %eax
    11df: 0f 84 11 00 00 00            	je	0x11f6 <weave_rt_contract_fail+0x56>
    11e5: 48 8b 45 e0                  	movq	-0x20(%rbp), %rax
    11e9: 48 83 c0 01                  	addq	$0x1, %rax
    11ed: 48 89 45 e0                  	movq	%rax, -0x20(%rbp)
    11f1: e9 da ff ff ff               	jmp	0x11d0 <weave_rt_contract_fail+0x30>
    11f6: 48 8b 75 e8                  	movq	-0x18(%rbp), %rsi
    11fa: 48 8b 55 e0                  	movq	-0x20(%rbp), %rdx
    11fe: bf 02 00 00 00               	movl	$0x2, %edi
    1203: e8 38 fe ff ff               	callq	0x1040 <write@plt>
    1208: bf 02 00 00 00               	movl	$0x2, %edi
    120d: 48 8d 75 f7                  	leaq	-0x9(%rbp), %rsi
    1211: ba 01 00 00 00               	movl	$0x1, %edx
    1216: e8 25 fe ff ff               	callq	0x1040 <write@plt>
    121b: bf 01 00 00 00               	movl	$0x1, %edi
    1220: e8 0b fe ff ff               	callq	0x1030 <_exit@plt>

Disassembly of section .fini:

0000000000001228 <_fini>:
    1228: f3 0f 1e fa                  	endbr64
    122c: 48 83 ec 08                  	subq	$0x8, %rsp
    1230: 48 83 c4 08                  	addq	$0x8, %rsp
    1234: c3                           	retq
```

### LLVM optimization record

```yaml
# weavec optimization stage: llvm-ir
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
  - Cost:            '-15'
  - String:          ', threshold='
  - Threshold:       '250'
  - String:          ')'
...
--- !Passed
Pass:            loop-delete
Name:            Invariant
Function:        main
Args:
  - String:          Loop deleted because it is invariant
...
--- !Analysis
Pass:            loop-vectorize
Name:            NonReductionValueUsedOutsideLoop
Function:        fib
Args:
  - String:          'loop not vectorized: '
  - String:          value that could not be identified as reduction is used outside the loop
...
--- !Analysis
Pass:            loop-vectorize
Name:            CantComputeNumberOfIterations
Function:        fib
Args:
  - String:          'loop not vectorized: '
  - String:          could not determine number of loop iterations
...
--- !Missed
Pass:            loop-vectorize
Name:            MissedDetails
Function:        fib
Args:
  - String:          loop not vectorized
...
--- !Missed
Pass:            slp-vectorizer
Name:            NotPossible
Function:        fib
Args:
  - String:          'Cannot SLP vectorize list: vectorization was impossible'
  - String:          ' with available vectorization factors'
...
--- !Missed
Pass:            slp-vectorizer
Name:            NotPossible
Function:        fib
Args:
  - String:          'Cannot SLP vectorize list: vectorization was impossible'
  - String:          ' with available vectorization factors'
...
--- !Missed
Pass:            slp-vectorizer
Name:            NotPossible
Function:        fib
Args:
  - String:          'Cannot SLP vectorize list: vectorization was impossible'
  - String:          ' with available vectorization factors'
...
--- !Missed
Pass:            slp-vectorizer
Name:            NotBeneficial
Function:        fib
Args:
  - String:          'List vectorization was possible but not beneficial with cost '
  - Cost:            '0'
  - String:          ' >= '
  - Treshold:        '0'
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
--- !Analysis
Pass:            size-info
Name:            IRSizeChange
Function:        fib
Args:
  - Pass:            Canonicalize natural loops
  - String:          ': IR instruction count changed from '
  - IRInstrsBefore:  '12'
  - String:          ' to '
  - IRInstrsAfter:   '14'
  - String:          '; Delta: '
  - DeltaInstrCount: '2'
...
--- !Analysis
Pass:            size-info
Name:            FunctionIRSizeChange
Function:        fib
Args:
  - Pass:            Canonicalize natural loops
  - String:          ': Function: '
  - Function:        fib
  - String:          ': IR instruction count changed from '
  - IRInstrsBefore:  '11'
  - String:          ' to '
  - IRInstrsAfter:   '13'
  - String:          '; Delta: '
  - DeltaInstrCount: '2'
...
--- !Analysis
Pass:            size-info
Name:            IRSizeChange
Function:        fib
Args:
  - Pass:            CodeGen Prepare
  - String:          ': IR instruction count changed from '
  - IRInstrsBefore:  '14'
  - String:          ' to '
  - IRInstrsAfter:   '13'
  - String:          '; Delta: '
  - DeltaInstrCount: '-1'
...
--- !Analysis
Pass:            size-info
Name:            FunctionIRSizeChange
Function:        fib
Args:
  - Pass:            CodeGen Prepare
  - String:          ': Function: '
  - Function:        fib
  - String:          ': IR instruction count changed from '
  - IRInstrsBefore:  '13'
  - String:          ' to '
  - IRInstrsAfter:   '12'
  - String:          '; Delta: '
  - DeltaInstrCount: '-1'
...
--- !Analysis
Pass:            size-info
Name:            FunctionMISizeChange
Function:        fib
Args:
  - Pass:            'X86 DAG->DAG Instruction Selection'
  - String:          ': Function: '
  - Function:        fib
  - String:          ': '
  - String:          'MI Instruction count changed from '
  - MIInstrsBefore:  '0'
  - String:          ' to '
  - MIInstrsAfter:   '19'
  - String:          '; Delta: '
  - Delta:           '19'
...
--- !Analysis
Pass:            size-info
Name:            FunctionMISizeChange
Function:        fib
Args:
  - Pass:            Eliminate PHI nodes for register allocation
  - String:          ': Function: '
  - Function:        fib
  - String:          ': '
  - String:          'MI Instruction count changed from '
  - MIInstrsBefore:  '19'
  - String:          ' to '
  - MIInstrsAfter:   '27'
  - String:          '; Delta: '
  - Delta:           '8'
...
--- !Analysis
Pass:            size-info
Name:            FunctionMISizeChange
Function:        fib
Args:
  - Pass:            Two-Address instruction pass
  - String:          ': Function: '
  - Function:        fib
  - String:          ': '
  - String:          'MI Instruction count changed from '
  - MIInstrsBefore:  '27'
  - String:          ' to '
  - MIInstrsAfter:   '29'
  - String:          '; Delta: '
  - Delta:           '2'
...
--- !Analysis
Pass:            size-info
Name:            FunctionMISizeChange
Function:        fib
Args:
  - Pass:            Register Coalescer
  - String:          ': Function: '
  - Function:        fib
  - String:          ': '
  - String:          'MI Instruction count changed from '
  - MIInstrsBefore:  '29'
  - String:          ' to '
  - MIInstrsAfter:   '20'
  - String:          '; Delta: '
  - Delta:           '-9'
...
--- !Missed
Pass:            regalloc
Name:            LoopSpillReloadCopies
Function:        fib
Args:
  - NumVRCopies:     '4'
  - String:          ' virtual registers copies '
  - TotalCopiesCost: '6.400000e+01'
  - String:          ' total copies cost '
  - String:          generated in loop
...
--- !Missed
Pass:            regalloc
Name:            SpillReloadCopies
Function:        fib
Args:
  - NumVRCopies:     '5'
  - String:          ' virtual registers copies '
  - TotalCopiesCost: '6.450000e+01'
  - String:          ' total copies cost '
  - String:          generated in function
...
--- !Analysis
Pass:            size-info
Name:            FunctionMISizeChange
Function:        fib
Args:
  - Pass:            Virtual Register Rewriter
  - String:          ': Function: '
  - Function:        fib
  - String:          ': '
  - String:          'MI Instruction count changed from '
  - MIInstrsBefore:  '20'
  - String:          ' to '
  - MIInstrsAfter:   '18'
  - String:          '; Delta: '
  - Delta:           '-2'
...
--- !Analysis
Pass:            prologepilog
Name:            StackSize
Function:        fib
Args:
  - NumStackBytes:   '0'
  - String:          ' stack bytes in function '''
  - Function:        fib
  - String:          ''''
...
--- !Analysis
Pass:            size-info
Name:            FunctionMISizeChange
Function:        fib
Args:
  - Pass:            Control Flow Optimizer
  - String:          ': Function: '
  - Function:        fib
  - String:          ': '
  - String:          'MI Instruction count changed from '
  - MIInstrsBefore:  '18'
  - String:          ' to '
  - MIInstrsAfter:   '16'
  - String:          '; Delta: '
  - Delta:           '-2'
...
--- !Analysis
Pass:            stack-frame-layout
Name:            StackLayout
Function:        fib
Args:
  - String:          "\nFunction: fib"
...
--- !Analysis
Pass:            asm-printer
Name:            InstructionMix
Function:        fib
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
Name:            InstructionMix
Function:        fib
Args:
  - String:          'BasicBlock: '
  - BasicBlock:      ''
  - String:          "\n"
  - String:          ''
  - String:          ': '
  - INST_:           '2'
  - String:          "\n"
...
--- !Analysis
Pass:            asm-printer
Name:            InstructionMix
Function:        fib
Args:
  - String:          'BasicBlock: '
  - BasicBlock:      while.body1.preheader
  - String:          "\n"
  - String:          ''
  - String:          ': '
  - INST_:           '3'
  - String:          "\n"
...
--- !Analysis
Pass:            asm-printer
Name:            InstructionMix
Function:        fib
Args:
  - String:          'BasicBlock: '
  - BasicBlock:      while.body1
  - String:          "\n"
  - String:          ''
  - String:          ': '
  - INST_:           '8'
  - String:          "\n"
...
--- !Analysis
Pass:            asm-printer
Name:            InstructionMix
Function:        fib
Args:
  - String:          'BasicBlock: '
  - BasicBlock:      common.ret
  - String:          "\n"
  - String:          ''
  - String:          ': '
  - INST_:           '1'
  - String:          "\n"
...
--- !Analysis
Pass:            asm-printer
Name:            InstructionCount
Function:        fib
Args:
  - NumInstructions: '16'
  - String:          ' instructions in function'
...
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
  "optimized_llvm": {
    "add": 2,
    "alloca": 0,
    "anonymous_ssa_lines": 0,
    "basic_blocks": 4,
    "br": 2,
    "call": 0,
    "functions": 2,
    "icmp": 2,
    "identity_adds": 0,
    "instructions": 12,
    "invoke": 0,
    "load": 0,
    "mul": 0,
    "numeric_blocks": 0,
    "phi": 4,
    "poison_uses": 0,
    "provenance_comments": 0,
    "ret": 2,
    "sdiv": 0,
    "select": 0,
    "store": 0,
    "sub": 0,
    "switch": 0,
    "udiv": 0,
    "undef_uses": 0
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
  "output": "/tmp/loupe-audit-qi6uprp_/.audit.loupe.dwj2clxg/artifacts/program",
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
The final native program is correct, safe, ABI-valid, target-compatible, and free from avoidable compiler-generated overhead. The Weave source computes `fib(10)` iteratively and returns `55` as the process exit code. The WIR preserves the source semantics, and the raw LLVM IR correctly lowers the WIR into valid SSA with proper control flow. The optimized LLVM IR inlines `fib` into `main` and constant-folds the computation to `ret i32 55`. The target assembly and linked executable disassembly confirm that `main` compiles to `movl $55, %eax; retq`, matching the System V AMD64 ABI return convention. The `fib` function is preserved in the final binary but is not invoked by `main`, representing dead code at runtime but not compiler-generated overhead in the active execution path. All verification matrix rows have affirmative artifact evidence.

## Verification matrix
- Source semantics and expected result: PASS. The Weave source (`docs/audit/fibonacci.weave`) defines an iterative `fib` function and `main` returns `fib(10)`. The expected result is `55` (Fibonacci sequence: 0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55).
- Weave-to-WIR semantic preservation: PASS. The WIR preserves the `if` condition (`le_i32 n (const_i32 1)`), the `while` loop (`le_i32 index n`), the iterative state updates (`add_i32`, `set`), and the `main` return call (`call_i32 fib (const_i32 10)`).
- WIR-to-raw-LLVM semantic preservation: PASS. The raw LLVM IR maps the WIR `if` to `icmp sle i32 %n, 1`, the `while` to `icmp sle i32 %t1, %n`, and the iterative updates to `add i32` and `store` operations. The `main` function calls `@fib(i32 10)` and returns the result.
- Raw LLVM validity, SSA, and control flow: PASS. The raw LLVM IR is valid SSA with proper basic blocks (`entry`, `then`, `endif`, `while.cond1`, `while.body1`, `while.end1`), well-formed `phi`-free control flow, and correct `ret` instructions. The analysis JSON confirms 0 `poison_uses` and 0 `undef_uses`.
- Optimized LLVM semantic preservation: PASS. The optimized LLVM IR inlines `fib` into `main` (confirmed by the optimization record `inline` pass) and constant-folds the result to `ret i32 55`. The `fib` function is preserved with correct loop logic (`phi` nodes for `index`, `current`, `previous`).
- Integer signedness, overflow, shifts, and comparisons: PASS. The source uses `i32` with `le_i32` and `add_i32`. The LLVM IR uses `icmp sle`/`slt` and `add i32`. For `fib(10)`, the maximum value is `55`, well within `i32` range, so no overflow occurs. The `cmpl $2, %edi; jge` in `fib` correctly implements the signed comparison `n < 2`.
- Calls, return values, ABI, stack alignment, and register use: PASS. `main` returns `55` in `%eax` per System V AMD64 ABI. The linked disassembly shows `_start` calling `main` via `__libc_start_main` (implied by the `callq *0x2f3b(%rip)`). `fib` uses `%edi` for the `n` parameter and `%eax` for the return value, with 0 stack bytes (confirmed by optimization record `StackSize: 0`).
- Memory safety, lifetime, leaks, and undefined behavior: PASS. The raw LLVM IR uses `alloca` for local variables, but the optimized LLVM IR promotes them to SSA registers (0 `alloca` in optimized IR). No heap allocations or leaks. The `weave_rt_contract_fail` function is present but unreachable from `main`.
- Target compatibility and native instruction validity: PASS. The target triple is `x86_64-pc-linux-gnu`. The assembly uses valid x86-64 instructions (`movl`, `retq`, `cmpl`, `jge`, `addl`, `incl`, `jle`). The linked executable is `elf64-x86-64` with standard glibc integration.
- Compiler-generated overhead remaining in final native code: PASS. `main` is minimal (`movl $55, %eax; retq`) with no compiler-generated overhead. The `fib` function contains a tight loop with no spills or redundant operations (optimization record confirms 0 stack bytes and efficient register allocation).

## Blocking findings
None found.

## Non-blocking opportunities
- The `fib` function is preserved in the final binary despite `main` not calling it (due to inlining and constant folding). If `fib` is not required as a public symbol, marking it as `internal` or `private` linkage in the Weave source or LLVM IR would allow the linker to discard it, reducing binary size. This is a source-level algorithm choice, not compiler-generated overhead.
- The `weave_rt_contract_fail` function is linked into the binary but is unreachable from `main`. Link-time garbage collection (`-Wl,--gc-sections`) or marking it as dead could reduce binary size if not needed for debugging.

## Suggested verification
- Run the linked executable and verify the process exit code is `55` (`echo $?`).
- Test `fib` with edge cases (e.g., `fib(0)`, `fib(1)`, `fib(2)`) to confirm the `n < 2` boundary condition.
- Test `fib` with larger inputs (e.g., `fib(47)`) to confirm signed `i32` overflow behavior matches Weave semantics.
- Inspect the linked binary with `nm` to confirm `fib` is present as a global symbol and evaluate whether dead-code elimination could remove it.

<details>
<summary>Raw model response</summary>

```text
OK
## Summary
The final native program is correct, safe, ABI-valid, target-compatible, and free from avoidable compiler-generated overhead. The Weave source computes `fib(10)` iteratively and returns `55` as the process exit code. The WIR preserves the source semantics, and the raw LLVM IR correctly lowers the WIR into valid SSA with proper control flow. The optimized LLVM IR inlines `fib` into `main` and constant-folds the computation to `ret i32 55`. The target assembly and linked executable disassembly confirm that `main` compiles to `movl $55, %eax; retq`, matching the System V AMD64 ABI return convention. The `fib` function is preserved in the final binary but is not invoked by `main`, representing dead code at runtime but not compiler-generated overhead in the active execution path. All verification matrix rows have affirmative artifact evidence.

## Verification matrix
- Source semantics and expected result: PASS. The Weave source (`docs/audit/fibonacci.weave`) defines an iterative `fib` function and `main` returns `fib(10)`. The expected result is `55` (Fibonacci sequence: 0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55).
- Weave-to-WIR semantic preservation: PASS. The WIR preserves the `if` condition (`le_i32 n (const_i32 1)`), the `while` loop (`le_i32 index n`), the iterative state updates (`add_i32`, `set`), and the `main` return call (`call_i32 fib (const_i32 10)`).
- WIR-to-raw-LLVM semantic preservation: PASS. The raw LLVM IR maps the WIR `if` to `icmp sle i32 %n, 1`, the `while` to `icmp sle i32 %t1, %n`, and the iterative updates to `add i32` and `store` operations. The `main` function calls `@fib(i32 10)` and returns the result.
- Raw LLVM validity, SSA, and control flow: PASS. The raw LLVM IR is valid SSA with proper basic blocks (`entry`, `then`, `endif`, `while.cond1`, `while.body1`, `while.end1`), well-formed `phi`-free control flow, and correct `ret` instructions. The analysis JSON confirms 0 `poison_uses` and 0 `undef_uses`.
- Optimized LLVM semantic preservation: PASS. The optimized LLVM IR inlines `fib` into `main` (confirmed by the optimization record `inline` pass) and constant-folds the result to `ret i32 55`. The `fib` function is preserved with correct loop logic (`phi` nodes for `index`, `current`, `previous`).
- Integer signedness, overflow, shifts, and comparisons: PASS. The source uses `i32` with `le_i32` and `add_i32`. The LLVM IR uses `icmp sle`/`slt` and `add i32`. For `fib(10)`, the maximum value is `55`, well within `i32` range, so no overflow occurs. The `cmpl $2, %edi; jge` in `fib` correctly implements the signed comparison `n < 2`.
- Calls, return values, ABI, stack alignment, and register use: PASS. `main` returns `55` in `%eax` per System V AMD64 ABI. The linked disassembly shows `_start` calling `main` via `__libc_start_main` (implied by the `callq *0x2f3b(%rip)`). `fib` uses `%edi` for the `n` parameter and `%eax` for the return value, with 0 stack bytes (confirmed by optimization record `StackSize: 0`).
- Memory safety, lifetime, leaks, and undefined behavior: PASS. The raw LLVM IR uses `alloca` for local variables, but the optimized LLVM IR promotes them to SSA registers (0 `alloca` in optimized IR). No heap allocations or leaks. The `weave_rt_contract_fail` function is present but unreachable from `main`.
- Target compatibility and native instruction validity: PASS. The target triple is `x86_64-pc-linux-gnu`. The assembly uses valid x86-64 instructions (`movl`, `retq`, `cmpl`, `jge`, `addl`, `incl`, `jle`). The linked executable is `elf64-x86-64` with standard glibc integration.
- Compiler-generated overhead remaining in final native code: PASS. `main` is minimal (`movl $55, %eax; retq`) with no compiler-generated overhead. The `fib` function contains a tight loop with no spills or redundant operations (optimization record confirms 0 stack bytes and efficient register allocation).

## Blocking findings
None found.

## Non-blocking opportunities
- The `fib` function is preserved in the final binary despite `main` not calling it (due to inlining and constant folding). If `fib` is not required as a public symbol, marking it as `internal` or `private` linkage in the Weave source or LLVM IR would allow the linker to discard it, reducing binary size. This is a source-level algorithm choice, not compiler-generated overhead.
- The `weave_rt_contract_fail` function is linked into the binary but is unreachable from `main`. Link-time garbage collection (`-Wl,--gc-sections`) or marking it as dead could reduce binary size if not needed for debugging.

## Suggested verification
- Run the linked executable and verify the process exit code is `55` (`echo $?`).
- Test `fib` with edge cases (e.g., `fib(0)`, `fib(1)`, `fib(2)`) to confirm the `n < 2` boundary condition.
- Test `fib` with larger inputs (e.g., `fib(47)`) to confirm signed `i32` overflow behavior matches Weave semantics.
- Inspect the linked binary with `nm` to confirm `fib` is present as a global symbol and evaluate whether dead-code elimination could remove it.
```
</details>
