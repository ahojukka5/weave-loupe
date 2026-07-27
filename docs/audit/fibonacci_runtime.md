# Weave Loupe Audit Report

## Verdict

- **Status:** OK
- **Code:** none
- **Reason:** No blocking defect found.

## Reproducibility

- **Audit timestamp (UTC):** `2026-07-27T18:35:18+00:00`
- **Audited source Git SHA:** `d1d470feb45e547ab78e43e349a26ce86e9227fa`
- **Source tree state:** `clean`
- **Weave Loupe Git SHA:** `d1d470feb45e547ab78e43e349a26ce86e9227fa`
- **weavec Git SHA:** `b7046aacc634283a7ae6e548984d00511dcc7776`
- **weavec binary SHA-256:** `96e78338d7ae0199646f78f4af6d4d3c25f2b027c8ddc7ab25bd3a2dfdfdea70`
- **weavec version:** `unavailable`
- **LLM model:** `z-ai/glm-5.2`
- **GitHub run ID:** `30294376027`
- **GitHub workflow SHA:** `7e496dfc8925725cf736cbf525e1110c96d9540f`

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

- `docs/audit/fibonacci_runtime.weave` — SHA-256 `a0df013d2e54ac1426498c7fda686d113ae4ca4f7371fe3836c490ccf9343ba4`

## Captured evidence

- `assembly` — SHA-256 `355551c6d11759a2137d794f6154bee9f187aff00d09f7f13887d82a052f3bf1`
- `build_manifest` — SHA-256 `d2856103e6eb34ef6cfd4d94748c75156df9401ea0b9dae70bfe55419a7be246`
- `diagnostics` — SHA-256 `a40b573053cda943c381742ad672108b1c8985ecc97e2f21dfa604094e31ff63`
- `disassembly` — SHA-256 `fc79aff611b518050aabf8fba9f4e4d9206bbb333c222fa01363938355cb582a`
- `llvm` — SHA-256 `9a2a63d52ca9eb50d0415fa8f29b0e5f9b42118fb0706c1912241a4b04080ce8`
- `optimization_record` — SHA-256 `c1eed531ffbbd0e9d7c3558ecea6e951283dcb7e51ce4ebf7c1144aa66d37c6d`
- `optimized_llvm` — SHA-256 `7bda6a3ae32ec72bf1ac4f39971bba88d5f34fff09f56798c9cdbbf76414598e`
- `trace` — SHA-256 `b2b31cb4820d6e3e8eb29602a4ca1e1637f19953fa4ce2230d0a6f2d5d8e7878`
- `wir` — SHA-256 `18612b3faa8ab3ff49cb3715d81de010c09459b00b83fb4121043ef8a63495d4`

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

### WIR

```lisp
(core-module
  (core-version 2)
  (decls
; weavec-source-file-v1 0 "docs/audit/fibonacci_runtime.weave"
    ; weavec-source-span-v1 0 412 469
(; weavec-source-span-v1 0 413 419
extern ; weavec-source-span-v1 0 420 426
getenv ; weavec-source-span-v1 0 431 450
(; weavec-source-span-v1 0 432 438
params ; weavec-source-span-v1 0 439 449
(; weavec-source-span-v1 0 440 444
name ; weavec-source-span-v1 0 445 448
ptr)) ; weavec-source-span-v1 0 455 468
(; weavec-source-span-v1 0 456 463
returns ; weavec-source-span-v1 0 464 467
ptr))
    ; weavec-source-span-v1 0 473 528
(; weavec-source-span-v1 0 474 480
extern ; weavec-source-span-v1 0 481 485
atoi ; weavec-source-span-v1 0 490 509
(; weavec-source-span-v1 0 491 497
params ; weavec-source-span-v1 0 498 508
(; weavec-source-span-v1 0 499 503
text ; weavec-source-span-v1 0 504 507
ptr)) ; weavec-source-span-v1 0 514 527
(; weavec-source-span-v1 0 515 522
returns ; weavec-source-span-v1 0 523 526
i32))
    ; weavec-source-span-v1 0 532 1096
(; weavec-source-span-v1 0 533 535
fn ; weavec-source-span-v1 0 536 539
fib ; weavec-source-span-v1 0 544 560
(; weavec-source-span-v1 0 545 551
params ; weavec-source-span-v1 0 552 559
(; weavec-source-span-v1 0 553 554
n ; weavec-source-span-v1 0 555 558
i32)) ; weavec-source-span-v1 0 565 578
(; weavec-source-span-v1 0 566 573
returns ; weavec-source-span-v1 0 574 577
i32) ; weavec-source-span-v1 0 583 1095
(do ; weavec-source-span-v1 0 593 725
(; weavec-source-span-v1 0 594 596
if ; weavec-source-span-v1 0 605 641
(; weavec-source-span-v1 0 606 615
condition ; weavec-source-span-v1 0 616 640
(; weavec-source-span-v1 0 617 623
le_i32 ; weavec-source-span-v1 0 624 625
n ; weavec-source-span-v1 0 626 639
(; weavec-source-span-v1 0 627 636
const_i32 ; weavec-source-span-v1 0 637 638
1))) ; weavec-source-span-v1 0 650 694
(; weavec-source-span-v1 0 651 655
then ; weavec-source-span-v1 0 666 693
(do ; weavec-source-span-v1 0 682 692
(; weavec-source-span-v1 0 683 689
return ; weavec-source-span-v1 0 690 691
n))) ; weavec-source-span-v1 0 703 724
(; weavec-source-span-v1 0 704 708
else ; weavec-source-span-v1 0 719 723
(do))) ; weavec-source-span-v1 0 733 765
(let ; weavec-source-span-v1 0 738 746
previous i32 ; weavec-source-span-v1 0 751 764
(; weavec-source-span-v1 0 752 761
const_i32 ; weavec-source-span-v1 0 762 763
0)) ; weavec-source-span-v1 0 772 803
(let ; weavec-source-span-v1 0 777 784
current i32 ; weavec-source-span-v1 0 789 802
(; weavec-source-span-v1 0 790 799
const_i32 ; weavec-source-span-v1 0 800 801
1)) ; weavec-source-span-v1 0 810 839
(let ; weavec-source-span-v1 0 815 820
index i32 ; weavec-source-span-v1 0 825 838
(; weavec-source-span-v1 0 826 835
const_i32 ; weavec-source-span-v1 0 836 837
2)) ; weavec-source-span-v1 0 847 1070
(; weavec-source-span-v1 0 848 853
while ; weavec-source-span-v1 0 862 890
(; weavec-source-span-v1 0 863 872
condition ; weavec-source-span-v1 0 873 889
(; weavec-source-span-v1 0 874 880
le_i32 ; weavec-source-span-v1 0 881 886
index ; weavec-source-span-v1 0 887 888
n)) ; weavec-source-span-v1 0 899 1069
(do ; weavec-source-span-v1 0 913 954
(let ; weavec-source-span-v1 0 918 922
next i32 ; weavec-source-span-v1 0 927 953
(; weavec-source-span-v1 0 928 935
add_i32 ; weavec-source-span-v1 0 936 944
previous ; weavec-source-span-v1 0 945 952
current)) ; weavec-source-span-v1 0 965 987
(; weavec-source-span-v1 0 966 969
set ; weavec-source-span-v1 0 970 978
previous ; weavec-source-span-v1 0 979 986
current) ; weavec-source-span-v1 0 998 1016
(; weavec-source-span-v1 0 999 1002
set ; weavec-source-span-v1 0 1003 1010
current ; weavec-source-span-v1 0 1011 1015
next) ; weavec-source-span-v1 0 1027 1068
(; weavec-source-span-v1 0 1028 1031
set ; weavec-source-span-v1 0 1032 1037
index ; weavec-source-span-v1 0 1038 1067
(; weavec-source-span-v1 0 1039 1046
add_i32 ; weavec-source-span-v1 0 1047 1052
index ; weavec-source-span-v1 0 1053 1066
(; weavec-source-span-v1 0 1054 1063
const_i32 ; weavec-source-span-v1 0 1064 1065
1))))) ; weavec-source-span-v1 0 1078 1094
(; weavec-source-span-v1 0 1079 1085
return ; weavec-source-span-v1 0 1086 1093
current)))
; weavec-source-span-v1 0 1100 1778
    (fn ; weavec-source-span-v1 0 1107 1111
main ; weavec-source-span-v1 0 1116 1124
(; weavec-source-span-v1 0 1117 1123
params) ; weavec-source-span-v1 0 1129 1142
(; weavec-source-span-v1 0 1130 1137
returns ; weavec-source-span-v1 0 1138 1141
i32) ; weavec-source-span-v1 0 1147 1777
(do ; weavec-source-span-v1 0 1157 1243
(let ; weavec-source-span-v1 0 1162 1167
input ptr ; weavec-source-span-v1 0 1180 1242
(; weavec-source-span-v1 0 1181 1189
call_ptr ; weavec-source-span-v1 0 1190 1196
getenv ; weavec-source-span-v1 0 1207 1241
(; weavec-source-span-v1 0 1208 1224
const_string_ptr ; weavec-source-span-v1 0 1226 1239
"WEAVE_AUDIT_N"))) ; weavec-source-span-v1 0 1250 1276
(let ; weavec-source-span-v1 0 1255 1256
n i32 ; weavec-source-span-v1 0 1261 1275
(; weavec-source-span-v1 0 1262 1271
const_i32 ; weavec-source-span-v1 0 1272 1274
10)) ; weavec-source-span-v1 0 1284 1438
(; weavec-source-span-v1 0 1285 1287
if ; weavec-source-span-v1 0 1296 1335
(; weavec-source-span-v1 0 1297 1306
condition ; weavec-source-span-v1 0 1307 1334
(; weavec-source-span-v1 0 1308 1314
ne_ptr ; weavec-source-span-v1 0 1315 1320
input ; weavec-source-span-v1 0 1321 1333
(; weavec-source-span-v1 0 1322 1332
const_null))) ; weavec-source-span-v1 0 1344 1407
(; weavec-source-span-v1 0 1345 1349
then ; weavec-source-span-v1 0 1360 1406
(do ; weavec-source-span-v1 0 1376 1405
(; weavec-source-span-v1 0 1377 1380
set ; weavec-source-span-v1 0 1381 1382
n ; weavec-source-span-v1 0 1383 1404
(; weavec-source-span-v1 0 1384 1392
call_i32 ; weavec-source-span-v1 0 1393 1397
atoi ; weavec-source-span-v1 0 1398 1403
input)))) ; weavec-source-span-v1 0 1416 1437
(; weavec-source-span-v1 0 1417 1421
else ; weavec-source-span-v1 0 1432 1436
(do))) ; weavec-source-span-v1 0 1446 1590
(; weavec-source-span-v1 0 1447 1449
if ; weavec-source-span-v1 0 1458 1494
(; weavec-source-span-v1 0 1459 1468
condition ; weavec-source-span-v1 0 1469 1493
(; weavec-source-span-v1 0 1470 1476
lt_i32 ; weavec-source-span-v1 0 1477 1478
n ; weavec-source-span-v1 0 1479 1492
(; weavec-source-span-v1 0 1480 1489
const_i32 ; weavec-source-span-v1 0 1490 1491
0))) ; weavec-source-span-v1 0 1503 1559
(; weavec-source-span-v1 0 1504 1508
then ; weavec-source-span-v1 0 1519 1558
(do ; weavec-source-span-v1 0 1535 1557
(; weavec-source-span-v1 0 1536 1539
set ; weavec-source-span-v1 0 1540 1541
n ; weavec-source-span-v1 0 1542 1556
(; weavec-source-span-v1 0 1543 1552
const_i32 ; weavec-source-span-v1 0 1553 1555
10)))) ; weavec-source-span-v1 0 1568 1589
(; weavec-source-span-v1 0 1569 1573
else ; weavec-source-span-v1 0 1584 1588
(do))) ; weavec-source-span-v1 0 1598 1743
(; weavec-source-span-v1 0 1599 1601
if ; weavec-source-span-v1 0 1610 1647
(; weavec-source-span-v1 0 1611 1620
condition ; weavec-source-span-v1 0 1621 1646
(; weavec-source-span-v1 0 1622 1628
gt_i32 ; weavec-source-span-v1 0 1629 1630
n ; weavec-source-span-v1 0 1631 1645
(; weavec-source-span-v1 0 1632 1641
const_i32 ; weavec-source-span-v1 0 1642 1644
46))) ; weavec-source-span-v1 0 1656 1712
(; weavec-source-span-v1 0 1657 1661
then ; weavec-source-span-v1 0 1672 1711
(do ; weavec-source-span-v1 0 1688 1710
(; weavec-source-span-v1 0 1689 1692
set ; weavec-source-span-v1 0 1693 1694
n ; weavec-source-span-v1 0 1695 1709
(; weavec-source-span-v1 0 1696 1705
const_i32 ; weavec-source-span-v1 0 1706 1708
10)))) ; weavec-source-span-v1 0 1721 1742
(; weavec-source-span-v1 0 1722 1726
else ; weavec-source-span-v1 0 1737 1741
(do))) ; weavec-source-span-v1 0 1751 1776
(; weavec-source-span-v1 0 1752 1758
return ; weavec-source-span-v1 0 1759 1775
(; weavec-source-span-v1 0 1760 1768
call_i32 ; weavec-source-span-v1 0 1769 1772
fib ; weavec-source-span-v1 0 1773 1774
n))))
  )
)
```

### Raw LLVM IR

```llvm
; generated by weavec
; source: /tmp/weavec-build-KGItfo/program.wir
; core-version: 2

; declarations

declare ptr @getenv(ptr)
declare i32 @atoi(ptr)

; string literals

@.str0 = private unnamed_addr constant [14 x i8] c"WEAVE_AUDIT_N\00"

; weave.source kind=function index=0 bytes=1100..1778 wir-bytes=4192..7941 path="docs/audit/fibonacci_runtime.weave"
; function: main
; params: none
; returns: i32
define i32 @main() {
entry:
  %n.addr = alloca i32
; weave.source kind=statement index=0 bytes=1157..1243 wir-bytes=4516..4836 path="docs/audit/fibonacci_runtime.weave"
  %t0 = getelementptr [14 x i8], ptr @.str0, i64 0, i64 0
  %t1 = call ptr @getenv(ptr %t0)
  ; let input
; weave.source kind=statement index=0 bytes=1250..1276 wir-bytes=4873..5043 path="docs/audit/fibonacci_runtime.weave"
  ; let n
  store i32 10, ptr %n.addr
; weave.source kind=statement index=0 bytes=1284..1438 wir-bytes=5080..5934 path="docs/audit/fibonacci_runtime.weave"
  ; if condition
  %t2 = icmp ne ptr %t1, null
  br i1 %t2, label %then, label %endif
then:
  ; then
; weave.source kind=statement index=0 bytes=1376..1405 wir-bytes=5566..5811 path="docs/audit/fibonacci_runtime.weave"
  ; set n
  %t3 = call i32 @atoi(ptr %t1)
  store i32 %t3, ptr %n.addr
  br label %endif
endif:
; weave.source kind=statement index=0 bytes=1446..1590 wir-bytes=5971..6815 path="docs/audit/fibonacci_runtime.weave"
  ; if condition
  %t4 = load i32, ptr %n.addr
  %t5 = icmp slt i32 %t4, 0
  br i1 %t5, label %then1, label %endif1
then1:
  ; then
; weave.source kind=statement index=0 bytes=1535..1557 wir-bytes=6490..6692 path="docs/audit/fibonacci_runtime.weave"
  ; set n
  store i32 10, ptr %n.addr
  br label %endif1
endif1:
; weave.source kind=statement index=0 bytes=1598..1743 wir-bytes=6852..7697 path="docs/audit/fibonacci_runtime.weave"
  ; if condition
  %t6 = load i32, ptr %n.addr
  %t7 = icmp sgt i32 %t6, 46
  br i1 %t7, label %then2, label %endif2
then2:
  ; then
; weave.source kind=statement index=0 bytes=1688..1710 wir-bytes=7372..7574 path="docs/audit/fibonacci_runtime.weave"
  ; set n
  store i32 10, ptr %n.addr
  br label %endif2
endif2:
; weave.source kind=statement index=0 bytes=1751..1776 wir-bytes=7734..7939 path="docs/audit/fibonacci_runtime.weave"
  ; return
  %t8 = load i32, ptr %n.addr
  %t9 = call i32 @fib(i32 %t8)
  ret i32 %t9
}

; weave.source kind=function index=0 bytes=532..1096 wir-bytes=997..4151 path="docs/audit/fibonacci_runtime.weave"
; function: fib
; params: i32
; returns: i32
define internal i32 @fib(i32 %n) {
entry:
  %previous.addr = alloca i32
  %current.addr = alloca i32
  %index.addr = alloca i32
; weave.source kind=statement index=0 bytes=593..725 wir-bytes=1449..2137 path="docs/audit/fibonacci_runtime.weave"
  ; if condition
  %t0 = icmp sle i32 %n, 1
  br i1 %t0, label %then, label %endif
then:
  ; then
; weave.source kind=statement index=0 bytes=682..692 wir-bytes=1942..2020 path="docs/audit/fibonacci_runtime.weave"
  ; return
  ret i32 %n
endif:
; weave.source kind=statement index=0 bytes=733..765 wir-bytes=2172..2340 path="docs/audit/fibonacci_runtime.weave"
  ; let previous
  store i32 0, ptr %previous.addr
; weave.source kind=statement index=0 bytes=772..803 wir-bytes=2375..2542 path="docs/audit/fibonacci_runtime.weave"
  ; let current
  store i32 1, ptr %current.addr
; weave.source kind=statement index=0 bytes=810..839 wir-bytes=2577..2742 path="docs/audit/fibonacci_runtime.weave"
  ; let index
  store i32 2, ptr %index.addr
; weave.source kind=statement index=0 bytes=847..1070 wir-bytes=2778..4024 path="docs/audit/fibonacci_runtime.weave"
  ; while condition
  br label %while.cond1
while.cond1:
  %t1 = load i32, ptr %index.addr
  %t2 = icmp sle i32 %t1, %n
  br i1 %t2, label %while.body1, label %while.end1
while.body1:
  ; while body
; weave.source kind=statement index=0 bytes=913..954 wir-bytes=3125..3336 path="docs/audit/fibonacci_runtime.weave"
  %t3 = load i32, ptr %previous.addr
  %t4 = load i32, ptr %current.addr
  %t5 = add i32 %t3, %t4
  ; let next
; weave.source kind=statement index=0 bytes=965..987 wir-bytes=3371..3495 path="docs/audit/fibonacci_runtime.weave"
  ; set previous
  %t6 = load i32, ptr %current.addr
  store i32 %t6, ptr %previous.addr
; weave.source kind=statement index=0 bytes=998..1016 wir-bytes=3531..3656 path="docs/audit/fibonacci_runtime.weave"
  ; set current
  store i32 %t5, ptr %current.addr
; weave.source kind=statement index=0 bytes=1027..1068 wir-bytes=3693..4022 path="docs/audit/fibonacci_runtime.weave"
  ; set index
  %t7 = load i32, ptr %index.addr
  %t8 = add i32 %t7, 1
  store i32 %t8, ptr %index.addr
  br label %while.cond1
while.end1:
; weave.source kind=statement index=0 bytes=1078..1094 wir-bytes=4061..4149 path="docs/audit/fibonacci_runtime.weave"
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
      "atoi@plt": {
        "direct_calls": [],
        "indirect_calls": 0,
        "instructions": 3,
        "padding_instructions": 0
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
      "getenv@plt": {
        "direct_calls": [],
        "indirect_calls": 0,
        "instructions": 3,
        "padding_instructions": 0
      },
      "main": {
        "direct_calls": [
          "atoi@plt",
          "getenv@plt"
        ],
        "indirect_calls": 0,
        "instructions": 25,
        "padding_instructions": 1
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
  "output": "/tmp/loupe-audit-88174fy1/.audit.loupe.408n5n21/artifacts/program",
  "sources": ["docs/audit/fibonacci_runtime.weave"]
}
```

### Compiler trace

```json
{
  "format": "weavec-compilation-trace-v1",
  "status": "succeeded",
  "phase": "complete",
  "sources": ["docs/audit/fibonacci_runtime.weave"],
  "events": []
}
```

## LLM review

## Summary
The final native program for `docs/audit/fibonacci_runtime.weave` is correct, safe, ABI-valid, target-compatible, and free from avoidable compiler-generated overhead. The Weave source defines a runtime-input Fibonacci computation that intentionally resists constant folding. This semantic intent is preserved through WIR, raw LLVM, optimized LLVM, target assembly, and the linked executable. LLVM successfully inlines the `fib` function into `main`, promotes stack temporaries to registers, and emits a compact 25-instruction native `main` function that retains the input-dependent loop. All control-flow edges, signed comparisons, and arithmetic widths match the source semantics. The x86_64 ABI is respected, and no undefined behavior or memory unsafety is present.

## Verification matrix
- Source semantics and expected result: PASS. The Weave source (`fibonacci_runtime.weave`) defines a `fib` function with an input-dependent `while` loop and a `main` function that reads `WEAVE_AUDIT_N`, clamps the value to `[0, 46]` (defaulting to 10), and calls `fib`. The linked disassembly (`1150`-`119f`) contains the loop and calls to `getenv@plt` and `atoi@plt`, matching the expected runtime behavior.
- Weave-to-WIR semantic preservation: PASS. The WIR preserves all source constructs, including the `le_i32`, `add_i32`, `lt_i32`, and `gt_i32` operations, the `while` loop, and the `getenv`/`atoi` calls with correct pointer and integer types.
- WIR-to-raw-LLVM semantic preservation: PASS. The raw LLVM IR maps WIR operations to valid LLVM instructions (`icmp sle`, `add i32`, `icmp slt`, `icmp sgt`). Stack allocations (`alloca`) are used for local variables, and control flow matches the WIR structure.
- Raw LLVM validity, SSA, types, and control flow: PASS. The raw LLVM IR is valid, uses correct SSA form, and has well-formed basic blocks and control-flow edges. The analysis JSON confirms 0 `poison_uses` and 0 `undef_uses`.
- Optimized LLVM semantic preservation: PASS. The optimized LLVM IR inlines `fib` into `main`, promotes all variables to SSA registers (0 `alloca`, 0 `store`), and preserves the input-dependent loop (`while.body1.i`). The `freeze i32` instruction on `atoi`'s return value safely handles potential undef values without altering semantics.
- Integer signedness, overflow, shifts, and comparisons: PASS. The source uses signed 32-bit integers. The optimized LLVM uses `icmp ugt` for the `> 46` check, which is safe because the preceding `lt_i32 n 0` check in `main` (compiled to `icmp slt` in raw LLVM) guarantees the value is non-negative. The `add i32` in the loop matches the source's `add_i32`. The final assembly uses `cmpl $0x2e, %eax` (unsigned `ja`) and `cmpl %ebx, %ecx` (signed `jle`), correctly matching the optimized IR.
- Calls, return values, ABI, stack alignment, and register use: PASS. The target assembly and disassembly show correct x86_64 SysV ABI usage: `rdi` for string pointer argument, `eax` for `atoi` return value, `rbx` as callee-saved register (saved with `pushq`/`popq`), and 16-byte stack alignment maintained. `main` returns `i32` in `eax` via `retq`.
- Memory safety, lifetime, leaks, and undefined behavior: PASS. The program uses a string literal in `.rodata` and passes it to `getenv`. The null check (`testq %rax, %rax; je`) prevents calling `atoi` on a null pointer. The `freeze` instruction in optimized LLVM prevents UB from propagating undef values. No dynamic memory allocation is performed.
- Target compatibility and native instruction validity: PASS. The target assembly specifies `x86_64-pc-linux-gnu` and uses standard instructions valid for the AMD EPYC 9V74 processor. The linked executable is a valid ELF64 binary.
- Compiler-generated overhead remaining in final native code: PASS. The optimization record confirms `fib` was inlined into `main`. The analysis JSON shows 0 `alloca` and 0 `store` in optimized LLVM. The final `main` function is 25 instructions with no unnecessary stack traffic or redundant computations.

## Blocking findings
None found.

## Non-blocking opportunities
- The `fib` algorithm uses a simple iterative loop. While optimal for space, it could be replaced with a closed-form formula or memoization if performance were critical, though this is a source-level algorithm choice, not a compiler overhead issue.
- The optimization record notes that loop vectorization was missed due to the loop carrying dependencies. This is expected for a Fibonacci sequence and does not represent a compiler defect.

## Suggested verification
- Execute the linked executable with `WEAVE_AUDIT_N=10` and verify the exit code is 55.
- Execute with `WEAVE_AUDIT_N=46` and verify the exit code is 1836311903 (F(46)).
- Execute with `WEAVE_AUDIT_N=47` and verify the exit code is 55 (fallback to 10).
- Execute with `WEAVE_AUDIT_N=-5` and verify the exit code is 55 (fallback to 10).
- Execute with `WEAVE_AUDIT_N` unset and verify the exit code is 55.

<details>
<summary>Raw model response</summary>

```text
OK
## Summary
The final native program for `docs/audit/fibonacci_runtime.weave` is correct, safe, ABI-valid, target-compatible, and free from avoidable compiler-generated overhead. The Weave source defines a runtime-input Fibonacci computation that intentionally resists constant folding. This semantic intent is preserved through WIR, raw LLVM, optimized LLVM, target assembly, and the linked executable. LLVM successfully inlines the `fib` function into `main`, promotes stack temporaries to registers, and emits a compact 25-instruction native `main` function that retains the input-dependent loop. All control-flow edges, signed comparisons, and arithmetic widths match the source semantics. The x86_64 ABI is respected, and no undefined behavior or memory unsafety is present.

## Verification matrix
- Source semantics and expected result: PASS. The Weave source (`fibonacci_runtime.weave`) defines a `fib` function with an input-dependent `while` loop and a `main` function that reads `WEAVE_AUDIT_N`, clamps the value to `[0, 46]` (defaulting to 10), and calls `fib`. The linked disassembly (`1150`-`119f`) contains the loop and calls to `getenv@plt` and `atoi@plt`, matching the expected runtime behavior.
- Weave-to-WIR semantic preservation: PASS. The WIR preserves all source constructs, including the `le_i32`, `add_i32`, `lt_i32`, and `gt_i32` operations, the `while` loop, and the `getenv`/`atoi` calls with correct pointer and integer types.
- WIR-to-raw-LLVM semantic preservation: PASS. The raw LLVM IR maps WIR operations to valid LLVM instructions (`icmp sle`, `add i32`, `icmp slt`, `icmp sgt`). Stack allocations (`alloca`) are used for local variables, and control flow matches the WIR structure.
- Raw LLVM validity, SSA, types, and control flow: PASS. The raw LLVM IR is valid, uses correct SSA form, and has well-formed basic blocks and control-flow edges. The analysis JSON confirms 0 `poison_uses` and 0 `undef_uses`.
- Optimized LLVM semantic preservation: PASS. The optimized LLVM IR inlines `fib` into `main`, promotes all variables to SSA registers (0 `alloca`, 0 `store`), and preserves the input-dependent loop (`while.body1.i`). The `freeze i32` instruction on `atoi`'s return value safely handles potential undef values without altering semantics.
- Integer signedness, overflow, shifts, and comparisons: PASS. The source uses signed 32-bit integers. The optimized LLVM uses `icmp ugt` for the `> 46` check, which is safe because the preceding `lt_i32 n 0` check in `main` (compiled to `icmp slt` in raw LLVM) guarantees the value is non-negative. The `add i32` in the loop matches the source's `add_i32`. The final assembly uses `cmpl $0x2e, %eax` (unsigned `ja`) and `cmpl %ebx, %ecx` (signed `jle`), correctly matching the optimized IR.
- Calls, return values, ABI, stack alignment, and register use: PASS. The target assembly and disassembly show correct x86_64 SysV ABI usage: `rdi` for string pointer argument, `eax` for `atoi` return value, `rbx` as callee-saved register (saved with `pushq`/`popq`), and 16-byte stack alignment maintained. `main` returns `i32` in `eax` via `retq`.
- Memory safety, lifetime, leaks, and undefined behavior: PASS. The program uses a string literal in `.rodata` and passes it to `getenv`. The null check (`testq %rax, %rax; je`) prevents calling `atoi` on a null pointer. The `freeze` instruction in optimized LLVM prevents UB from propagating undef values. No dynamic memory allocation is performed.
- Target compatibility and native instruction validity: PASS. The target assembly specifies `x86_64-pc-linux-gnu` and uses standard instructions valid for the AMD EPYC 9V74 processor. The linked executable is a valid ELF64 binary.
- Compiler-generated overhead remaining in final native code: PASS. The optimization record confirms `fib` was inlined into `main`. The analysis JSON shows 0 `alloca` and 0 `store` in optimized LLVM. The final `main` function is 25 instructions with no unnecessary stack traffic or redundant computations.

## Blocking findings
None found.

## Non-blocking opportunities
- The `fib` algorithm uses a simple iterative loop. While optimal for space, it could be replaced with a closed-form formula or memoization if performance were critical, though this is a source-level algorithm choice, not a compiler overhead issue.
- The optimization record notes that loop vectorization was missed due to the loop carrying dependencies. This is expected for a Fibonacci sequence and does not represent a compiler defect.

## Suggested verification
- Execute the linked executable with `WEAVE_AUDIT_N=10` and verify the exit code is 55.
- Execute with `WEAVE_AUDIT_N=46` and verify the exit code is 1836311903 (F(46)).
- Execute with `WEAVE_AUDIT_N=47` and verify the exit code is 55 (fallback to 10).
- Execute with `WEAVE_AUDIT_N=-5` and verify the exit code is 55 (fallback to 10).
- Execute with `WEAVE_AUDIT_N` unset and verify the exit code is 55.
```
</details>
