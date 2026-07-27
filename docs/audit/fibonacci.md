# Weave Loupe Audit Report

## Verdict

- **Status:** OK
- **Code:** none
- **Reason:** No blocking defect found.

## Reproducibility

- **Audit timestamp (UTC):** `2026-07-27T12:26:21+00:00`
- **Audited source Git SHA:** `3388071b3f1bc15cf5bfab40c17cf2fe029ad22f`
- **Source tree state:** `clean`
- **Weave Loupe Git SHA:** `3388071b3f1bc15cf5bfab40c17cf2fe029ad22f`
- **weavec Git SHA:** `dbe9e379f663d6dbc7627b3acf21c6d1452db425`
- **weavec binary SHA-256:** `44da49a96942174d8f29dca9ca5582d5ef330e272c6b5de622d66162f500f6ac`
- **weavec version:** `unavailable`
- **LLM model:** `z-ai/glm-5.2`
- **GitHub run ID:** `30265842076`
- **GitHub workflow SHA:** `fb64fa3d4be58b813de69951d569fd898f2b0e13`

## Machine and running conditions

- **Operating system:** `Ubuntu 24.04.4 LTS`
- **Kernel:** `Linux 6.17.0-1020-azure`
- **Architecture:** `x86_64`
- **CPU:** `AMD EPYC 7763 64-Core Processor`
- **Logical CPUs:** `4`
- **Memory:** `16770752512` bytes
- **Python:** `3.12.13`
- **libc:** `glibc 2.39`

## Audited inputs

- `docs/audit/fibonacci.weave` — SHA-256 `a4f2c64e04bcc12b583227e37087ee31ccc58e4a0a57e5f627a29bae980d5398`

## Captured evidence

- `assembly` — SHA-256 `7b499c3329a52cdeb44a0f97fd11525a60c93660e5b4b97c5a860aba92e37f30`
- `build_manifest` — SHA-256 `b6b8a3d74aeeabd94ad1bd0f0494ec08e70af2ebaa2d099399f94e03cf2398bb`
- `diagnostics` — SHA-256 `a40b573053cda943c381742ad672108b1c8985ecc97e2f21dfa604094e31ff63`
- `disassembly` — SHA-256 `ce594649f3931d9724a2c505ac0628e6d5e243e0ef235568cdb34af2ebb926c5`
- `llvm` — SHA-256 `df67366d90fdf7bf5dce959f164dd3343ccfe85cd87dd0230d10821298437a95`
- `optimization_record` — SHA-256 `c96b1b3b7a120ce22ccac3b010192ea88c0b1ce0ef063a37cc8a17d35ef8489f`
- `optimized_llvm` — SHA-256 `1271d4a27ff0eac2c525d5b7f9bb682e51bacdd658302ee50d1f023d5a603dad`
- `trace` — SHA-256 `9e100ae293767539eb406dc28704742846236f6dea99759cf6f731155a44d9ba`
- `wir` — SHA-256 `58edba09bdd223e16c72d47c66e2fa3a889105fa5043d1def0c08925dfaaa970`

## Complete compiler evidence

This section contains the exact evidence reviewed by the model so that the
source-to-native lowering can also be inspected manually.

### Weave source

```lisp
--- docs/audit/fibonacci.weave ---
; Canonical Weave Loupe audit corpus example.
; Computes fib(10) iteratively; the expected signed i32 return value is 55.

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
    ; weavec-source-span-v1 0 173 754
(; weavec-source-span-v1 0 174 176
fn ; weavec-source-span-v1 0 177 180
fib ; weavec-source-span-v1 0 185 201
(; weavec-source-span-v1 0 186 192
params ; weavec-source-span-v1 0 193 200
(; weavec-source-span-v1 0 194 195
n ; weavec-source-span-v1 0 196 199
i32)) ; weavec-source-span-v1 0 206 219
(; weavec-source-span-v1 0 207 214
returns ; weavec-source-span-v1 0 215 218
i32) ; weavec-source-span-v1 0 224 753
(do ; weavec-source-span-v1 0 234 376
(; weavec-source-span-v1 0 235 237
if ; weavec-source-span-v1 0 246 292
(; weavec-source-span-v1 0 247 256
condition ; weavec-source-span-v1 0 267 291
(; weavec-source-span-v1 0 268 274
le_i32 ; weavec-source-span-v1 0 275 276
n ; weavec-source-span-v1 0 277 290
(; weavec-source-span-v1 0 278 287
const_i32 ; weavec-source-span-v1 0 288 289
1))) ; weavec-source-span-v1 0 301 345
(; weavec-source-span-v1 0 302 306
then ; weavec-source-span-v1 0 317 344
(do ; weavec-source-span-v1 0 333 343
(; weavec-source-span-v1 0 334 340
return ; weavec-source-span-v1 0 341 342
n))) ; weavec-source-span-v1 0 354 375
(; weavec-source-span-v1 0 355 359
else ; weavec-source-span-v1 0 370 374
(do))) ; weavec-source-span-v1 0 383 415
(let ; weavec-source-span-v1 0 388 396
previous i32 ; weavec-source-span-v1 0 401 414
(; weavec-source-span-v1 0 402 411
const_i32 ; weavec-source-span-v1 0 412 413
0)) ; weavec-source-span-v1 0 422 453
(let ; weavec-source-span-v1 0 427 434
current i32 ; weavec-source-span-v1 0 439 452
(; weavec-source-span-v1 0 440 449
const_i32 ; weavec-source-span-v1 0 450 451
1)) ; weavec-source-span-v1 0 460 489
(let ; weavec-source-span-v1 0 465 470
index i32 ; weavec-source-span-v1 0 475 488
(; weavec-source-span-v1 0 476 485
const_i32 ; weavec-source-span-v1 0 486 487
2)) ; weavec-source-span-v1 0 496 729
(; weavec-source-span-v1 0 497 502
while ; weavec-source-span-v1 0 511 549
(; weavec-source-span-v1 0 512 521
condition ; weavec-source-span-v1 0 532 548
(; weavec-source-span-v1 0 533 539
le_i32 ; weavec-source-span-v1 0 540 545
index ; weavec-source-span-v1 0 546 547
n)) ; weavec-source-span-v1 0 558 728
(do ; weavec-source-span-v1 0 572 613
(let ; weavec-source-span-v1 0 577 581
next i32 ; weavec-source-span-v1 0 586 612
(; weavec-source-span-v1 0 587 594
add_i32 ; weavec-source-span-v1 0 595 603
previous ; weavec-source-span-v1 0 604 611
current)) ; weavec-source-span-v1 0 624 646
(; weavec-source-span-v1 0 625 628
set ; weavec-source-span-v1 0 629 637
previous ; weavec-source-span-v1 0 638 645
current) ; weavec-source-span-v1 0 657 675
(; weavec-source-span-v1 0 658 661
set ; weavec-source-span-v1 0 662 669
current ; weavec-source-span-v1 0 670 674
next) ; weavec-source-span-v1 0 686 727
(; weavec-source-span-v1 0 687 690
set ; weavec-source-span-v1 0 691 696
index ; weavec-source-span-v1 0 697 726
(; weavec-source-span-v1 0 698 705
add_i32 ; weavec-source-span-v1 0 706 711
index ; weavec-source-span-v1 0 712 725
(; weavec-source-span-v1 0 713 722
const_i32 ; weavec-source-span-v1 0 723 724
1))))) ; weavec-source-span-v1 0 736 752
(; weavec-source-span-v1 0 737 743
return ; weavec-source-span-v1 0 744 751
current)))
; weavec-source-span-v1 0 757 854
    (fn ; weavec-source-span-v1 0 764 768
main ; weavec-source-span-v1 0 773 781
(; weavec-source-span-v1 0 774 780
params) ; weavec-source-span-v1 0 786 799
(; weavec-source-span-v1 0 787 794
returns ; weavec-source-span-v1 0 795 798
i32) ; weavec-source-span-v1 0 804 853
(do ; weavec-source-span-v1 0 814 852
(; weavec-source-span-v1 0 815 821
return ; weavec-source-span-v1 0 822 851
(; weavec-source-span-v1 0 823 831
call_i32 ; weavec-source-span-v1 0 832 835
fib ; weavec-source-span-v1 0 836 850
(; weavec-source-span-v1 0 837 846
const_i32 ; weavec-source-span-v1 0 847 849
10)))))
  )
)
```

### Raw LLVM IR

```llvm
; generated by weavec
; source: /tmp/weavec-build-ynavEU/program.wir
; core-version: 2

; weave.source kind=function index=0 bytes=757..854 wir-bytes=3294..3880 path="docs/audit/fibonacci.weave"
; function: main
; params: none
; returns: i32
define i32 @main() {
entry:
; weave.source kind=statement index=0 bytes=814..852 wir-bytes=3602..3878 path="docs/audit/fibonacci.weave"
  ; return
  %t0 = call i32 @fib(i32 10)
  ret i32 %t0
}

; weave.source kind=function index=0 bytes=173..754 wir-bytes=134..3255 path="docs/audit/fibonacci.weave"
; function: fib
; params: i32
; returns: i32
define i32 @fib(i32 %n) {
entry:
  %previous.addr = alloca i32
  %current.addr = alloca i32
  %index.addr = alloca i32
; weave.source kind=statement index=0 bytes=234..376 wir-bytes=585..1273 path="docs/audit/fibonacci.weave"
  ; if condition
  %t0 = icmp sle i32 %n, 1
  br i1 %t0, label %then, label %endif
then:
  ; then
; weave.source kind=statement index=0 bytes=333..343 wir-bytes=1078..1156 path="docs/audit/fibonacci.weave"
  ; return
  ret i32 %n
endif:
; weave.source kind=statement index=0 bytes=383..415 wir-bytes=1308..1476 path="docs/audit/fibonacci.weave"
  ; let previous
  store i32 0, ptr %previous.addr
; weave.source kind=statement index=0 bytes=422..453 wir-bytes=1511..1678 path="docs/audit/fibonacci.weave"
  ; let current
  store i32 1, ptr %current.addr
; weave.source kind=statement index=0 bytes=460..489 wir-bytes=1713..1878 path="docs/audit/fibonacci.weave"
  ; let index
  store i32 2, ptr %index.addr
; weave.source kind=statement index=0 bytes=496..729 wir-bytes=1913..3134 path="docs/audit/fibonacci.weave"
  ; while condition
  br label %while.cond1
while.cond1:
  %t1 = load i32, ptr %index.addr
  %t2 = icmp sle i32 %t1, %n
  br i1 %t2, label %while.body1, label %while.end1
while.body1:
  ; while body
; weave.source kind=statement index=0 bytes=572..613 wir-bytes=2259..2470 path="docs/audit/fibonacci.weave"
  %t3 = load i32, ptr %previous.addr
  %t4 = load i32, ptr %current.addr
  %t5 = add i32 %t3, %t4
  ; let next
; weave.source kind=statement index=0 bytes=624..646 wir-bytes=2505..2629 path="docs/audit/fibonacci.weave"
  ; set previous
  %t6 = load i32, ptr %current.addr
  store i32 %t6, ptr %previous.addr
; weave.source kind=statement index=0 bytes=657..675 wir-bytes=2664..2784 path="docs/audit/fibonacci.weave"
  ; set current
  store i32 %t5, ptr %current.addr
; weave.source kind=statement index=0 bytes=686..727 wir-bytes=2819..3132 path="docs/audit/fibonacci.weave"
  ; set index
  %t7 = load i32, ptr %index.addr
  %t8 = add i32 %t7, 1
  store i32 %t8, ptr %index.addr
  br label %while.cond1
while.end1:
; weave.source kind=statement index=0 bytes=736..752 wir-bytes=3169..3253 path="docs/audit/fibonacci.weave"
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
  "output": "/tmp/loupe-audit-9jrqr7_n/.audit.loupe.2z18iz7w/artifacts/program",
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
The Weave compiler toolchain successfully preserves the semantics of the iterative Fibonacci computation from the source code through WIR, raw LLVM IR, optimized LLVM IR, and final x86_64 assembly. The `main` function correctly evaluates to a constant return of 55 (`0x37`), which is verified across the optimized LLVM IR and the linked executable disassembly. The `fib` function is correctly compiled to a native loop that adheres to the System V AMD64 ABI, using 32-bit registers and signed comparisons without generating any stack frames or avoidable overhead. No blocking defects, undefined behavior, or ABI violations were found.

## Verification matrix
- Source semantics and expected result: PASS. The source `docs/audit/fibonacci.weave` defines an iterative `fib(10)` computation. The expected return value of 55 is confirmed in the linked executable disassembly (`movl $0x37, %eax` at `0x1150`).
- Weave-to-WIR semantic preservation: PASS. The WIR accurately reflects the source structure, including the `le_i32` condition, `let` bindings for `previous`, `current`, and `index`, and the `while` loop with `add_i32` operations.
- WIR-to-raw-LLVM semantic preservation: PASS. The raw LLVM IR correctly maps WIR variables to `alloca`/`load`/`store` patterns and translates `le_i32` to `icmp sle i32 %n, 1`.
- Raw LLVM validity, SSA, types, and control flow: PASS. The raw LLVM IR is well-formed, uses valid SSA values, and has correct branching (`br i1 %t0, label %then, label %endif`) with no unreachable blocks or invalid types.
- Optimized LLVM semantic preservation: PASS. The optimized LLVM IR promotes stack allocations to registers using `phi` nodes, inlines `fib` into `main` (as noted in the optimization record), and correctly folds `main` to `ret i32 55`.
- Integer signedness, overflow, shifts, and comparisons: PASS. The optimized LLVM IR uses `icmp slt` and `icmp sgt` for signed comparisons. The target assembly uses `cmpl $0x2, %edi` followed by `jge` and `jle`, which correctly implement signed comparisons for i32 values.
- Calls, return values, ABI, stack alignment, and register use: PASS. The `fib` function receives its argument in `%edi` and returns in `%eax`, matching the System V AMD64 ABI. No stack adjustments are needed in `fib` or `main`, as confirmed by the `StackSize: 0` analysis in the optimization record.
- Memory safety, lifetime, leaks, and undefined behavior: PASS. The raw LLVM IR uses safe stack allocations that are completely optimized away. The optimized LLVM IR has no `alloca`, `load`, or `store` instructions, eliminating memory safety risks.
- Target compatibility and native instruction validity: PASS. The target assembly uses valid x86_64 instructions (`movl`, `cmpl`, `addl`, `incl`, `jle`, `jge`, `retq`) appropriate for the `x86_64-pc-linux-gnu` target triple.
- Compiler-generated overhead remaining in final native code: PASS. The final `fib` function is highly optimized, operating entirely in registers (`%edi`, `%esi`, `%edx`, `%ecx`, `%r8d`, `%eax`) with zero stack usage and no unnecessary moves or spills.

## Blocking findings
None found.

## Non-blocking opportunities
- The `fib` function's loop body contains several register-to-register moves (`movl %esi, %r8d`, `movl %ecx, %eax`, `movl %ecx, %esi`, `movl %r8d, %ecx`) to manage the iterative state. While these are standard for an iterative Fibonacci implementation and do not represent compiler-generated overhead, a source-level recursive implementation or a closed-form mathematical formula could reduce the instruction count further. This is a source algorithm choice, not a compiler defect.
- The raw LLVM IR uses `alloca` for local variables, which is standard for unoptimized code generation but adds verbosity. These are completely eliminated during LLVM optimization, so it is not a blocking issue.

## Suggested verification
- Execute the linked executable to dynamically verify that the process exit code is 55 (`$?` equals 55).
- Test the `fib` function with edge cases such as `fib(0)`, `fib(1)`, and `fib(-1)` to ensure the signed comparison `cmpl $0x2, %edi; jge` correctly handles values less than 2.
- Test with a large value of `n` (e.g., `n = 46`) to observe i32 signed integer overflow behavior and confirm it wraps around as expected for two's complement arithmetic.

<details>
<summary>Raw model response</summary>

```text
OK
## Summary
The Weave compiler toolchain successfully preserves the semantics of the iterative Fibonacci computation from the source code through WIR, raw LLVM IR, optimized LLVM IR, and final x86_64 assembly. The `main` function correctly evaluates to a constant return of 55 (`0x37`), which is verified across the optimized LLVM IR and the linked executable disassembly. The `fib` function is correctly compiled to a native loop that adheres to the System V AMD64 ABI, using 32-bit registers and signed comparisons without generating any stack frames or avoidable overhead. No blocking defects, undefined behavior, or ABI violations were found.

## Verification matrix
- Source semantics and expected result: PASS. The source `docs/audit/fibonacci.weave` defines an iterative `fib(10)` computation. The expected return value of 55 is confirmed in the linked executable disassembly (`movl $0x37, %eax` at `0x1150`).
- Weave-to-WIR semantic preservation: PASS. The WIR accurately reflects the source structure, including the `le_i32` condition, `let` bindings for `previous`, `current`, and `index`, and the `while` loop with `add_i32` operations.
- WIR-to-raw-LLVM semantic preservation: PASS. The raw LLVM IR correctly maps WIR variables to `alloca`/`load`/`store` patterns and translates `le_i32` to `icmp sle i32 %n, 1`.
- Raw LLVM validity, SSA, types, and control flow: PASS. The raw LLVM IR is well-formed, uses valid SSA values, and has correct branching (`br i1 %t0, label %then, label %endif`) with no unreachable blocks or invalid types.
- Optimized LLVM semantic preservation: PASS. The optimized LLVM IR promotes stack allocations to registers using `phi` nodes, inlines `fib` into `main` (as noted in the optimization record), and correctly folds `main` to `ret i32 55`.
- Integer signedness, overflow, shifts, and comparisons: PASS. The optimized LLVM IR uses `icmp slt` and `icmp sgt` for signed comparisons. The target assembly uses `cmpl $0x2, %edi` followed by `jge` and `jle`, which correctly implement signed comparisons for i32 values.
- Calls, return values, ABI, stack alignment, and register use: PASS. The `fib` function receives its argument in `%edi` and returns in `%eax`, matching the System V AMD64 ABI. No stack adjustments are needed in `fib` or `main`, as confirmed by the `StackSize: 0` analysis in the optimization record.
- Memory safety, lifetime, leaks, and undefined behavior: PASS. The raw LLVM IR uses safe stack allocations that are completely optimized away. The optimized LLVM IR has no `alloca`, `load`, or `store` instructions, eliminating memory safety risks.
- Target compatibility and native instruction validity: PASS. The target assembly uses valid x86_64 instructions (`movl`, `cmpl`, `addl`, `incl`, `jle`, `jge`, `retq`) appropriate for the `x86_64-pc-linux-gnu` target triple.
- Compiler-generated overhead remaining in final native code: PASS. The final `fib` function is highly optimized, operating entirely in registers (`%edi`, `%esi`, `%edx`, `%ecx`, `%r8d`, `%eax`) with zero stack usage and no unnecessary moves or spills.

## Blocking findings
None found.

## Non-blocking opportunities
- The `fib` function's loop body contains several register-to-register moves (`movl %esi, %r8d`, `movl %ecx, %eax`, `movl %ecx, %esi`, `movl %r8d, %ecx`) to manage the iterative state. While these are standard for an iterative Fibonacci implementation and do not represent compiler-generated overhead, a source-level recursive implementation or a closed-form mathematical formula could reduce the instruction count further. This is a source algorithm choice, not a compiler defect.
- The raw LLVM IR uses `alloca` for local variables, which is standard for unoptimized code generation but adds verbosity. These are completely eliminated during LLVM optimization, so it is not a blocking issue.

## Suggested verification
- Execute the linked executable to dynamically verify that the process exit code is 55 (`$?` equals 55).
- Test the `fib` function with edge cases such as `fib(0)`, `fib(1)`, and `fib(-1)` to ensure the signed comparison `cmpl $0x2, %edi; jge` correctly handles values less than 2.
- Test with a large value of `n` (e.g., `n = 46`) to observe i32 signed integer overflow behavior and confirm it wraps around as expected for two's complement arithmetic.
```
</details>
