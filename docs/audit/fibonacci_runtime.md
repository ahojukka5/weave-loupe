# Weave Loupe Audit Report

## Verdict

- **Status:** OK
- **Code:** none
- **Reason:** No blocking defect found.

## Reproducibility

- **Audit timestamp (UTC):** `2026-07-27T17:28:32+00:00`
- **Audited source Git SHA:** `02af8912a0bcf503ecce0ad76f8eddd5c2fafd81`
- **Source tree state:** `clean`
- **Weave Loupe Git SHA:** `02af8912a0bcf503ecce0ad76f8eddd5c2fafd81`
- **weavec Git SHA:** `b7046aacc634283a7ae6e548984d00511dcc7776`
- **weavec binary SHA-256:** `96e78338d7ae0199646f78f4af6d4d3c25f2b027c8ddc7ab25bd3a2dfdfdea70`
- **weavec version:** `unavailable`
- **LLM model:** `z-ai/glm-5.2`
- **GitHub run ID:** `30289348756`
- **GitHub workflow SHA:** `b90f04499bc2bc1f464caee8d78eeb21e2bf31e3`

## Machine and running conditions

- **Operating system:** `Ubuntu 24.04.4 LTS`
- **Kernel:** `Linux 6.17.0-1020-azure`
- **Architecture:** `x86_64`
- **CPU:** `AMD EPYC 7763 64-Core Processor`
- **Logical CPUs:** `4`
- **Memory:** `16766410752` bytes
- **Python:** `3.12.13`
- **libc:** `glibc 2.39`

## Audited inputs

- `docs/audit/fibonacci_runtime.weave` — SHA-256 `6507f21700b5289ba78d6f5c6d7f42f5639ec74b07a9257134513c690911d6ca`

## Captured evidence

- `assembly` — SHA-256 `3f28a70f7e5cc20e23cd78a3697506388a2a1cf3caa1d78b3a09bef16da08662`
- `build_manifest` — SHA-256 `036f45f4e414d933072ceac37956f51f0dbc9b0d211fdb8eb593aa11c7a4dec8`
- `diagnostics` — SHA-256 `a40b573053cda943c381742ad672108b1c8985ecc97e2f21dfa604094e31ff63`
- `disassembly` — SHA-256 `a29e3b01123b2be31e0e139e56065f270da9877b5bf24b3590f6e01b8ee98cbb`
- `llvm` — SHA-256 `6545672c67c1c9a10e685a0fa116fa1dd496809d2a506f71a83f0e5527c718a4`
- `optimization_record` — SHA-256 `ab4f664ca6e7c09a2f5b048ed8645e5b6afeaf1a41b7e5b322d6b93add7b9266`
- `optimized_llvm` — SHA-256 `f184d1f2ffb3e8dbc8b6d2030612112f021c1dea6ffdafeb20e33f733c2849d2`
- `trace` — SHA-256 `b2b31cb4820d6e3e8eb29602a4ca1e1637f19953fa4ce2230d0a6f2d5d8e7878`
- `wir` — SHA-256 `5bdac66db258e51949b6cddbb8b13d0b3b02e042c295ef5d78e36affc0f24308`

## Complete compiler evidence

This section contains the exact evidence reviewed by the model so that the
source-to-native lowering can also be inspected manually.

### Weave source

```lisp
--- docs/audit/fibonacci_runtime.weave ---
; Runtime-input Weave Loupe audit corpus example.
; Reads WEAVE_AUDIT_N as a decimal integer in the inclusive range 0..46.
; Missing, malformed, or out-of-range input falls back to 10.
; Examples: unset or 10 -> 55, 12 -> 144, 20 -> 6765.
;
; Unlike fibonacci.weave, the compiler cannot know n at compile time. It may
; inline functions and promote loop variables to SSA, but an input-dependent
; Fibonacci computation must remain in optimized LLVM and native code.

(program
  (name "fibonacci-runtime")
  (version "0.1")

  (extern getenv
    (params (name ptr))
    (returns ptr))

  (fn parse_audit_n
    (params (text ptr))
    (returns i32)
    (do
      (if
        (condition
          (eq_ptr (param_get text) (const_null)))
        (then
          (do
            (return (const_i32 10))))
        (else
          (do)))

      (let first i32
        (load_u8 (param_get text)))
      (if
        (condition
          (lt_i32 (local_get first) (const_i32 48)))
        (then
          (do
            (return (const_i32 10))))
        (else
          (do)))
      (if
        (condition
          (gt_i32 (local_get first) (const_i32 57)))
        (then
          (do
            (return (const_i32 10))))
        (else
          (do)))

      (let tens i32
        (sub_i32 (local_get first) (const_i32 48)))
      (let second_ptr ptr
        (ptr_add (param_get text) (const_i64 1)))
      (let second i32
        (load_u8 (local_get second_ptr)))

      (if
        (condition
          (eq_i32 (local_get second) (const_i32 0)))
        (then
          (do
            (return (local_get tens))))
        (else
          (do)))
      (if
        (condition
          (lt_i32 (local_get second) (const_i32 48)))
        (then
          (do
            (return (const_i32 10))))
        (else
          (do)))
      (if
        (condition
          (gt_i32 (local_get second) (const_i32 57)))
        (then
          (do
            (return (const_i32 10))))
        (else
          (do)))

      (let third i32
        (load_u8
          (ptr_add (param_get text) (const_i64 2))))
      (if
        (condition
          (ne_i32 (local_get third) (const_i32 0)))
        (then
          (do
            (return (const_i32 10))))
        (else
          (do)))

      (let value i32
        (add_i32
          (mul_i32 (local_get tens) (const_i32 10))
          (sub_i32 (local_get second) (const_i32 48))))
      (if
        (condition
          (gt_i32 (local_get value) (const_i32 46)))
        (then
          (do
            (return (const_i32 10))))
        (else
          (do)))
      (return (local_get value))))

  (fn fib
    (params (n i32))
    (returns i32)
    (do
      (if
        (condition
          (le_i32 (param_get n) (const_i32 1)))
        (then
          (do
            (return (param_get n))))
        (else
          (do)))
      (let previous i32 (const_i32 0))
      (let current i32 (const_i32 1))
      (let index i32 (const_i32 2))
      (while
        (condition
          (le_i32 (local_get index) (param_get n)))
        (do
          (let next i32
            (add_i32 (local_get previous) (local_get current)))
          (set previous (local_get current))
          (set current (local_get next))
          (set index
            (add_i32 (local_get index) (const_i32 1)))))
      (return (local_get current))))

  (entry main
    (params)
    (returns i32)
    (do
      (let input ptr
        (call_ptr getenv
          (const_string_ptr "WEAVE_AUDIT_N")))
      (let n i32
        (call_i32 parse_audit_n (local_get input)))
      (return
        (call_i32 fib (local_get n))))))
```

### WIR

```lisp
(core-module
  (core-version 2)
  (decls
; weavec-source-file-v1 0 "docs/audit/fibonacci_runtime.weave"
    ; weavec-source-span-v1 0 526 583
(; weavec-source-span-v1 0 527 533
extern ; weavec-source-span-v1 0 534 540
getenv ; weavec-source-span-v1 0 545 564
(; weavec-source-span-v1 0 546 552
params ; weavec-source-span-v1 0 553 563
(; weavec-source-span-v1 0 554 558
name ; weavec-source-span-v1 0 559 562
ptr)) ; weavec-source-span-v1 0 569 582
(; weavec-source-span-v1 0 570 577
returns ; weavec-source-span-v1 0 578 581
ptr))
    ; weavec-source-span-v1 0 587 2632
(; weavec-source-span-v1 0 588 590
fn ; weavec-source-span-v1 0 591 604
parse_audit_n ; weavec-source-span-v1 0 609 628
(; weavec-source-span-v1 0 610 616
params ; weavec-source-span-v1 0 617 627
(; weavec-source-span-v1 0 618 622
text ; weavec-source-span-v1 0 623 626
ptr)) ; weavec-source-span-v1 0 633 646
(; weavec-source-span-v1 0 634 641
returns ; weavec-source-span-v1 0 642 645
i32) ; weavec-source-span-v1 0 651 2631
(do ; weavec-source-span-v1 0 661 830
(; weavec-source-span-v1 0 662 664
if ; weavec-source-span-v1 0 673 733
(; weavec-source-span-v1 0 674 683
condition ; weavec-source-span-v1 0 694 732
(; weavec-source-span-v1 0 695 701
eq_ptr ; weavec-source-span-v1 0 702 718
(; weavec-source-span-v1 0 703 712
param_get ; weavec-source-span-v1 0 713 717
text) ; weavec-source-span-v1 0 719 731
(; weavec-source-span-v1 0 720 730
const_null))) ; weavec-source-span-v1 0 742 799
(; weavec-source-span-v1 0 743 747
then ; weavec-source-span-v1 0 758 798
(do ; weavec-source-span-v1 0 774 797
(; weavec-source-span-v1 0 775 781
return ; weavec-source-span-v1 0 782 796
(; weavec-source-span-v1 0 783 792
const_i32 ; weavec-source-span-v1 0 793 795
10)))) ; weavec-source-span-v1 0 808 829
(; weavec-source-span-v1 0 809 813
else ; weavec-source-span-v1 0 824 828
(do))) ; weavec-source-span-v1 0 838 888
(let ; weavec-source-span-v1 0 843 848
first i32 ; weavec-source-span-v1 0 861 887
(; weavec-source-span-v1 0 862 869
load_u8 ; weavec-source-span-v1 0 870 886
(; weavec-source-span-v1 0 871 880
param_get ; weavec-source-span-v1 0 881 885
text))) ; weavec-source-span-v1 0 895 1067
(; weavec-source-span-v1 0 896 898
if ; weavec-source-span-v1 0 907 970
(; weavec-source-span-v1 0 908 917
condition ; weavec-source-span-v1 0 928 969
(; weavec-source-span-v1 0 929 935
lt_i32 ; weavec-source-span-v1 0 936 953
(; weavec-source-span-v1 0 937 946
local_get ; weavec-source-span-v1 0 947 952
first) ; weavec-source-span-v1 0 954 968
(; weavec-source-span-v1 0 955 964
const_i32 ; weavec-source-span-v1 0 965 967
48))) ; weavec-source-span-v1 0 979 1036
(; weavec-source-span-v1 0 980 984
then ; weavec-source-span-v1 0 995 1035
(do ; weavec-source-span-v1 0 1011 1034
(; weavec-source-span-v1 0 1012 1018
return ; weavec-source-span-v1 0 1019 1033
(; weavec-source-span-v1 0 1020 1029
const_i32 ; weavec-source-span-v1 0 1030 1032
10)))) ; weavec-source-span-v1 0 1045 1066
(; weavec-source-span-v1 0 1046 1050
else ; weavec-source-span-v1 0 1061 1065
(do))) ; weavec-source-span-v1 0 1074 1246
(; weavec-source-span-v1 0 1075 1077
if ; weavec-source-span-v1 0 1086 1149
(; weavec-source-span-v1 0 1087 1096
condition ; weavec-source-span-v1 0 1107 1148
(; weavec-source-span-v1 0 1108 1114
gt_i32 ; weavec-source-span-v1 0 1115 1132
(; weavec-source-span-v1 0 1116 1125
local_get ; weavec-source-span-v1 0 1126 1131
first) ; weavec-source-span-v1 0 1133 1147
(; weavec-source-span-v1 0 1134 1143
const_i32 ; weavec-source-span-v1 0 1144 1146
57))) ; weavec-source-span-v1 0 1158 1215
(; weavec-source-span-v1 0 1159 1163
then ; weavec-source-span-v1 0 1174 1214
(do ; weavec-source-span-v1 0 1190 1213
(; weavec-source-span-v1 0 1191 1197
return ; weavec-source-span-v1 0 1198 1212
(; weavec-source-span-v1 0 1199 1208
const_i32 ; weavec-source-span-v1 0 1209 1211
10)))) ; weavec-source-span-v1 0 1224 1245
(; weavec-source-span-v1 0 1225 1229
else ; weavec-source-span-v1 0 1240 1244
(do))) ; weavec-source-span-v1 0 1254 1319
(let ; weavec-source-span-v1 0 1259 1263
tens i32 ; weavec-source-span-v1 0 1276 1318
(; weavec-source-span-v1 0 1277 1284
sub_i32 ; weavec-source-span-v1 0 1285 1302
(; weavec-source-span-v1 0 1286 1295
local_get ; weavec-source-span-v1 0 1296 1301
first) ; weavec-source-span-v1 0 1303 1317
(; weavec-source-span-v1 0 1304 1313
const_i32 ; weavec-source-span-v1 0 1314 1316
48))) ; weavec-source-span-v1 0 1326 1395
(let ; weavec-source-span-v1 0 1331 1341
second_ptr ptr ; weavec-source-span-v1 0 1354 1394
(; weavec-source-span-v1 0 1355 1362
ptr_add ; weavec-source-span-v1 0 1363 1379
(; weavec-source-span-v1 0 1364 1373
param_get ; weavec-source-span-v1 0 1374 1378
text) ; weavec-source-span-v1 0 1380 1393
(; weavec-source-span-v1 0 1381 1390
const_i64 ; weavec-source-span-v1 0 1391 1392
1))) ; weavec-source-span-v1 0 1402 1459
(let ; weavec-source-span-v1 0 1407 1413
second i32 ; weavec-source-span-v1 0 1426 1458
(; weavec-source-span-v1 0 1427 1434
load_u8 ; weavec-source-span-v1 0 1435 1457
(; weavec-source-span-v1 0 1436 1445
local_get ; weavec-source-span-v1 0 1446 1456
second_ptr))) ; weavec-source-span-v1 0 1467 1641
(; weavec-source-span-v1 0 1468 1470
if ; weavec-source-span-v1 0 1479 1542
(; weavec-source-span-v1 0 1480 1489
condition ; weavec-source-span-v1 0 1500 1541
(; weavec-source-span-v1 0 1501 1507
eq_i32 ; weavec-source-span-v1 0 1508 1526
(; weavec-source-span-v1 0 1509 1518
local_get ; weavec-source-span-v1 0 1519 1525
second) ; weavec-source-span-v1 0 1527 1540
(; weavec-source-span-v1 0 1528 1537
const_i32 ; weavec-source-span-v1 0 1538 1539
0))) ; weavec-source-span-v1 0 1551 1610
(; weavec-source-span-v1 0 1552 1556
then ; weavec-source-span-v1 0 1567 1609
(do ; weavec-source-span-v1 0 1583 1608
(; weavec-source-span-v1 0 1584 1590
return ; weavec-source-span-v1 0 1591 1607
(; weavec-source-span-v1 0 1592 1601
local_get ; weavec-source-span-v1 0 1602 1606
tens)))) ; weavec-source-span-v1 0 1619 1640
(; weavec-source-span-v1 0 1620 1624
else ; weavec-source-span-v1 0 1635 1639
(do))) ; weavec-source-span-v1 0 1648 1821
(; weavec-source-span-v1 0 1649 1651
if ; weavec-source-span-v1 0 1660 1724
(; weavec-source-span-v1 0 1661 1670
condition ; weavec-source-span-v1 0 1681 1723
(; weavec-source-span-v1 0 1682 1688
lt_i32 ; weavec-source-span-v1 0 1689 1707
(; weavec-source-span-v1 0 1690 1699
local_get ; weavec-source-span-v1 0 1700 1706
second) ; weavec-source-span-v1 0 1708 1722
(; weavec-source-span-v1 0 1709 1718
const_i32 ; weavec-source-span-v1 0 1719 1721
48))) ; weavec-source-span-v1 0 1733 1790
(; weavec-source-span-v1 0 1734 1738
then ; weavec-source-span-v1 0 1749 1789
(do ; weavec-source-span-v1 0 1765 1788
(; weavec-source-span-v1 0 1766 1772
return ; weavec-source-span-v1 0 1773 1787
(; weavec-source-span-v1 0 1774 1783
const_i32 ; weavec-source-span-v1 0 1784 1786
10)))) ; weavec-source-span-v1 0 1799 1820
(; weavec-source-span-v1 0 1800 1804
else ; weavec-source-span-v1 0 1815 1819
(do))) ; weavec-source-span-v1 0 1828 2001
(; weavec-source-span-v1 0 1829 1831
if ; weavec-source-span-v1 0 1840 1904
(; weavec-source-span-v1 0 1841 1850
condition ; weavec-source-span-v1 0 1861 1903
(; weavec-source-span-v1 0 1862 1868
gt_i32 ; weavec-source-span-v1 0 1869 1887
(; weavec-source-span-v1 0 1870 1879
local_get ; weavec-source-span-v1 0 1880 1886
second) ; weavec-source-span-v1 0 1888 1902
(; weavec-source-span-v1 0 1889 1898
const_i32 ; weavec-source-span-v1 0 1899 1901
57))) ; weavec-source-span-v1 0 1913 1970
(; weavec-source-span-v1 0 1914 1918
then ; weavec-source-span-v1 0 1929 1969
(do ; weavec-source-span-v1 0 1945 1968
(; weavec-source-span-v1 0 1946 1952
return ; weavec-source-span-v1 0 1953 1967
(; weavec-source-span-v1 0 1954 1963
const_i32 ; weavec-source-span-v1 0 1964 1966
10)))) ; weavec-source-span-v1 0 1979 2000
(; weavec-source-span-v1 0 1980 1984
else ; weavec-source-span-v1 0 1995 1999
(do))) ; weavec-source-span-v1 0 2009 2093
(let ; weavec-source-span-v1 0 2014 2019
third i32 ; weavec-source-span-v1 0 2032 2092
(; weavec-source-span-v1 0 2033 2040
load_u8 ; weavec-source-span-v1 0 2051 2091
(; weavec-source-span-v1 0 2052 2059
ptr_add ; weavec-source-span-v1 0 2060 2076
(; weavec-source-span-v1 0 2061 2070
param_get ; weavec-source-span-v1 0 2071 2075
text) ; weavec-source-span-v1 0 2077 2090
(; weavec-source-span-v1 0 2078 2087
const_i64 ; weavec-source-span-v1 0 2088 2089
2)))) ; weavec-source-span-v1 0 2100 2271
(; weavec-source-span-v1 0 2101 2103
if ; weavec-source-span-v1 0 2112 2174
(; weavec-source-span-v1 0 2113 2122
condition ; weavec-source-span-v1 0 2133 2173
(; weavec-source-span-v1 0 2134 2140
ne_i32 ; weavec-source-span-v1 0 2141 2158
(; weavec-source-span-v1 0 2142 2151
local_get ; weavec-source-span-v1 0 2152 2157
third) ; weavec-source-span-v1 0 2159 2172
(; weavec-source-span-v1 0 2160 2169
const_i32 ; weavec-source-span-v1 0 2170 2171
0))) ; weavec-source-span-v1 0 2183 2240
(; weavec-source-span-v1 0 2184 2188
then ; weavec-source-span-v1 0 2199 2239
(do ; weavec-source-span-v1 0 2215 2238
(; weavec-source-span-v1 0 2216 2222
return ; weavec-source-span-v1 0 2223 2237
(; weavec-source-span-v1 0 2224 2233
const_i32 ; weavec-source-span-v1 0 2234 2236
10)))) ; weavec-source-span-v1 0 2249 2270
(; weavec-source-span-v1 0 2250 2254
else ; weavec-source-span-v1 0 2265 2269
(do))) ; weavec-source-span-v1 0 2279 2418
(let ; weavec-source-span-v1 0 2284 2289
value i32 ; weavec-source-span-v1 0 2302 2417
(; weavec-source-span-v1 0 2303 2310
add_i32 ; weavec-source-span-v1 0 2321 2362
(; weavec-source-span-v1 0 2322 2329
mul_i32 ; weavec-source-span-v1 0 2330 2346
(; weavec-source-span-v1 0 2331 2340
local_get ; weavec-source-span-v1 0 2341 2345
tens) ; weavec-source-span-v1 0 2347 2361
(; weavec-source-span-v1 0 2348 2357
const_i32 ; weavec-source-span-v1 0 2358 2360
10)) ; weavec-source-span-v1 0 2373 2416
(; weavec-source-span-v1 0 2374 2381
sub_i32 ; weavec-source-span-v1 0 2382 2400
(; weavec-source-span-v1 0 2383 2392
local_get ; weavec-source-span-v1 0 2393 2399
second) ; weavec-source-span-v1 0 2401 2415
(; weavec-source-span-v1 0 2402 2411
const_i32 ; weavec-source-span-v1 0 2412 2414
48)))) ; weavec-source-span-v1 0 2425 2597
(; weavec-source-span-v1 0 2426 2428
if ; weavec-source-span-v1 0 2437 2500
(; weavec-source-span-v1 0 2438 2447
condition ; weavec-source-span-v1 0 2458 2499
(; weavec-source-span-v1 0 2459 2465
gt_i32 ; weavec-source-span-v1 0 2466 2483
(; weavec-source-span-v1 0 2467 2476
local_get ; weavec-source-span-v1 0 2477 2482
value) ; weavec-source-span-v1 0 2484 2498
(; weavec-source-span-v1 0 2485 2494
const_i32 ; weavec-source-span-v1 0 2495 2497
46))) ; weavec-source-span-v1 0 2509 2566
(; weavec-source-span-v1 0 2510 2514
then ; weavec-source-span-v1 0 2525 2565
(do ; weavec-source-span-v1 0 2541 2564
(; weavec-source-span-v1 0 2542 2548
return ; weavec-source-span-v1 0 2549 2563
(; weavec-source-span-v1 0 2550 2559
const_i32 ; weavec-source-span-v1 0 2560 2562
10)))) ; weavec-source-span-v1 0 2575 2596
(; weavec-source-span-v1 0 2576 2580
else ; weavec-source-span-v1 0 2591 2595
(do))) ; weavec-source-span-v1 0 2604 2630
(; weavec-source-span-v1 0 2605 2611
return ; weavec-source-span-v1 0 2612 2629
(; weavec-source-span-v1 0 2613 2622
local_get ; weavec-source-span-v1 0 2623 2628
value))))
    ; weavec-source-span-v1 0 2636 3361
(; weavec-source-span-v1 0 2637 2639
fn ; weavec-source-span-v1 0 2640 2643
fib ; weavec-source-span-v1 0 2648 2664
(; weavec-source-span-v1 0 2649 2655
params ; weavec-source-span-v1 0 2656 2663
(; weavec-source-span-v1 0 2657 2658
n ; weavec-source-span-v1 0 2659 2662
i32)) ; weavec-source-span-v1 0 2669 2682
(; weavec-source-span-v1 0 2670 2677
returns ; weavec-source-span-v1 0 2678 2681
i32) ; weavec-source-span-v1 0 2687 3360
(do ; weavec-source-span-v1 0 2697 2863
(; weavec-source-span-v1 0 2698 2700
if ; weavec-source-span-v1 0 2709 2767
(; weavec-source-span-v1 0 2710 2719
condition ; weavec-source-span-v1 0 2730 2766
(; weavec-source-span-v1 0 2731 2737
le_i32 ; weavec-source-span-v1 0 2738 2751
(; weavec-source-span-v1 0 2739 2748
param_get ; weavec-source-span-v1 0 2749 2750
n) ; weavec-source-span-v1 0 2752 2765
(; weavec-source-span-v1 0 2753 2762
const_i32 ; weavec-source-span-v1 0 2763 2764
1))) ; weavec-source-span-v1 0 2776 2832
(; weavec-source-span-v1 0 2777 2781
then ; weavec-source-span-v1 0 2792 2831
(do ; weavec-source-span-v1 0 2808 2830
(; weavec-source-span-v1 0 2809 2815
return ; weavec-source-span-v1 0 2816 2829
(; weavec-source-span-v1 0 2817 2826
param_get ; weavec-source-span-v1 0 2827 2828
n)))) ; weavec-source-span-v1 0 2841 2862
(; weavec-source-span-v1 0 2842 2846
else ; weavec-source-span-v1 0 2857 2861
(do))) ; weavec-source-span-v1 0 2870 2902
(let ; weavec-source-span-v1 0 2875 2883
previous i32 ; weavec-source-span-v1 0 2888 2901
(; weavec-source-span-v1 0 2889 2898
const_i32 ; weavec-source-span-v1 0 2899 2900
0)) ; weavec-source-span-v1 0 2909 2940
(let ; weavec-source-span-v1 0 2914 2921
current i32 ; weavec-source-span-v1 0 2926 2939
(; weavec-source-span-v1 0 2927 2936
const_i32 ; weavec-source-span-v1 0 2937 2938
1)) ; weavec-source-span-v1 0 2947 2976
(let ; weavec-source-span-v1 0 2952 2957
index i32 ; weavec-source-span-v1 0 2962 2975
(; weavec-source-span-v1 0 2963 2972
const_i32 ; weavec-source-span-v1 0 2973 2974
2)) ; weavec-source-span-v1 0 2983 3324
(; weavec-source-span-v1 0 2984 2989
while ; weavec-source-span-v1 0 2998 3060
(; weavec-source-span-v1 0 2999 3008
condition ; weavec-source-span-v1 0 3019 3059
(; weavec-source-span-v1 0 3020 3026
le_i32 ; weavec-source-span-v1 0 3027 3044
(; weavec-source-span-v1 0 3028 3037
local_get ; weavec-source-span-v1 0 3038 3043
index) ; weavec-source-span-v1 0 3045 3058
(; weavec-source-span-v1 0 3046 3055
param_get ; weavec-source-span-v1 0 3056 3057
n))) ; weavec-source-span-v1 0 3069 3323
(do ; weavec-source-span-v1 0 3083 3160
(let ; weavec-source-span-v1 0 3088 3092
next i32 ; weavec-source-span-v1 0 3109 3159
(; weavec-source-span-v1 0 3110 3117
add_i32 ; weavec-source-span-v1 0 3118 3138
(; weavec-source-span-v1 0 3119 3128
local_get ; weavec-source-span-v1 0 3129 3137
previous) ; weavec-source-span-v1 0 3139 3158
(; weavec-source-span-v1 0 3140 3149
local_get ; weavec-source-span-v1 0 3150 3157
current))) ; weavec-source-span-v1 0 3171 3205
(; weavec-source-span-v1 0 3172 3175
set ; weavec-source-span-v1 0 3176 3184
previous ; weavec-source-span-v1 0 3185 3204
(; weavec-source-span-v1 0 3186 3195
local_get ; weavec-source-span-v1 0 3196 3203
current)) ; weavec-source-span-v1 0 3216 3246
(; weavec-source-span-v1 0 3217 3220
set ; weavec-source-span-v1 0 3221 3228
current ; weavec-source-span-v1 0 3229 3245
(; weavec-source-span-v1 0 3230 3239
local_get ; weavec-source-span-v1 0 3240 3244
next)) ; weavec-source-span-v1 0 3257 3322
(; weavec-source-span-v1 0 3258 3261
set ; weavec-source-span-v1 0 3262 3267
index ; weavec-source-span-v1 0 3280 3321
(; weavec-source-span-v1 0 3281 3288
add_i32 ; weavec-source-span-v1 0 3289 3306
(; weavec-source-span-v1 0 3290 3299
local_get ; weavec-source-span-v1 0 3300 3305
index) ; weavec-source-span-v1 0 3307 3320
(; weavec-source-span-v1 0 3308 3317
const_i32 ; weavec-source-span-v1 0 3318 3319
1))))) ; weavec-source-span-v1 0 3331 3359
(; weavec-source-span-v1 0 3332 3338
return ; weavec-source-span-v1 0 3339 3358
(; weavec-source-span-v1 0 3340 3349
local_get ; weavec-source-span-v1 0 3350 3357
current))))
; weavec-source-span-v1 0 3365 3631
    (fn ; weavec-source-span-v1 0 3372 3376
main ; weavec-source-span-v1 0 3381 3389
(; weavec-source-span-v1 0 3382 3388
params) ; weavec-source-span-v1 0 3394 3407
(; weavec-source-span-v1 0 3395 3402
returns ; weavec-source-span-v1 0 3403 3406
i32) ; weavec-source-span-v1 0 3412 3630
(do ; weavec-source-span-v1 0 3422 3508
(let ; weavec-source-span-v1 0 3427 3432
input ptr ; weavec-source-span-v1 0 3445 3507
(; weavec-source-span-v1 0 3446 3454
call_ptr ; weavec-source-span-v1 0 3455 3461
getenv ; weavec-source-span-v1 0 3472 3506
(; weavec-source-span-v1 0 3473 3489
const_string_ptr ; weavec-source-span-v1 0 3491 3504
"WEAVE_AUDIT_N"))) ; weavec-source-span-v1 0 3515 3577
(let ; weavec-source-span-v1 0 3520 3521
n i32 ; weavec-source-span-v1 0 3534 3576
(; weavec-source-span-v1 0 3535 3543
call_i32 ; weavec-source-span-v1 0 3544 3557
parse_audit_n ; weavec-source-span-v1 0 3558 3575
(; weavec-source-span-v1 0 3559 3568
local_get ; weavec-source-span-v1 0 3569 3574
input))) ; weavec-source-span-v1 0 3584 3629
(; weavec-source-span-v1 0 3585 3591
return ; weavec-source-span-v1 0 3600 3628
(; weavec-source-span-v1 0 3601 3609
call_i32 ; weavec-source-span-v1 0 3610 3613
fib ; weavec-source-span-v1 0 3614 3627
(; weavec-source-span-v1 0 3615 3624
local_get ; weavec-source-span-v1 0 3625 3626
n)))))
  )
)
```

### Raw LLVM IR

```llvm
; generated by weavec
; source: /tmp/weavec-build-Qe47hn/program.wir
; core-version: 2

; declarations

declare ptr @getenv(ptr)

; string literals

@.str0 = private unnamed_addr constant [14 x i8] c"WEAVE_AUDIT_N\00"

; weave.source kind=function index=0 bytes=3365..3631 wir-bytes=15540..16855 path="docs/audit/fibonacci_runtime.weave"
; function: main
; params: none
; returns: i32
define i32 @main() {
entry:
; weave.source kind=statement index=0 bytes=3422..3508 wir-bytes=15864..16184 path="docs/audit/fibonacci_runtime.weave"
  %t0 = getelementptr [14 x i8], ptr @.str0, i64 0, i64 0
  %t1 = call ptr @getenv(ptr %t0)
  ; let input
; weave.source kind=statement index=0 bytes=3515..3577 wir-bytes=16221..16527 path="docs/audit/fibonacci_runtime.weave"
  %t2 = call i32 @parse_audit_n(ptr %t1)
  ; let n
; weave.source kind=statement index=0 bytes=3584..3629 wir-bytes=16564..16853 path="docs/audit/fibonacci_runtime.weave"
  ; return
  %t3 = call i32 @fib(i32 %t2)
  ret i32 %t3
}

; weave.source kind=function index=0 bytes=587..2632 wir-bytes=571..11337 path="docs/audit/fibonacci_runtime.weave"
; function: parse_audit_n
; params: ptr
; returns: i32
define internal i32 @parse_audit_n(ptr %text) {
entry:
; weave.source kind=statement index=0 bytes=661..830 wir-bytes=1036..1853 path="docs/audit/fibonacci_runtime.weave"
  ; if condition
  %t0 = icmp eq ptr %text, null
  br i1 %t0, label %then, label %endif
then:
  ; then
; weave.source kind=statement index=0 bytes=774..797 wir-bytes=1577..1736 path="docs/audit/fibonacci_runtime.weave"
  ; return
  ret i32 10
endif:
; weave.source kind=statement index=0 bytes=838..888 wir-bytes=1888..2134 path="docs/audit/fibonacci_runtime.weave"
  %t1 = load i8, ptr %text
  %t2 = zext i8 %t1 to i32
  ; let first
; weave.source kind=statement index=0 bytes=895..1067 wir-bytes=2170..3042 path="docs/audit/fibonacci_runtime.weave"
  ; if condition
  %t3 = icmp slt i32 %t2, 48
  br i1 %t3, label %then1, label %endif1
then1:
  ; then
; weave.source kind=statement index=0 bytes=1011..1034 wir-bytes=2752..2919 path="docs/audit/fibonacci_runtime.weave"
  ; return
  ret i32 10
endif1:
; weave.source kind=statement index=0 bytes=1074..1246 wir-bytes=3079..3977 path="docs/audit/fibonacci_runtime.weave"
  ; if condition
  %t4 = icmp sgt i32 %t2, 57
  br i1 %t4, label %then2, label %endif2
then2:
  ; then
; weave.source kind=statement index=0 bytes=1190..1213 wir-bytes=3687..3854 path="docs/audit/fibonacci_runtime.weave"
  ; return
  ret i32 10
endif2:
; weave.source kind=statement index=0 bytes=1254..1319 wir-bytes=4014..4395 path="docs/audit/fibonacci_runtime.weave"
  %t5 = sub i32 %t2, 48
  ; let tens
; weave.source kind=statement index=0 bytes=1326..1395 wir-bytes=4432..4817 path="docs/audit/fibonacci_runtime.weave"
  %t6 = getelementptr i8, ptr %text, i64 1
  ; let second_ptr
; weave.source kind=statement index=0 bytes=1402..1459 wir-bytes=4854..5119 path="docs/audit/fibonacci_runtime.weave"
  %t7 = load i8, ptr %t6
  %t8 = zext i8 %t7 to i32
  ; let second
; weave.source kind=statement index=0 bytes=1467..1641 wir-bytes=5156..6056 path="docs/audit/fibonacci_runtime.weave"
  ; if condition
  %t9 = icmp eq i32 %t8, 0
  br i1 %t9, label %then3, label %endif3
then3:
  ; then
; weave.source kind=statement index=0 bytes=1583..1608 wir-bytes=5764..5933 path="docs/audit/fibonacci_runtime.weave"
  ; return
  ret i32 %t5
endif3:
; weave.source kind=statement index=0 bytes=1648..1821 wir-bytes=6093..6992 path="docs/audit/fibonacci_runtime.weave"
  ; if condition
  %t10 = icmp slt i32 %t8, 48
  br i1 %t10, label %then4, label %endif4
then4:
  ; then
; weave.source kind=statement index=0 bytes=1765..1788 wir-bytes=6702..6869 path="docs/audit/fibonacci_runtime.weave"
  ; return
  ret i32 10
endif4:
; weave.source kind=statement index=0 bytes=1828..2001 wir-bytes=7029..7928 path="docs/audit/fibonacci_runtime.weave"
  ; if condition
  %t11 = icmp sgt i32 %t8, 57
  br i1 %t11, label %then5, label %endif5
then5:
  ; then
; weave.source kind=statement index=0 bytes=1945..1968 wir-bytes=7638..7805 path="docs/audit/fibonacci_runtime.weave"
  ; return
  ret i32 10
endif5:
; weave.source kind=statement index=0 bytes=2009..2093 wir-bytes=7965..8427 path="docs/audit/fibonacci_runtime.weave"
  %t12 = getelementptr i8, ptr %text, i64 2
  %t13 = load i8, ptr %t12
  %t14 = zext i8 %t13 to i32
  ; let third
; weave.source kind=statement index=0 bytes=2100..2271 wir-bytes=8464..9361 path="docs/audit/fibonacci_runtime.weave"
  ; if condition
  %t15 = icmp ne i32 %t14, 0
  br i1 %t15, label %then6, label %endif6
then6:
  ; then
; weave.source kind=statement index=0 bytes=2215..2238 wir-bytes=9071..9238 path="docs/audit/fibonacci_runtime.weave"
  ; return
  ret i32 10
endif6:
; weave.source kind=statement index=0 bytes=2279..2418 wir-bytes=9398..10193 path="docs/audit/fibonacci_runtime.weave"
  %t16 = mul i32 %t5, 10
  %t17 = sub i32 %t8, 48
  %t18 = add i32 %t16, %t17
  ; let value
; weave.source kind=statement index=0 bytes=2425..2597 wir-bytes=10230..11128 path="docs/audit/fibonacci_runtime.weave"
  ; if condition
  %t19 = icmp sgt i32 %t18, 46
  br i1 %t19, label %then7, label %endif7
then7:
  ; then
; weave.source kind=statement index=0 bytes=2541..2564 wir-bytes=10838..11005 path="docs/audit/fibonacci_runtime.weave"
  ; return
  ret i32 10
endif7:
; weave.source kind=statement index=0 bytes=2604..2630 wir-bytes=11165..11335 path="docs/audit/fibonacci_runtime.weave"
  ; return
  ret i32 %t18
}

; weave.source kind=function index=0 bytes=2636..3361 wir-bytes=11378..15499 path="docs/audit/fibonacci_runtime.weave"
; function: fib
; params: i32
; returns: i32
define internal i32 @fib(i32 %n) {
entry:
  %previous.addr = alloca i32
  %current.addr = alloca i32
  %index.addr = alloca i32
; weave.source kind=statement index=0 bytes=2697..2863 wir-bytes=11853..12745 path="docs/audit/fibonacci_runtime.weave"
  ; if condition
  %t0 = icmp sle i32 %n, 1
  br i1 %t0, label %then, label %endif
then:
  ; then
; weave.source kind=statement index=0 bytes=2808..2830 wir-bytes=12456..12622 path="docs/audit/fibonacci_runtime.weave"
  ; return
  ret i32 %n
endif:
; weave.source kind=statement index=0 bytes=2870..2902 wir-bytes=12782..12958 path="docs/audit/fibonacci_runtime.weave"
  ; let previous
  store i32 0, ptr %previous.addr
; weave.source kind=statement index=0 bytes=2909..2940 wir-bytes=12995..13170 path="docs/audit/fibonacci_runtime.weave"
  ; let current
  store i32 1, ptr %current.addr
; weave.source kind=statement index=0 bytes=2947..2976 wir-bytes=13207..13380 path="docs/audit/fibonacci_runtime.weave"
  ; let index
  store i32 2, ptr %index.addr
; weave.source kind=statement index=0 bytes=2983..3324 wir-bytes=13417..15288 path="docs/audit/fibonacci_runtime.weave"
  ; while condition
  br label %while.cond1
while.cond1:
  %t1 = load i32, ptr %index.addr
  %t2 = icmp sle i32 %t1, %n
  br i1 %t2, label %while.body1, label %while.end1
while.body1:
  ; while body
; weave.source kind=statement index=0 bytes=3083..3160 wir-bytes=13949..14338 path="docs/audit/fibonacci_runtime.weave"
  %t3 = load i32, ptr %previous.addr
  %t4 = load i32, ptr %current.addr
  %t5 = add i32 %t3, %t4
  ; let next
; weave.source kind=statement index=0 bytes=3171..3205 wir-bytes=14375..14589 path="docs/audit/fibonacci_runtime.weave"
  ; set previous
  %t6 = load i32, ptr %current.addr
  store i32 %t6, ptr %previous.addr
; weave.source kind=statement index=0 bytes=3216..3246 wir-bytes=14626..14836 path="docs/audit/fibonacci_runtime.weave"
  ; set current
  store i32 %t5, ptr %current.addr
; weave.source kind=statement index=0 bytes=3257..3322 wir-bytes=14873..15286 path="docs/audit/fibonacci_runtime.weave"
  ; set index
  %t7 = load i32, ptr %index.addr
  %t8 = add i32 %t7, 1
  store i32 %t8, ptr %index.addr
  br label %while.cond1
while.end1:
; weave.source kind=statement index=0 bytes=3331..3359 wir-bytes=15325..15497 path="docs/audit/fibonacci_runtime.weave"
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

; Function Attrs: nofree nounwind memory(read)
define i32 @main() local_unnamed_addr #0 {
entry:
  %t1 = tail call ptr @getenv(ptr nonnull @.str0)
  %t0.i = icmp eq ptr %t1, null
  br i1 %t0.i, label %while.body1.i.preheader, label %endif.i

endif.i:                                          ; preds = %entry
  %t1.i = load i8, ptr %t1, align 1
  %0 = add i8 %t1.i, -58
  %or.cond.i = icmp ult i8 %0, -10
  br i1 %or.cond.i, label %while.body1.i.preheader, label %endif2.i

endif2.i:                                         ; preds = %endif.i
  %t2.i = zext nneg i8 %t1.i to i32
  %t5.i = add nsw i32 %t2.i, -48
  %t6.i = getelementptr i8, ptr %t1, i64 1
  %t7.i = load i8, ptr %t6.i, align 1
  %t8.i = zext i8 %t7.i to i32
  %t9.i = icmp eq i8 %t7.i, 0
  br i1 %t9.i, label %parse_audit_n.exit, label %endif3.i

endif3.i:                                         ; preds = %endif2.i
  %1 = add i8 %t7.i, -58
  %or.cond1.i = icmp ult i8 %1, -10
  br i1 %or.cond1.i, label %while.body1.i.preheader, label %endif5.i

endif5.i:                                         ; preds = %endif3.i
  %t12.i = getelementptr i8, ptr %t1, i64 2
  %t13.i = load i8, ptr %t12.i, align 1
  %t15.not.i = icmp eq i8 %t13.i, 0
  br i1 %t15.not.i, label %endif6.i, label %while.body1.i.preheader

endif6.i:                                         ; preds = %endif5.i
  %t16.i = mul nuw nsw i32 %t5.i, 10
  %t17.i = add nsw i32 %t16.i, -48
  %t18.i = add nsw i32 %t17.i, %t8.i
  %t19.i = icmp sgt i32 %t18.i, 46
  br i1 %t19.i, label %while.body1.i.preheader, label %parse_audit_n.exit

parse_audit_n.exit:                               ; preds = %endif6.i, %endif2.i
  %common.ret.op.i = phi i32 [ %t5.i, %endif2.i ], [ %t18.i, %endif6.i ]
  %t0.i1 = icmp slt i32 %common.ret.op.i, 2
  br i1 %t0.i1, label %fib.exit, label %while.body1.i.preheader

while.body1.i.preheader:                          ; preds = %endif6.i, %endif5.i, %endif3.i, %endif.i, %entry, %parse_audit_n.exit
  %common.ret.op.i7 = phi i32 [ %common.ret.op.i, %parse_audit_n.exit ], [ 10, %entry ], [ 10, %endif.i ], [ 10, %endif3.i ], [ 10, %endif5.i ], [ 10, %endif6.i ]
  %2 = add nsw i32 %common.ret.op.i7, -1
  %3 = add nsw i32 %common.ret.op.i7, -2
  %xtraiter = and i32 %2, 7
  %4 = icmp ult i32 %3, 7
  br i1 %4, label %fib.exit.loopexit.unr-lcssa, label %while.body1.i.preheader.new

while.body1.i.preheader.new:                      ; preds = %while.body1.i.preheader
  %unroll_iter = and i32 %2, -8
  br label %while.body1.i

while.body1.i:                                    ; preds = %while.body1.i, %while.body1.i.preheader.new
  %current.addr.05.i = phi i32 [ 1, %while.body1.i.preheader.new ], [ %t5.i2.7, %while.body1.i ]
  %previous.addr.04.i = phi i32 [ 0, %while.body1.i.preheader.new ], [ %t5.i2.6, %while.body1.i ]
  %niter = phi i32 [ 0, %while.body1.i.preheader.new ], [ %niter.next.7, %while.body1.i ]
  %t5.i2 = add i32 %previous.addr.04.i, %current.addr.05.i
  %t5.i2.1 = add i32 %current.addr.05.i, %t5.i2
  %t5.i2.2 = add i32 %t5.i2, %t5.i2.1
  %t5.i2.3 = add i32 %t5.i2.1, %t5.i2.2
  %t5.i2.4 = add i32 %t5.i2.2, %t5.i2.3
  %t5.i2.5 = add i32 %t5.i2.3, %t5.i2.4
  %t5.i2.6 = add i32 %t5.i2.4, %t5.i2.5
  %t5.i2.7 = add i32 %t5.i2.5, %t5.i2.6
  %niter.next.7 = add i32 %niter, 8
  %niter.ncmp.7 = icmp eq i32 %niter.next.7, %unroll_iter
  br i1 %niter.ncmp.7, label %fib.exit.loopexit.unr-lcssa, label %while.body1.i

fib.exit.loopexit.unr-lcssa:                      ; preds = %while.body1.i, %while.body1.i.preheader
  %t5.i2.lcssa.ph = phi i32 [ undef, %while.body1.i.preheader ], [ %t5.i2.7, %while.body1.i ]
  %current.addr.05.i.unr = phi i32 [ 1, %while.body1.i.preheader ], [ %t5.i2.7, %while.body1.i ]
  %previous.addr.04.i.unr = phi i32 [ 0, %while.body1.i.preheader ], [ %t5.i2.6, %while.body1.i ]
  %lcmp.mod.not = icmp eq i32 %xtraiter, 0
  br i1 %lcmp.mod.not, label %fib.exit, label %while.body1.i.epil

while.body1.i.epil:                               ; preds = %fib.exit.loopexit.unr-lcssa, %while.body1.i.epil
  %current.addr.05.i.epil = phi i32 [ %t5.i2.epil, %while.body1.i.epil ], [ %current.addr.05.i.unr, %fib.exit.loopexit.unr-lcssa ]
  %previous.addr.04.i.epil = phi i32 [ %current.addr.05.i.epil, %while.body1.i.epil ], [ %previous.addr.04.i.unr, %fib.exit.loopexit.unr-lcssa ]
  %epil.iter = phi i32 [ %epil.iter.next, %while.body1.i.epil ], [ 0, %fib.exit.loopexit.unr-lcssa ]
  %t5.i2.epil = add i32 %previous.addr.04.i.epil, %current.addr.05.i.epil
  %epil.iter.next = add i32 %epil.iter, 1
  %epil.iter.cmp.not = icmp eq i32 %epil.iter.next, %xtraiter
  br i1 %epil.iter.cmp.not, label %fib.exit, label %while.body1.i.epil, !llvm.loop !0

fib.exit:                                         ; preds = %fib.exit.loopexit.unr-lcssa, %while.body1.i.epil, %parse_audit_n.exit
  %common.ret.op.i4 = phi i32 [ %common.ret.op.i, %parse_audit_n.exit ], [ %t5.i2.lcssa.ph, %fib.exit.loopexit.unr-lcssa ], [ %t5.i2.epil, %while.body1.i.epil ]
  ret i32 %common.ret.op.i4
}

attributes #0 = { nofree nounwind memory(read) }

!0 = distinct !{!0, !1}
!1 = !{!"llvm.loop.unroll.disable"}
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
	pushq	%rax
	leaq	.L.str0(%rip), %rdi
	callq	getenv@PLT
	movl	$10, %edx
	testq	%rax, %rax
	je	.LBB0_7
# %bb.1:                                # %endif.i
	movq	%rax, %rcx
	movzbl	(%rax), %eax
	leal	-58(%rax), %esi
	cmpb	$-10, %sil
	jb	.LBB0_7
# %bb.2:                                # %endif2.i
	movzbl	1(%rcx), %esi
	addl	$-48, %eax
	testl	%esi, %esi
	je	.LBB0_6
# %bb.3:                                # %endif3.i
	leal	-58(%rsi), %edi
	cmpb	$-10, %dil
	jb	.LBB0_7
# %bb.4:                                # %endif5.i
	cmpb	$0, 2(%rcx)
	jne	.LBB0_7
# %bb.5:                                # %endif6.i
	leal	(%rax,%rax,4), %eax
	leal	-48(%rsi,%rax,2), %eax
	cmpl	$46, %eax
	jg	.LBB0_7
.LBB0_6:                                # %parse_audit_n.exit
	movl	%eax, %edx
	cmpl	$2, %eax
	jl	.LBB0_13
.LBB0_7:                                # %while.body1.i.preheader
	leal	-1(%rdx), %esi
	addl	$-2, %edx
	movl	%esi, %ecx
	andl	$7, %ecx
	cmpl	$7, %edx
	jae	.LBB0_9
# %bb.8:
	xorl	%edx, %edx
	movl	$1, %eax
	jmp	.LBB0_11
.LBB0_9:                                # %while.body1.i.preheader.new
	andl	$-8, %esi
	movl	$1, %eax
	xorl	%edx, %edx
	.p2align	4, 0x90
.LBB0_10:                               # %while.body1.i
                                        # =>This Inner Loop Header: Depth=1
	addl	%eax, %edx
	addl	%edx, %eax
	addl	%eax, %edx
	addl	%edx, %eax
	addl	%eax, %edx
	addl	%edx, %eax
	addl	%eax, %edx
	addl	%edx, %eax
	addl	$-8, %esi
	jne	.LBB0_10
.LBB0_11:                               # %fib.exit.loopexit.unr-lcssa
	testl	%ecx, %ecx
	je	.LBB0_13
	.p2align	4, 0x90
.LBB0_12:                               # %while.body1.i.epil
                                        # =>This Inner Loop Header: Depth=1
	movl	%eax, %esi
	movl	%edx, %eax
	addl	%esi, %eax
	decl	%ecx
	movl	%esi, %edx
	jne	.LBB0_12
.LBB0_13:                               # %fib.exit
                                        # kill: def $eax killed $eax killed $rax
	popq	%rcx
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

Disassembly of section .plt.got:

0000000000001040 <__cxa_finalize@plt>:
    1040: ff 25 9a 2f 00 00            	jmpq	*0x2f9a(%rip)           # 0x3fe0 <getenv@GLIBC_2.2.5+0x3fe0>
    1046: 66 90                        	nop

Disassembly of section .text:

0000000000001050 <_start>:
    1050: f3 0f 1e fa                  	endbr64
    1054: 31 ed                        	xorl	%ebp, %ebp
    1056: 49 89 d1                     	movq	%rdx, %r9
    1059: 5e                           	popq	%rsi
    105a: 48 89 e2                     	movq	%rsp, %rdx
    105d: 48 83 e4 f0                  	andq	$-0x10, %rsp
    1061: 50                           	pushq	%rax
    1062: 54                           	pushq	%rsp
    1063: 45 31 c0                     	xorl	%r8d, %r8d
    1066: 31 c9                        	xorl	%ecx, %ecx
    1068: 48 8d 3d d1 00 00 00         	leaq	0xd1(%rip), %rdi        # 0x1140 <main>
    106f: ff 15 4b 2f 00 00            	callq	*0x2f4b(%rip)           # 0x3fc0 <getenv@GLIBC_2.2.5+0x3fc0>
    1075: f4                           	hlt
    1076: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

0000000000001080 <deregister_tm_clones>:
    1080: 48 8d 3d 89 2f 00 00         	leaq	0x2f89(%rip), %rdi      # 0x4010 <completed.0>
    1087: 48 8d 05 82 2f 00 00         	leaq	0x2f82(%rip), %rax      # 0x4010 <completed.0>
    108e: 48 39 f8                     	cmpq	%rdi, %rax
    1091: 74 15                        	je	0x10a8 <deregister_tm_clones+0x28>
    1093: 48 8b 05 2e 2f 00 00         	movq	0x2f2e(%rip), %rax      # 0x3fc8 <getenv@GLIBC_2.2.5+0x3fc8>
    109a: 48 85 c0                     	testq	%rax, %rax
    109d: 74 09                        	je	0x10a8 <deregister_tm_clones+0x28>
    109f: ff e0                        	jmpq	*%rax
    10a1: 0f 1f 80 00 00 00 00         	nopl	(%rax)
    10a8: c3                           	retq
    10a9: 0f 1f 80 00 00 00 00         	nopl	(%rax)

00000000000010b0 <register_tm_clones>:
    10b0: 48 8d 3d 59 2f 00 00         	leaq	0x2f59(%rip), %rdi      # 0x4010 <completed.0>
    10b7: 48 8d 35 52 2f 00 00         	leaq	0x2f52(%rip), %rsi      # 0x4010 <completed.0>
    10be: 48 29 fe                     	subq	%rdi, %rsi
    10c1: 48 89 f0                     	movq	%rsi, %rax
    10c4: 48 c1 ee 3f                  	shrq	$0x3f, %rsi
    10c8: 48 c1 f8 03                  	sarq	$0x3, %rax
    10cc: 48 01 c6                     	addq	%rax, %rsi
    10cf: 48 d1 fe                     	sarq	%rsi
    10d2: 74 14                        	je	0x10e8 <register_tm_clones+0x38>
    10d4: 48 8b 05 fd 2e 00 00         	movq	0x2efd(%rip), %rax      # 0x3fd8 <getenv@GLIBC_2.2.5+0x3fd8>
    10db: 48 85 c0                     	testq	%rax, %rax
    10de: 74 08                        	je	0x10e8 <register_tm_clones+0x38>
    10e0: ff e0                        	jmpq	*%rax
    10e2: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
    10e8: c3                           	retq
    10e9: 0f 1f 80 00 00 00 00         	nopl	(%rax)

00000000000010f0 <__do_global_dtors_aux>:
    10f0: f3 0f 1e fa                  	endbr64
    10f4: 80 3d 15 2f 00 00 00         	cmpb	$0x0, 0x2f15(%rip)      # 0x4010 <completed.0>
    10fb: 75 2b                        	jne	0x1128 <__do_global_dtors_aux+0x38>
    10fd: 55                           	pushq	%rbp
    10fe: 48 83 3d da 2e 00 00 00      	cmpq	$0x0, 0x2eda(%rip)      # 0x3fe0 <getenv@GLIBC_2.2.5+0x3fe0>
    1106: 48 89 e5                     	movq	%rsp, %rbp
    1109: 74 0c                        	je	0x1117 <__do_global_dtors_aux+0x27>
    110b: 48 8b 3d f6 2e 00 00         	movq	0x2ef6(%rip), %rdi      # 0x4008 <__dso_handle>
    1112: e8 29 ff ff ff               	callq	0x1040 <__cxa_finalize@plt>
    1117: e8 64 ff ff ff               	callq	0x1080 <deregister_tm_clones>
    111c: c6 05 ed 2e 00 00 01         	movb	$0x1, 0x2eed(%rip)      # 0x4010 <completed.0>
    1123: 5d                           	popq	%rbp
    1124: c3                           	retq
    1125: 0f 1f 00                     	nopl	(%rax)
    1128: c3                           	retq
    1129: 0f 1f 80 00 00 00 00         	nopl	(%rax)

0000000000001130 <frame_dummy>:
    1130: f3 0f 1e fa                  	endbr64
    1134: e9 77 ff ff ff               	jmp	0x10b0 <register_tm_clones>
    1139: 0f 1f 80 00 00 00 00         	nopl	(%rax)

0000000000001140 <main>:
    1140: 50                           	pushq	%rax
    1141: 48 8d 3d b8 0e 00 00         	leaq	0xeb8(%rip), %rdi       # 0x2000 <getenv@GLIBC_2.2.5+0x2000>
    1148: e8 e3 fe ff ff               	callq	0x1030 <getenv@plt>
    114d: ba 0a 00 00 00               	movl	$0xa, %edx
    1152: 48 85 c0                     	testq	%rax, %rax
    1155: 74 3c                        	je	0x1193 <main+0x53>
    1157: 48 89 c1                     	movq	%rax, %rcx
    115a: 0f b6 00                     	movzbl	(%rax), %eax
    115d: 8d 70 c6                     	leal	-0x3a(%rax), %esi
    1160: 40 80 fe f6                  	cmpb	$-0xa, %sil
    1164: 72 2d                        	jb	0x1193 <main+0x53>
    1166: 0f b6 71 01                  	movzbl	0x1(%rcx), %esi
    116a: 83 c0 d0                     	addl	$-0x30, %eax
    116d: 85 f6                        	testl	%esi, %esi
    116f: 74 1b                        	je	0x118c <main+0x4c>
    1171: 8d 7e c6                     	leal	-0x3a(%rsi), %edi
    1174: 40 80 ff f6                  	cmpb	$-0xa, %dil
    1178: 72 19                        	jb	0x1193 <main+0x53>
    117a: 80 79 02 00                  	cmpb	$0x0, 0x2(%rcx)
    117e: 75 13                        	jne	0x1193 <main+0x53>
    1180: 8d 04 80                     	leal	(%rax,%rax,4), %eax
    1183: 8d 44 46 d0                  	leal	-0x30(%rsi,%rax,2), %eax
    1187: 83 f8 2e                     	cmpl	$0x2e, %eax
    118a: 7f 07                        	jg	0x1193 <main+0x53>
    118c: 89 c2                        	movl	%eax, %edx
    118e: 83 f8 02                     	cmpl	$0x2, %eax
    1191: 7c 59                        	jl	0x11ec <main+0xac>
    1193: 8d 72 ff                     	leal	-0x1(%rdx), %esi
    1196: 83 c2 fe                     	addl	$-0x2, %edx
    1199: 89 f1                        	movl	%esi, %ecx
    119b: 83 e1 07                     	andl	$0x7, %ecx
    119e: 83 fa 07                     	cmpl	$0x7, %edx
    11a1: 73 09                        	jae	0x11ac <main+0x6c>
    11a3: 31 d2                        	xorl	%edx, %edx
    11a5: b8 01 00 00 00               	movl	$0x1, %eax
    11aa: eb 29                        	jmp	0x11d5 <main+0x95>
    11ac: 83 e6 f8                     	andl	$-0x8, %esi
    11af: b8 01 00 00 00               	movl	$0x1, %eax
    11b4: 31 d2                        	xorl	%edx, %edx
    11b6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)
    11c0: 01 c2                        	addl	%eax, %edx
    11c2: 01 d0                        	addl	%edx, %eax
    11c4: 01 c2                        	addl	%eax, %edx
    11c6: 01 d0                        	addl	%edx, %eax
    11c8: 01 c2                        	addl	%eax, %edx
    11ca: 01 d0                        	addl	%edx, %eax
    11cc: 01 c2                        	addl	%eax, %edx
    11ce: 01 d0                        	addl	%edx, %eax
    11d0: 83 c6 f8                     	addl	$-0x8, %esi
    11d3: 75 eb                        	jne	0x11c0 <main+0x80>
    11d5: 85 c9                        	testl	%ecx, %ecx
    11d7: 74 13                        	je	0x11ec <main+0xac>
    11d9: 0f 1f 80 00 00 00 00         	nopl	(%rax)
    11e0: 89 c6                        	movl	%eax, %esi
    11e2: 89 d0                        	movl	%edx, %eax
    11e4: 01 f0                        	addl	%esi, %eax
    11e6: ff c9                        	decl	%ecx
    11e8: 89 f2                        	movl	%esi, %edx
    11ea: 75 f4                        	jne	0x11e0 <main+0xa0>
    11ec: 59                           	popq	%rcx
    11ed: c3                           	retq

Disassembly of section .fini:

00000000000011f0 <_fini>:
    11f0: f3 0f 1e fa                  	endbr64
    11f4: 48 83 ec 08                  	subq	$0x8, %rsp
    11f8: 48 83 c4 08                  	addq	$0x8, %rsp
    11fc: c3                           	retq
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
--- !Passed
Pass:            inline
Name:            Inlined
Function:        main
Args:
  - String:          ''''
  - Callee:          parse_audit_n
  - String:          ''' inlined into '''
  - Caller:          main
  - String:          ''''
  - String:          ' with '
  - String:          '(cost='
  - Cost:            '-14930'
  - String:          ', threshold='
  - Threshold:       '250'
  - String:          ')'
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
--- !Passed
Pass:            loop-unroll
Name:            PartialUnrolled
Function:        main
Args:
  - String:          'unrolled loop by a factor of '
  - UnrollCount:     '8'
  - String:          ' with run-time trip count'
...

# weavec optimization stage: target-codegen
--- !Analysis
Pass:            size-info
Name:            IRSizeChange
Function:        main
Args:
  - Pass:            Canonicalize natural loops
  - String:          ': IR instruction count changed from '
  - IRInstrsBefore:  '65'
  - String:          ' to '
  - IRInstrsAfter:   '68'
  - String:          '; Delta: '
  - DeltaInstrCount: '3'
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
  - IRInstrsBefore:  '65'
  - String:          ' to '
  - IRInstrsAfter:   '68'
  - String:          '; Delta: '
  - DeltaInstrCount: '3'
...
--- !Analysis
Pass:            size-info
Name:            IRSizeChange
Function:        main
Args:
  - Pass:            CodeGen Prepare
  - String:          ': IR instruction count changed from '
  - IRInstrsBefore:  '68'
  - String:          ' to '
  - IRInstrsAfter:   '67'
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
  - IRInstrsBefore:  '68'
  - String:          ' to '
  - IRInstrsAfter:   '67'
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
  - MIInstrsAfter:   '92'
  - String:          '; Delta: '
  - Delta:           '92'
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
  - MIInstrsBefore:  '92'
  - String:          ' to '
  - MIInstrsAfter:   '88'
  - String:          '; Delta: '
  - Delta:           '-4'
...
--- !Analysis
Pass:            size-info
Name:            FunctionMISizeChange
Function:        main
Args:
  - Pass:            Process Implicit Definitions
  - String:          ': Function: '
  - Function:        main
  - String:          ': '
  - String:          'MI Instruction count changed from '
  - MIInstrsBefore:  '88'
  - String:          ' to '
  - MIInstrsAfter:   '84'
  - String:          '; Delta: '
  - Delta:           '-4'
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
  - MIInstrsBefore:  '84'
  - String:          ' to '
  - MIInstrsAfter:   '113'
  - String:          '; Delta: '
  - Delta:           '29'
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
  - MIInstrsBefore:  '113'
  - String:          ' to '
  - MIInstrsAfter:   '135'
  - String:          '; Delta: '
  - Delta:           '22'
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
  - MIInstrsBefore:  '135'
  - String:          ' to '
  - MIInstrsAfter:   '71'
  - String:          '; Delta: '
  - Delta:           '-64'
...
--- !Missed
Pass:            regalloc
Name:            LoopSpillReloadCopies
Function:        main
Args:
  - NumVRCopies:     '3'
  - String:          ' virtual registers copies '
  - TotalCopiesCost: '5.593506e+01'
  - String:          ' total copies cost '
  - String:          generated in loop
...
--- !Missed
Pass:            regalloc
Name:            SpillReloadCopies
Function:        main
Args:
  - NumVRCopies:     '6'
  - String:          ' virtual registers copies '
  - TotalCopiesCost: '5.800281e+01'
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
  - MIInstrsBefore:  '71'
  - String:          ' to '
  - MIInstrsAfter:   '70'
  - String:          '; Delta: '
  - Delta:           '-1'
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
  - Pass:            Control Flow Optimizer
  - String:          ': Function: '
  - Function:        main
  - String:          ': '
  - String:          'MI Instruction count changed from '
  - MIInstrsBefore:  '70'
  - String:          ' to '
  - MIInstrsAfter:   '60'
  - String:          '; Delta: '
  - Delta:           '-10'
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
  - INST_:           '6'
  - String:          "\n"
...
--- !Analysis
Pass:            asm-printer
Name:            InstructionMix
Function:        main
Args:
  - String:          'BasicBlock: '
  - BasicBlock:      endif.i
  - String:          "\n"
  - String:          ''
  - String:          ': '
  - INST_:           '5'
  - String:          "\n"
...
--- !Analysis
Pass:            asm-printer
Name:            InstructionMix
Function:        main
Args:
  - String:          'BasicBlock: '
  - BasicBlock:      endif2.i
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
  - BasicBlock:      endif3.i
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
  - BasicBlock:      endif5.i
  - String:          "\n"
  - String:          ''
  - String:          ': '
  - INST_:           '2'
  - String:          "\n"
...
--- !Analysis
Pass:            asm-printer
Name:            InstructionMix
Function:        main
Args:
  - String:          'BasicBlock: '
  - BasicBlock:      endif6.i
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
  - BasicBlock:      parse_audit_n.exit
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
  - INST_:           '6'
  - String:          "\n"
...
--- !Analysis
Pass:            asm-printer
Name:            InstructionMix
Function:        main
Args:
  - String:          'BasicBlock: '
  - BasicBlock:      ''
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
  - BasicBlock:      while.body1.i.preheader.new
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
  - INST_:           '10'
  - String:          "\n"
...
--- !Analysis
Pass:            asm-printer
Name:            InstructionMix
Function:        main
Args:
  - String:          'BasicBlock: '
  - BasicBlock:      fib.exit.loopexit.unr-lcssa
  - String:          "\n"
  - String:          ''
  - String:          ': '
  - INST_:           '2'
  - String:          "\n"
...
--- !Analysis
Pass:            asm-printer
Name:            InstructionMix
Function:        main
Args:
  - String:          'BasicBlock: '
  - BasicBlock:      while.body1.i.epil
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
  - NumInstructions: '59'
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
    "add": 3,
    "alloca": 3,
    "anonymous_ssa_lines": 0,
    "basic_blocks": 24,
    "br": 12,
    "call": 3,
    "functions": 3,
    "icmp": 10,
    "identity_adds": 0,
    "instructions": 67,
    "invoke": 0,
    "load": 9,
    "mul": 1,
    "numeric_blocks": 0,
    "phi": 0,
    "poison_uses": 0,
    "provenance_comments": 40,
    "ret": 12,
    "sdiv": 0,
    "select": 0,
    "store": 6,
    "sub": 2,
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
      "getenv@plt": {
        "direct_calls": [],
        "indirect_calls": 0,
        "instructions": 3,
        "padding_instructions": 0
      },
      "main": {
        "direct_calls": [
          "getenv@plt"
        ],
        "indirect_calls": 0,
        "instructions": 59,
        "padding_instructions": 2
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
    "add": 18,
    "alloca": 0,
    "anonymous_ssa_lines": 10,
    "basic_blocks": 13,
    "br": 12,
    "call": 1,
    "functions": 1,
    "icmp": 11,
    "identity_adds": 0,
    "instructions": 65,
    "invoke": 0,
    "load": 3,
    "mul": 1,
    "numeric_blocks": 0,
    "phi": 12,
    "poison_uses": 0,
    "provenance_comments": 0,
    "ret": 1,
    "sdiv": 0,
    "select": 0,
    "store": 0,
    "sub": 0,
    "switch": 0,
    "udiv": 0,
    "undef_uses": 1
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
  "output": "/tmp/loupe-audit-lhxkjym8/.audit.loupe.udzocvlo/artifacts/program",
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
The final native program is correct, safe, ABI-valid, target-compatible, and free from avoidable compiler-generated overhead. The Weave source implements a runtime-input Fibonacci computation with input validation and fallback. WIR preserves the source semantics. Raw LLVM IR is valid SSA with correct control flow and memory operations. Optimized LLVM inlines `parse_audit_n` and `fib` into `main`, promotes loop variables to SSA, and unrolls the Fibonacci loop by a factor of 8 while preserving the input-dependent computation. Target assembly and linked executable disassembly match the optimized LLVM semantics, use the correct x86-64 System V ABI, and contain no remaining compiler-generated overhead.

## Verification matrix
- Source semantics and expected result: PASS. The Weave source (`docs/audit/fibonacci_runtime.weave`) reads `WEAVE_AUDIT_N`, parses it as a decimal integer in 0..46 with fallback to 10, and computes Fibonacci iteratively. Expected results: unset or 10 -> 55, 12 -> 144, 20 -> 6765.
- Weave-to-WIR semantic preservation: PASS. WIR contains all source functions (`parse_audit_n`, `fib`, `main`) with matching control flow, operations, and source spans.
- WIR-to-raw-LLVM semantic preservation: PASS. Raw LLVM IR translates WIR operations directly: `load_u8` becomes `load i8` + `zext`, `ptr_add` becomes `getelementptr i8`, comparisons use `icmp`, and the `while` loop uses explicit `while.cond`/`while.body`/`while.end` blocks.
- Raw LLVM validity, SSA, types, and control flow: PASS. SSA is valid, types are consistent (`i32`, `ptr`, `i8`), and control flow edges are well-formed. `fib` uses allocas for loop variables, which is valid IR.
- Optimized LLVM semantic preservation: PASS. Optimized LLVM inlines both functions, promotes `fib` loop variables to SSA `phi` nodes, and unrolls the loop by 8. The input-dependent computation remains, satisfying the source requirement.
- Integer signedness, overflow, shifts, and comparisons: PASS. Comparisons use signed `icmp` predicates (`slt`, `sgt`, `sle`) matching source semantics. `fib` uses `add i32` which is correct for n ≤ 46 (max Fibonacci value 1836311903, fits in signed 32-bit). The optimized LLVM uses `add nsw` where safe.
- Calls, return values, ABI, stack alignment, and register use: PASS. `main` returns `i32` in `%eax` per x86-64 System V ABI. `getenv` is called with string pointer in `%rdi`. Stack is 16-byte aligned via `pushq %rax` (8 bytes) + return address (8 bytes). Return uses `popq %rcx; retq`.
- Memory safety, lifetime, leaks, and undefined behavior: PASS. No dynamic allocation. `getenv` result is null-checked. String literal is statically allocated. No out-of-bounds access: parser checks first byte, then second, then third sequentially with early returns.
- Target compatibility and native instruction validity: PASS. Target triple is `x86_64-pc-linux-gnu`. Instructions are valid x86-64. Linked executable disassembly matches assembly and runs on the specified AMD EPYC 7763 / Ubuntu 24.04 target.
- Compiler-generated overhead remaining in final native code: PASS. No overhead remains. Loop unrolling is beneficial. The `fib` loop is compact (8 adds per iteration in unrolled loop, 1 add per iteration in epilogue). No spills, no redundant operations.

## Blocking findings
None found.

## Non-blocking opportunities
- The raw LLVM IR uses `alloca` for `previous`, `current`, and `index` in `fib`, causing stack traffic. This is eliminated in optimized LLVM via SSA promotion and is not a defect.
- The loop vectorizer could not vectorize the Fibonacci loop due to the non-reduction value used outside the loop. This is inherent to the Fibonacci recurrence and not a compiler defect.
- The `fib` function could use a closed-form formula or memoization, but this is a source-level algorithm choice, not a compiler-generated overhead issue.

## Suggested verification
- Test with `WEAVE_AUDIT_N=0` (expect 0), `WEAVE_AUDIT_N=1` (expect 1), `WEAVE_AUDIT_N=46` (expect 1836311903).
- Test with malformed input: `WEAVE_AUDIT_N=abc` (expect 55), `WEAVE_AUDIT_N=47` (expect 55), `WEAVE_AUDIT_N=-1` (expect 55).
- Test with unset `WEAVE_AUDIT_N` (expect 55).
- Verify stack alignment at `main` entry using a debugger to confirm 16-byte alignment before `callq getenv@PLT`.

<details>
<summary>Raw model response</summary>

```text
OK
## Summary
The final native program is correct, safe, ABI-valid, target-compatible, and free from avoidable compiler-generated overhead. The Weave source implements a runtime-input Fibonacci computation with input validation and fallback. WIR preserves the source semantics. Raw LLVM IR is valid SSA with correct control flow and memory operations. Optimized LLVM inlines `parse_audit_n` and `fib` into `main`, promotes loop variables to SSA, and unrolls the Fibonacci loop by a factor of 8 while preserving the input-dependent computation. Target assembly and linked executable disassembly match the optimized LLVM semantics, use the correct x86-64 System V ABI, and contain no remaining compiler-generated overhead.

## Verification matrix
- Source semantics and expected result: PASS. The Weave source (`docs/audit/fibonacci_runtime.weave`) reads `WEAVE_AUDIT_N`, parses it as a decimal integer in 0..46 with fallback to 10, and computes Fibonacci iteratively. Expected results: unset or 10 -> 55, 12 -> 144, 20 -> 6765.
- Weave-to-WIR semantic preservation: PASS. WIR contains all source functions (`parse_audit_n`, `fib`, `main`) with matching control flow, operations, and source spans.
- WIR-to-raw-LLVM semantic preservation: PASS. Raw LLVM IR translates WIR operations directly: `load_u8` becomes `load i8` + `zext`, `ptr_add` becomes `getelementptr i8`, comparisons use `icmp`, and the `while` loop uses explicit `while.cond`/`while.body`/`while.end` blocks.
- Raw LLVM validity, SSA, types, and control flow: PASS. SSA is valid, types are consistent (`i32`, `ptr`, `i8`), and control flow edges are well-formed. `fib` uses allocas for loop variables, which is valid IR.
- Optimized LLVM semantic preservation: PASS. Optimized LLVM inlines both functions, promotes `fib` loop variables to SSA `phi` nodes, and unrolls the loop by 8. The input-dependent computation remains, satisfying the source requirement.
- Integer signedness, overflow, shifts, and comparisons: PASS. Comparisons use signed `icmp` predicates (`slt`, `sgt`, `sle`) matching source semantics. `fib` uses `add i32` which is correct for n ≤ 46 (max Fibonacci value 1836311903, fits in signed 32-bit). The optimized LLVM uses `add nsw` where safe.
- Calls, return values, ABI, stack alignment, and register use: PASS. `main` returns `i32` in `%eax` per x86-64 System V ABI. `getenv` is called with string pointer in `%rdi`. Stack is 16-byte aligned via `pushq %rax` (8 bytes) + return address (8 bytes). Return uses `popq %rcx; retq`.
- Memory safety, lifetime, leaks, and undefined behavior: PASS. No dynamic allocation. `getenv` result is null-checked. String literal is statically allocated. No out-of-bounds access: parser checks first byte, then second, then third sequentially with early returns.
- Target compatibility and native instruction validity: PASS. Target triple is `x86_64-pc-linux-gnu`. Instructions are valid x86-64. Linked executable disassembly matches assembly and runs on the specified AMD EPYC 7763 / Ubuntu 24.04 target.
- Compiler-generated overhead remaining in final native code: PASS. No overhead remains. Loop unrolling is beneficial. The `fib` loop is compact (8 adds per iteration in unrolled loop, 1 add per iteration in epilogue). No spills, no redundant operations.

## Blocking findings
None found.

## Non-blocking opportunities
- The raw LLVM IR uses `alloca` for `previous`, `current`, and `index` in `fib`, causing stack traffic. This is eliminated in optimized LLVM via SSA promotion and is not a defect.
- The loop vectorizer could not vectorize the Fibonacci loop due to the non-reduction value used outside the loop. This is inherent to the Fibonacci recurrence and not a compiler defect.
- The `fib` function could use a closed-form formula or memoization, but this is a source-level algorithm choice, not a compiler-generated overhead issue.

## Suggested verification
- Test with `WEAVE_AUDIT_N=0` (expect 0), `WEAVE_AUDIT_N=1` (expect 1), `WEAVE_AUDIT_N=46` (expect 1836311903).
- Test with malformed input: `WEAVE_AUDIT_N=abc` (expect 55), `WEAVE_AUDIT_N=47` (expect 55), `WEAVE_AUDIT_N=-1` (expect 55).
- Test with unset `WEAVE_AUDIT_N` (expect 55).
- Verify stack alignment at `main` entry using a debugger to confirm 16-byte alignment before `callq getenv@PLT`.
```
</details>
