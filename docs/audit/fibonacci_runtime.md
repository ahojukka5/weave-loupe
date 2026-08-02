# Weave Loupe Audit Report

## Verdict

- **Status:** OK
- **Code:** none
- **Reason:** No blocking defect found.

## Reproducibility

- **Report content SHA-256:** `1060600247c38f16dfd5c28b15e29c5b92c28541cd1283bbf17d46f1b376dcc9`
- **Audit timestamp (UTC):** `2026-08-02T23:55:59+00:00`
- **Re-audit no later than (UTC):** `2026-09-01T23:55:59+00:00`
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
- **LLM prompt SHA-256:** `a633561fe2b48efccfa4889d9ffae42e79d1312347f9edea77c2c61ee5d26a19`
- **LLM request SHA-256:** `d7e344d87da3b32f63260932fb340981789023d7c25506eadc68f79fb2abb9a7`
- **Provider-reported model:** `z-ai/glm-5.2`
- **Provider response ID:** `chatcmpl-a938672c-7090-4abc-afbf-ca7df77283a9`
- **Provider system fingerprint:** `unavailable`
- **Provider finish reason:** `stop`
- **Provider created (Unix):** `1785715083`
- **Provider prompt tokens:** `11845`
- **Provider completion tokens:** `1515`
- **Provider total tokens:** `13360`
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

- Source `docs/audit/fibonacci_runtime.weave` — SHA-256 `a0df013d2e54ac1426498c7fda686d113ae4ca4f7371fe3836c490ccf9343ba4` — 1779 bytes
- Runtime matrix `docs/audit/fibonacci_runtime.audit.json` — SHA-256 `dc8e5b6d2d6234628a045cdf49a535825fd337815af4d3fa5f53adfc59c0d7d2`

## Captured evidence

- `assembly` — SHA-256 `355551c6d11759a2137d794f6154bee9f187aff00d09f7f13887d82a052f3bf1`
- `build_manifest` — SHA-256 `99f69f032cd59b169e6e713372d6f2d52f09bd865351b1699594ea5984f450f1`
- `diagnostics` — SHA-256 `a40b573053cda943c381742ad672108b1c8985ecc97e2f21dfa604094e31ff63`
- `disassembly` — SHA-256 `fc79aff611b518050aabf8fba9f4e4d9206bbb333c222fa01363938355cb582a`
- `executable` — SHA-256 `8096a9e86313b02d5038903d99f134a5e00416c11de2752492f204fc927fec8d`
- `llvm` — SHA-256 `d5435d2d17b6fd4c0e5131f2a74ab57684b5accefefca51b349d651c0cb2b006`
- `optimization_record` — SHA-256 `c1eed531ffbbd0e9d7c3558ecea6e951283dcb7e51ce4ebf7c1144aa66d37c6d`
- `optimized_llvm` — SHA-256 `7bda6a3ae32ec72bf1ac4f39971bba88d5f34fff09f56798c9cdbbf76414598e`
- `trace` — SHA-256 `c93c225da4447178c911c30bbeb170036679a5508fff214878cd7aef5013a3b8`
- `wir` — SHA-256 `071f042e6b7c27df63e03cc4dcc83f39b6061c37ad6802a417bde46133d70fb5`

## Model review coverage and requests

- **Review format:** `weave-loupe-review-plan-v1`
- **Review mode:** `staged`
- **Token estimator:** `utf8-byte-upper-bound-v1`
- **Estimated complete review tokens:** `352756`
- **Request count:** `14`
- **Maximum total tokens:** `524288`
- **Maximum request tokens:** `98304`
- **Maximum artifact tokens:** `262144`
- **Artifact-review completion tokens:** `1024`

### Artifact coverage

#### `metadata` — Reproducibility metadata

- Language: `json`
- UTF-8 bytes: `10623`
- Estimated tokens: `10639`
- SHA-256: `cf0c0073d052678d50154c75c438540e03e36164ac73cc1a44f04857e49e98dc`
- Complete coverage: `True`
- Covered ranges: `metadata:[0, 10623)@cf0c0073d052678d50154c75c438540e03e36164ac73cc1a44f04857e49e98dc`

#### `source` — Weave source

- Language: `lisp`
- UTF-8 bytes: `1822`
- Estimated tokens: `1838`
- SHA-256: `344883c033044766e2bfbac4a1bf838b9e07900faffb15f9fe919da6fe69b759`
- Complete coverage: `True`
- Covered ranges: `source:[0, 1822)@344883c033044766e2bfbac4a1bf838b9e07900faffb15f9fe919da6fe69b759`

#### `wir` — WIR review projection

- Language: `lisp`
- UTF-8 bytes: `1269`
- Estimated tokens: `1285`
- SHA-256: `66955504c5683801f61dc176cc98d0c0c27909698197099712ef53956b70d471`
- Complete coverage: `True`
- Covered ranges: `wir:[0, 1269)@66955504c5683801f61dc176cc98d0c0c27909698197099712ef53956b70d471`

#### `raw_llvm` — Raw LLVM IR

- Language: `llvm`
- UTF-8 bytes: `5767`
- Estimated tokens: `5783`
- SHA-256: `d5435d2d17b6fd4c0e5131f2a74ab57684b5accefefca51b349d651c0cb2b006`
- Complete coverage: `True`
- Covered ranges: `raw_llvm:[0, 5767)@d5435d2d17b6fd4c0e5131f2a74ab57684b5accefefca51b349d651c0cb2b006`

#### `optimized_llvm` — Optimized LLVM IR

- Language: `llvm`
- UTF-8 bytes: `2227`
- Estimated tokens: `2243`
- SHA-256: `7bda6a3ae32ec72bf1ac4f39971bba88d5f34fff09f56798c9cdbbf76414598e`
- Complete coverage: `True`
- Covered ranges: `optimized_llvm:[0, 2227)@7bda6a3ae32ec72bf1ac4f39971bba88d5f34fff09f56798c9cdbbf76414598e`

#### `assembly` — Target assembly

- Language: `asm`
- UTF-8 bytes: `1262`
- Estimated tokens: `1278`
- SHA-256: `355551c6d11759a2137d794f6154bee9f187aff00d09f7f13887d82a052f3bf1`
- Complete coverage: `True`
- Covered ranges: `assembly:[0, 1262)@355551c6d11759a2137d794f6154bee9f187aff00d09f7f13887d82a052f3bf1`

#### `disassembly` — Linked executable disassembly

- Language: `asm`
- UTF-8 bytes: `7537`
- Estimated tokens: `7553`
- SHA-256: `fc79aff611b518050aabf8fba9f4e4d9206bbb333c222fa01363938355cb582a`
- Complete coverage: `True`
- Covered ranges: `disassembly:[0, 7537)@fc79aff611b518050aabf8fba9f4e4d9206bbb333c222fa01363938355cb582a`

#### `optimization_record` — LLVM optimization record

- Language: `yaml`
- UTF-8 bytes: `11024`
- Estimated tokens: `11040`
- SHA-256: `c1eed531ffbbd0e9d7c3558ecea6e951283dcb7e51ce4ebf7c1144aa66d37c6d`
- Complete coverage: `True`
- Covered ranges: `optimization_record:[0, 11024)@c1eed531ffbbd0e9d7c3558ecea6e951283dcb7e51ce4ebf7c1144aa66d37c6d`

#### `diagnostics` — Diagnostics

- Language: `json`
- UTF-8 bytes: `148`
- Estimated tokens: `164`
- SHA-256: `9683b322333373cb4d9534fef10e27edba462e771e2b03e02108d5c6a7fc71ca`
- Complete coverage: `True`
- Covered ranges: `diagnostics:[0, 148)@9683b322333373cb4d9534fef10e27edba462e771e2b03e02108d5c6a7fc71ca`

#### `analysis` — Complete deterministic analysis

- Language: `json`
- UTF-8 bytes: `127084`
- Estimated tokens: `127100`
- SHA-256: `b0233e05ec1145b5459ddbbc006463cbb92b99ed17e40b82208dbabb0f348fe3`
- Complete coverage: `True`
- Covered ranges: `analysis:[0, 86496)@013954af457047cbfaae025c8e2b0e68f1cf0d4dd64a015f266c411cc03192ec`, `analysis:[86496, 127084)@839a4bbc7a7e3f8f8ed7e00ecc5e99ebef96ed992fd2bfb72a386593fdbd3c0e`

#### `build_manifest` — Compiler build manifest

- Language: `json`
- UTF-8 bytes: `696`
- Estimated tokens: `712`
- SHA-256: `99f69f032cd59b169e6e713372d6f2d52f09bd865351b1699594ea5984f450f1`
- Complete coverage: `True`
- Covered ranges: `build_manifest:[0, 696)@99f69f032cd59b169e6e713372d6f2d52f09bd865351b1699594ea5984f450f1`

#### `trace` — Compiler trace

- Language: `json`
- UTF-8 bytes: `213`
- Estimated tokens: `229`
- SHA-256: `c93c225da4447178c911c30bbeb170036679a5508fff214878cd7aef5013a3b8`
- Complete coverage: `True`
- Covered ranges: `trace:[0, 213)@c93c225da4447178c911c30bbeb170036679a5508fff214878cd7aef5013a3b8`


### Review requests

#### `artifact-0001` — artifact

- Estimated input tokens: `20874`
- Reserved output tokens: `1024`
- Depends on: none
- Covered ranges: `metadata:[0, 10623)@cf0c0073d052678d50154c75c438540e03e36164ac73cc1a44f04857e49e98dc`
- Prompt SHA-256: `4ffe46a9f64f9d5780b36c641221d7688f93ecf6ceb72e359bb2f26d3a188b19`
- Request SHA-256: `c7f8ec805e28436f44e4b6ae0cd76a38156681d9b9249871fc94ed67c8f61be0`
- Requested model: `z-ai/glm-5.2`
- Provider model: `z-ai/glm-5.2`
- Provider response ID: `chatcmpl-112c2cf1-cd36-401a-974a-030bb3cb94c3`
- Finish reason: `stop`
- Provider prompt tokens: `9476`
- Provider completion tokens: `298`
- Provider total tokens: `9774`

#### `artifact-0002` — artifact

- Estimated input tokens: `12058`
- Reserved output tokens: `1024`
- Depends on: none
- Covered ranges: `source:[0, 1822)@344883c033044766e2bfbac4a1bf838b9e07900faffb15f9fe919da6fe69b759`
- Prompt SHA-256: `9cb9fb094f1f95d9301716d50a5bd8e64df30f90728df4111aed35ac2a3d22ba`
- Request SHA-256: `1d909e1d1c237987a13de99523426a1b510ba98699a9a15e7f56945a4d7a0e40`
- Requested model: `z-ai/glm-5.2`
- Provider model: `z-ai/glm-5.2`
- Provider response ID: `chatcmpl-f0c69f53-04b1-4c5a-a3de-96962458e295`
- Finish reason: `stop`
- Provider prompt tokens: `5131`
- Provider completion tokens: `141`
- Provider total tokens: `5272`

#### `artifact-0003` — artifact

- Estimated input tokens: `11511`
- Reserved output tokens: `1024`
- Depends on: none
- Covered ranges: `wir:[0, 1269)@66955504c5683801f61dc176cc98d0c0c27909698197099712ef53956b70d471`
- Prompt SHA-256: `fed7415d2f1d6d5ce654cc95476a60fec8f9a6c95a9298eec28da32b2c079a21`
- Request SHA-256: `69c0a9f03cb6d32992f80777be429c15dd355ffc79ddb014ea91cf71f615b500`
- Requested model: `z-ai/glm-5.2`
- Provider model: `z-ai/glm-5.2`
- Provider response ID: `chatcmpl-6c8589f0-805e-41da-ad32-093726252d19`
- Finish reason: `stop`
- Provider prompt tokens: `4996`
- Provider completion tokens: `171`
- Provider total tokens: `5167`

#### `artifact-0004` — artifact

- Estimated input tokens: `16004`
- Reserved output tokens: `1024`
- Depends on: none
- Covered ranges: `raw_llvm:[0, 5767)@d5435d2d17b6fd4c0e5131f2a74ab57684b5accefefca51b349d651c0cb2b006`
- Prompt SHA-256: `775805600aa28a8bdb32a51f7fc1e2016c05d133b3c1744131f031f7138ad61f`
- Request SHA-256: `7aa8388c1c53c0be326772f1f9414ce89a32a7afc9cfdaf36d6f8834ca8aff24`
- Requested model: `z-ai/glm-5.2`
- Provider model: `z-ai/glm-5.2`
- Provider response ID: `chatcmpl-6925469b-ffa2-42a9-b042-208ecfd7cb28`
- Finish reason: `stop`
- Provider prompt tokens: `6685`
- Provider completion tokens: `441`
- Provider total tokens: `7126`

#### `artifact-0005` — artifact

- Estimated input tokens: `12476`
- Reserved output tokens: `1024`
- Depends on: none
- Covered ranges: `optimized_llvm:[0, 2227)@7bda6a3ae32ec72bf1ac4f39971bba88d5f34fff09f56798c9cdbbf76414598e`
- Prompt SHA-256: `bbb99db53f3dd9b457ccf1fcb1f0afbed64e674eddc97fefd32bd264b43ab34a`
- Request SHA-256: `75ea478ec6712ffad77b4d2a36b7de3d92334d2a9b730666fd2ca7ba99b6c131`
- Requested model: `z-ai/glm-5.2`
- Provider model: `z-ai/glm-5.2`
- Provider response ID: `chatcmpl-7c0729cb-80a2-44e9-b241-11254a664f04`
- Finish reason: `stop`
- Provider prompt tokens: `5361`
- Provider completion tokens: `413`
- Provider total tokens: `5774`

#### `artifact-0006` — artifact

- Estimated input tokens: `11502`
- Reserved output tokens: `1024`
- Depends on: none
- Covered ranges: `assembly:[0, 1262)@355551c6d11759a2137d794f6154bee9f187aff00d09f7f13887d82a052f3bf1`
- Prompt SHA-256: `309fa9946b0beba71efd8789b5c7c755fba59aa912ad865ad2069587465a7f84`
- Request SHA-256: `c96eecccadf6feb48963f4835b1cf4351386ff2bafdca1712110cea3b220c7ef`
- Requested model: `z-ai/glm-5.2`
- Provider model: `z-ai/glm-5.2`
- Provider response ID: `chatcmpl-2b6fd2f3-9046-47c0-98a7-74ee139a2595`
- Finish reason: `stop`
- Provider prompt tokens: `5071`
- Provider completion tokens: `231`
- Provider total tokens: `5302`

#### `artifact-0007` — artifact

- Estimated input tokens: `17794`
- Reserved output tokens: `1024`
- Depends on: none
- Covered ranges: `disassembly:[0, 7537)@fc79aff611b518050aabf8fba9f4e4d9206bbb333c222fa01363938355cb582a`
- Prompt SHA-256: `979355787dfb2a49400c229fcdb891bf41b9da8f907d2513d3b16eb0a87ada86`
- Request SHA-256: `cc3507efd600aeee368bb6e3bba143f641bf646356ce5fab1b460692e6e8f519`
- Requested model: `z-ai/glm-5.2`
- Provider model: `z-ai/glm-5.2`
- Provider response ID: `chatcmpl-6c974e6c-5d09-4a60-b761-27bea459d16c`
- Finish reason: `stop`
- Provider prompt tokens: `7835`
- Provider completion tokens: `503`
- Provider total tokens: `8338`

#### `artifact-0008` — artifact

- Estimated input tokens: `21286`
- Reserved output tokens: `1024`
- Depends on: none
- Covered ranges: `optimization_record:[0, 11024)@c1eed531ffbbd0e9d7c3558ecea6e951283dcb7e51ce4ebf7c1144aa66d37c6d`
- Prompt SHA-256: `8cf3fa1520539185c11096d11a38fee6c9ddd23197d2eefa94b2dea85600f97c`
- Request SHA-256: `2f95206cad4b1a0768c56b938c38826cd2aaf297183bb9fddb2a89ab9fab0945`
- Requested model: `z-ai/glm-5.2`
- Provider model: `z-ai/glm-5.2`
- Provider response ID: `chatcmpl-6adef0e7-1a9d-4d9a-a252-bbadcfdb3c90`
- Finish reason: `stop`
- Provider prompt tokens: `7526`
- Provider completion tokens: `487`
- Provider total tokens: `8013`

#### `artifact-0009` — artifact

- Estimated input tokens: `10387`
- Reserved output tokens: `1024`
- Depends on: none
- Covered ranges: `diagnostics:[0, 148)@9683b322333373cb4d9534fef10e27edba462e771e2b03e02108d5c6a7fc71ca`
- Prompt SHA-256: `973dbbb1cbad12eeee1abc74e0904f750530831bbc865fdabf4c73f05301874c`
- Request SHA-256: `911de9515e5ea7e1446b05a7eb6edd2228f498b678701d2959edf12c5a362910`
- Requested model: `z-ai/glm-5.2`
- Provider model: `z-ai/glm-5.2`
- Provider response ID: `chatcmpl-437f9ef4-3148-417f-b308-567302cfdd7f`
- Finish reason: `stop`
- Provider prompt tokens: `4667`
- Provider completion tokens: `119`
- Provider total tokens: `4786`

#### `artifact-0010` — artifact

- Estimated input tokens: `96754`
- Reserved output tokens: `1024`
- Depends on: none
- Covered ranges: `analysis:[0, 86496)@013954af457047cbfaae025c8e2b0e68f1cf0d4dd64a015f266c411cc03192ec`
- Prompt SHA-256: `24a50192c52a2fd03d03c56fa90e5f4d45241553d2d3d3ab7811351659da7251`
- Request SHA-256: `c349a70c35ff9042e6fe4cfe40bcc0a4ae0de73e9de168e9f6c8d29e0b4d083a`
- Requested model: `z-ai/glm-5.2`
- Provider model: `z-ai/glm-5.2`
- Provider response ID: `chatcmpl-d6979518-5292-4bcc-8582-c2c279a3b92f`
- Finish reason: `stop`
- Provider prompt tokens: `28196`
- Provider completion tokens: `415`
- Provider total tokens: `28611`

#### `artifact-0011` — artifact

- Estimated input tokens: `50851`
- Reserved output tokens: `1024`
- Depends on: none
- Covered ranges: `analysis:[86496, 127084)@839a4bbc7a7e3f8f8ed7e00ecc5e99ebef96ed992fd2bfb72a386593fdbd3c0e`
- Prompt SHA-256: `c8011a928f57dea8b7012897d25eaf6628734c40bfd114137cf9a13ad4407042`
- Request SHA-256: `141be3846e50f831e16e63abce5c72c1af118290a76b643c38b7364dc48fb2e7`
- Requested model: `z-ai/glm-5.2`
- Provider model: `z-ai/glm-5.2`
- Provider response ID: `chatcmpl-0e6753ba-8cda-49b2-a4f5-68b28951e878`
- Finish reason: `stop`
- Provider prompt tokens: `16249`
- Provider completion tokens: `176`
- Provider total tokens: `16425`

#### `artifact-0012` — artifact

- Estimated input tokens: `10950`
- Reserved output tokens: `1024`
- Depends on: none
- Covered ranges: `build_manifest:[0, 696)@99f69f032cd59b169e6e713372d6f2d52f09bd865351b1699594ea5984f450f1`
- Prompt SHA-256: `2bb63ec063d3c1b2ed987a44691c61b6b26572ee8d6a97492815f9fb0e7016e9`
- Request SHA-256: `e9ad9f7d3e04159fb96d96f3b5a32f5eeef08d29dfd3c2a76c9a2d69e6a7a03d`
- Requested model: `z-ai/glm-5.2`
- Provider model: `z-ai/glm-5.2`
- Provider response ID: `chatcmpl-6f36ff50-54c9-467c-a50b-b29d76c7923b`
- Finish reason: `stop`
- Provider prompt tokens: `4856`
- Provider completion tokens: `171`
- Provider total tokens: `5027`

#### `artifact-0013` — artifact

- Estimated input tokens: `10449`
- Reserved output tokens: `1024`
- Depends on: none
- Covered ranges: `trace:[0, 213)@c93c225da4447178c911c30bbeb170036679a5508fff214878cd7aef5013a3b8`
- Prompt SHA-256: `860760b0edd8cf6943876114021eb0fd3aefdd9f19e4e7810c9920fcb9f31e82`
- Request SHA-256: `a200ea093320dba5aeff035a59faddb03a798b500c567512d3cdf8e45737bd6a`
- Requested model: `z-ai/glm-5.2`
- Provider model: `z-ai/glm-5.2`
- Provider response ID: `chatcmpl-b4ceccd0-d418-461f-87e0-7fb6d148ad13`
- Finish reason: `stop`
- Provider prompt tokens: `4680`
- Provider completion tokens: `200`
- Provider total tokens: `4880`

#### `synthesis-0001` — synthesis

- Estimated input tokens: `32452`
- Reserved output tokens: `4096`
- Depends on: `artifact-0001`, `artifact-0002`, `artifact-0003`, `artifact-0004`, `artifact-0005`, `artifact-0006`, `artifact-0007`, `artifact-0008`, `artifact-0009`, `artifact-0010`, `artifact-0011`, `artifact-0012`, `artifact-0013`
- Covered ranges: none
- Prompt SHA-256: `a633561fe2b48efccfa4889d9ffae42e79d1312347f9edea77c2c61ee5d26a19`
- Request SHA-256: `d7e344d87da3b32f63260932fb340981789023d7c25506eadc68f79fb2abb9a7`
- Requested model: `z-ai/glm-5.2`
- Provider model: `z-ai/glm-5.2`
- Provider response ID: `chatcmpl-a938672c-7090-4abc-afbf-ca7df77283a9`
- Finish reason: `stop`
- Provider prompt tokens: `11845`
- Provider completion tokens: `1515`
- Provider total tokens: `13360`

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
; source: /tmp/weavec-build-v3dS8w/program.wir
; core-version: 2

; declarations

declare ptr @getenv(ptr)
declare i32 @atoi(ptr)

; string literals

@.str0 = private unnamed_addr constant [14 x i8] c"WEAVE_AUDIT_N\00"

; weave.source kind=function index=0 bytes=1100..1778 wir-bytes=3919..7416 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
; function: main
; params: none
; returns: i32
define i32 @main() {
entry:
  %n.addr = alloca i32
; weave.source kind=statement index=0 bytes=1157..1243 wir-bytes=4243..4563 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
  %t0 = getelementptr [14 x i8], ptr @.str0, i64 0, i64 0
  %t1 = call ptr @getenv(ptr %t0)
  ; let input
; weave.source kind=statement index=0 bytes=1250..1276 wir-bytes=4600..4770 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
  ; let n
  store i32 10, ptr %n.addr
; weave.source kind=statement index=0 bytes=1284..1438 wir-bytes=4807..5589 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
  ; if condition
  %t2 = icmp ne ptr %t1, null
  br i1 %t2, label %then, label %endif
then:
  ; then
; weave.source kind=statement index=0 bytes=1376..1405 wir-bytes=5293..5466 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
  ; set n
  %t3 = call i32 @atoi(ptr %t1)
  store i32 %t3, ptr %n.addr
  br label %endif
endif:
; weave.source kind=statement index=0 bytes=1446..1590 wir-bytes=5626..6398 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
  ; if condition
  %t4 = load i32, ptr %n.addr
  %t5 = icmp slt i32 %t4, 0
  br i1 %t5, label %then1, label %endif1
then1:
  ; then
; weave.source kind=statement index=0 bytes=1535..1557 wir-bytes=6145..6275 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
  ; set n
  store i32 10, ptr %n.addr
  br label %endif1
endif1:
; weave.source kind=statement index=0 bytes=1598..1743 wir-bytes=6435..7208 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
  ; if condition
  %t6 = load i32, ptr %n.addr
  %t7 = icmp sgt i32 %t6, 46
  br i1 %t7, label %then2, label %endif2
then2:
  ; then
; weave.source kind=statement index=0 bytes=1688..1710 wir-bytes=6955..7085 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
  ; set n
  store i32 10, ptr %n.addr
  br label %endif2
endif2:
; weave.source kind=statement index=0 bytes=1751..1776 wir-bytes=7245..7414 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
  ; return
  %t8 = load i32, ptr %n.addr
  %t9 = call i32 @fib(i32 %t8)
  ret i32 %t9
}

; weave.source kind=function index=0 bytes=532..1096 wir-bytes=1039..3878 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
; function: fib
; params: i32
; returns: i32
define internal i32 @fib(i32 %n) {
entry:
  %previous.addr = alloca i32
  %current.addr = alloca i32
  %index.addr = alloca i32
; weave.source kind=statement index=0 bytes=593..725 wir-bytes=1457..2111 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
  ; if condition
  %t0 = icmp sle i32 %n, 1
  br i1 %t0, label %then, label %endif
then:
  ; then
; weave.source kind=statement index=0 bytes=682..692 wir-bytes=1950..1994 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
  ; return
  ret i32 %n
endif:
; weave.source kind=statement index=0 bytes=733..765 wir-bytes=2146..2314 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
  ; let previous
  store i32 0, ptr %previous.addr
; weave.source kind=statement index=0 bytes=772..803 wir-bytes=2349..2516 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
  ; let current
  store i32 1, ptr %current.addr
; weave.source kind=statement index=0 bytes=810..839 wir-bytes=2551..2716 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
  ; let index
  store i32 2, ptr %index.addr
; weave.source kind=statement index=0 bytes=847..1070 wir-bytes=2752..3787 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
  ; while condition
  br label %while.cond1
while.cond1:
  %t1 = load i32, ptr %index.addr
  %t2 = icmp sle i32 %t1, %n
  br i1 %t2, label %while.body1, label %while.end1
while.body1:
  ; while body
; weave.source kind=statement index=0 bytes=913..954 wir-bytes=3099..3310 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
  %t3 = load i32, ptr %previous.addr
  %t4 = load i32, ptr %current.addr
  %t5 = add i32 %t3, %t4
  ; let next
; weave.source kind=statement index=0 bytes=965..987 wir-bytes=3345..3401 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
  ; set previous
  %t6 = load i32, ptr %current.addr
  store i32 %t6, ptr %previous.addr
; weave.source kind=statement index=0 bytes=998..1016 wir-bytes=3437..3491 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
  ; set current
  store i32 %t5, ptr %current.addr
; weave.source kind=statement index=0 bytes=1027..1068 wir-bytes=3528..3785 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
  ; set index
  %t7 = load i32, ptr %index.addr
  %t8 = add i32 %t7, 1
  store i32 %t8, ptr %index.addr
  br label %while.cond1
while.end1:
; weave.source kind=statement index=0 bytes=1078..1094 wir-bytes=3824..3876 path="/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
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
        "elapsed_seconds": 0.009223,
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
        "elapsed_seconds": 0.008768,
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
        "elapsed_seconds": 0.008881,
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
        "elapsed_seconds": 0.008988,
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
        "elapsed_seconds": 0.009041,
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
        "elapsed_seconds": 0.009156,
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
        "elapsed_seconds": 0.008692,
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
        "elapsed_seconds": 0.008934,
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
        "elapsed_seconds": 0.008981,
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
    "process_count": 115,
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
  "optimization_remarks": {
    "available": true,
    "documents": 33,
    "errors": [],
    "failure_reason": null,
    "format": "weave-loupe-optimization-remarks-v1",
    "records": [
      {
        "arguments": [
          {
            "Pass": "Canonicalize natural loops"
          },
          {
            "String": ": IR instruction count changed from "
          },
          {
            "IRInstrsBefore": "20"
          },
          {
            "String": " to "
          },
          {
            "IRInstrsAfter": "21"
          },
          {
            "String": "; Delta: "
          },
          {
            "DeltaInstrCount": "1"
          }
        ],
        "category": "analysis",
        "document_index": 10,
        "function": "main",
        "hotness": null,
        "identity": "0be4223f057a02632f1f25fd649cea5501329d4b232ccfae5f70d1af0e797d0e",
        "location": null,
        "message": "Canonicalize natural loops: IR instruction count changed from 20 to 21; Delta: 1",
        "name": "IRSizeChange",
        "pass": "size-info",
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
            "MIInstrsAfter": "39"
          },
          {
            "String": "; Delta: "
          },
          {
            "Delta": "39"
          }
        ],
        "category": "analysis",
        "document_index": 14,
        "function": "main",
        "hotness": null,
        "identity": "0cfa5d8105c9c57829b51d6b55bf234e7a17d8fe4f0c633e3365edc1a8196c76",
        "location": null,
        "message": "X86 DAG->DAG Instruction Selection: Function: main: MI Instruction count changed from 0 to 39; Delta: 39",
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
            "BasicBlock": "while.body1.i"
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
            "INST_": "7"
          },
          {
            "String": "\n"
          }
        ],
        "category": "analysis",
        "document_index": 30,
        "function": "main",
        "hotness": null,
        "identity": "17e6b356ab399aa0d22de341e36bec14dfe9628f4f3c26d78a0e956a0add234c",
        "location": null,
        "message": "BasicBlock: while.body1.i\n: 7",
        "name": "InstructionMix",
        "pass": "asm-printer",
        "unknown_fields": {}
      },
      {
        "arguments": [
          {
            "NumInstructions": "25"
          },
          {
            "String": " instructions in function"
          }
        ],
        "category": "analysis",
        "document_index": 32,
        "function": "main",
        "hotness": null,
        "identity": "20e3a1869401264d6333dc74a444687b8d05453f2e80d630db72221b76b460d6",
        "location": null,
        "message": "25 instructions in function",
        "name": "InstructionCount",
        "pass": "asm-printer",
        "unknown_fields": {}
      },
      {
        "arguments": [
          {
            "String": "loop not vectorized: "
          },
          {
            "String": "could not determine number of loop iterations"
          }
        ],
        "category": "analysis",
        "document_index": 4,
        "function": "main",
        "hotness": null,
        "identity": "2b2628ea740dd2389a2a9b36b6dda1e3171220aec9a8010fbcba5c1077114ce8",
        "location": null,
        "message": "loop not vectorized: could not determine number of loop iterations",
        "name": "CantComputeNumberOfIterations",
        "pass": "loop-vectorize",
        "unknown_fields": {}
      },
      {
        "arguments": [
          {
            "Pass": "Eliminate PHI nodes for register allocation"
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
            "MIInstrsBefore": "38"
          },
          {
            "String": " to "
          },
          {
            "MIInstrsAfter": "49"
          },
          {
            "String": "; Delta: "
          },
          {
            "Delta": "11"
          }
        ],
        "category": "analysis",
        "document_index": 16,
        "function": "main",
        "hotness": null,
        "identity": "2f39e44ff4fe568620ed78173c316510c1dce6f0bc2f55198c5c61d816810320",
        "location": null,
        "message": "Eliminate PHI nodes for register allocation: Function: main: MI Instruction count changed from 38 to 49; Delta: 11",
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
            "BasicBlock": ".thread"
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
            "INST_": "3"
          },
          {
            "String": "\n"
          }
        ],
        "category": "analysis",
        "document_index": 28,
        "function": "main",
        "hotness": null,
        "identity": "31cbe3d8d523723d50f738f8a22275c37321fb10290c92a64c31c720dffd8843",
        "location": null,
        "message": "BasicBlock: .thread\n: 3",
        "name": "InstructionMix",
        "pass": "asm-printer",
        "unknown_fields": {}
      },
      {
        "arguments": [
          {
            "NumVRCopies": "5"
          },
          {
            "String": " virtual registers copies "
          },
          {
            "TotalCopiesCost": "8.193750e+01"
          },
          {
            "String": " total copies cost "
          },
          {
            "String": "generated in function"
          }
        ],
        "category": "missed",
        "document_index": 20,
        "function": "main",
        "hotness": null,
        "identity": "472566c050e6e68c733ab8792d7daee5a4a11a63ce6839481f66f99ba7b43618",
        "location": null,
        "message": "5 virtual registers copies 8.193750e+01 total copies cost generated in function",
        "name": "SpillReloadCopies",
        "pass": "regalloc",
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
            "Cost": "-15005"
          },
          {
            "String": ", threshold="
          },
          {
            "Threshold": "250"
          },
          {
            "String": ")"
          }
        ],
        "category": "passed",
        "document_index": 2,
        "function": "main",
        "hotness": null,
        "identity": "48daa16f5c60a088105aed9dd1f6e9a997ca353fdcfdb7b6a2db27d8830cfb65",
        "location": null,
        "message": "'fib' inlined into 'main' with (cost=-15005, threshold=250)",
        "name": "Inlined",
        "pass": "inline",
        "unknown_fields": {}
      },
      {
        "arguments": [
          {
            "Pass": "CodeGen Prepare"
          },
          {
            "String": ": IR instruction count changed from "
          },
          {
            "IRInstrsBefore": "21"
          },
          {
            "String": " to "
          },
          {
            "IRInstrsAfter": "20"
          },
          {
            "String": "; Delta: "
          },
          {
            "DeltaInstrCount": "-1"
          }
        ],
        "category": "analysis",
        "document_index": 12,
        "function": "main",
        "hotness": null,
        "identity": "495cfef50b17fd51d27ebea7c27b01d180f993e5d101b45fab386a3a9b2dd2a3",
        "location": null,
        "message": "CodeGen Prepare: IR instruction count changed from 21 to 20; Delta: -1",
        "name": "IRSizeChange",
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
            "INST_": "6"
          },
          {
            "String": "\n"
          }
        ],
        "category": "analysis",
        "document_index": 26,
        "function": "main",
        "hotness": null,
        "identity": "4e4189e04f1f53ed5b02a293eddd9cab6e9ec6cc95d2335daba1f05aa6de6622",
        "location": null,
        "message": "BasicBlock: entry\n: 6",
        "name": "InstructionMix",
        "pass": "asm-printer",
        "unknown_fields": {}
      },
      {
        "arguments": [
          {
            "Pass": "Prologue/Epilogue Insertion & Frame Finalization"
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
            "MIInstrsBefore": "31"
          },
          {
            "String": " to "
          },
          {
            "MIInstrsAfter": "29"
          },
          {
            "String": "; Delta: "
          },
          {
            "Delta": "-2"
          }
        ],
        "category": "analysis",
        "document_index": 23,
        "function": "main",
        "hotness": null,
        "identity": "4ecf9fd04a2737ab2eb340f7dbde8b265e122b9393a1a0d576ac3d779cf974ae",
        "location": null,
        "message": "Prologue/Epilogue Insertion & Frame Finalization: Function: main: MI Instruction count changed from 31 to 29; Delta: -2",
        "name": "FunctionMISizeChange",
        "pass": "size-info",
        "unknown_fields": {}
      },
      {
        "arguments": [
          {
            "String": "List vectorization was possible but not beneficial with cost "
          },
          {
            "Cost": "0"
          },
          {
            "String": " >= "
          },
          {
            "Treshold": "0"
          }
        ],
        "category": "missed",
        "document_index": 9,
        "function": "main",
        "hotness": null,
        "identity": "52a0e3e4ffc2ef877bde9cb097e088e336369219f2c1a63dc1f1bf76fd159492",
        "location": null,
        "message": "List vectorization was possible but not beneficial with cost 0 >= 0",
        "name": "NotBeneficial",
        "pass": "slp-vectorizer",
        "unknown_fields": {}
      },
      {
        "arguments": [
          {
            "String": "BasicBlock: "
          },
          {
            "BasicBlock": "endif"
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
            "INST_": "4"
          },
          {
            "String": "\n"
          }
        ],
        "category": "analysis",
        "document_index": 27,
        "function": "main",
        "hotness": null,
        "identity": "5a41f8aa83cbf57efd746ec40f40f877b43c54e6c85cfd70ac3d65e9a8c66f4b",
        "location": null,
        "message": "BasicBlock: endif\n: 4",
        "name": "InstructionMix",
        "pass": "asm-printer",
        "unknown_fields": {}
      },
      {
        "arguments": [
          {
            "Pass": "Register Coalescer"
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
            "MIInstrsBefore": "51"
          },
          {
            "String": " to "
          },
          {
            "MIInstrsAfter": "35"
          },
          {
            "String": "; Delta: "
          },
          {
            "Delta": "-16"
          }
        ],
        "category": "analysis",
        "document_index": 18,
        "function": "main",
        "hotness": null,
        "identity": "5f5f2e04337d418a7799f338778947fc6c7dd89193430010cb8d589aa3e03bb4",
        "location": null,
        "message": "Register Coalescer: Function: main: MI Instruction count changed from 51 to 35; Delta: -16",
        "name": "FunctionMISizeChange",
        "pass": "size-info",
        "unknown_fields": {}
      },
      {
        "arguments": [
          {
            "String": "loop not vectorized: "
          },
          {
            "String": "value that could not be identified as reduction is used outside the loop"
          }
        ],
        "category": "analysis",
        "document_index": 3,
        "function": "main",
        "hotness": null,
        "identity": "630a0d765af5491b1083e1202751d1dc5c04c4091cbc2d8fb6e92c9848df7c9e",
        "location": null,
        "message": "loop not vectorized: value that could not be identified as reduction is used outside the loop",
        "name": "NonReductionValueUsedOutsideLoop",
        "pass": "loop-vectorize",
        "unknown_fields": {}
      },
      {
        "arguments": [
          {
            "String": "Cannot SLP vectorize list: vectorization was impossible"
          },
          {
            "String": " with available vectorization factors"
          }
        ],
        "category": "missed",
        "document_index": 6,
        "function": "main",
        "hotness": null,
        "identity": "7ed021da2118269c35e6839ca7ffe2b6f41ead22540d2f2d9da735000ac1cf85",
        "location": null,
        "message": "Cannot SLP vectorize list: vectorization was impossible with available vectorization factors",
        "name": "NotPossible",
        "pass": "slp-vectorizer",
        "unknown_fields": {}
      },
      {
        "arguments": [
          {
            "String": "Cannot SLP vectorize list: vectorization was impossible"
          },
          {
            "String": " with available vectorization factors"
          }
        ],
        "category": "missed",
        "document_index": 7,
        "function": "main",
        "hotness": null,
        "identity": "7ed021da2118269c35e6839ca7ffe2b6f41ead22540d2f2d9da735000ac1cf85",
        "location": null,
        "message": "Cannot SLP vectorize list: vectorization was impossible with available vectorization factors",
        "name": "NotPossible",
        "pass": "slp-vectorizer",
        "unknown_fields": {}
      },
      {
        "arguments": [
          {
            "String": "Cannot SLP vectorize list: vectorization was impossible"
          },
          {
            "String": " with available vectorization factors"
          }
        ],
        "category": "missed",
        "document_index": 8,
        "function": "main",
        "hotness": null,
        "identity": "7ed021da2118269c35e6839ca7ffe2b6f41ead22540d2f2d9da735000ac1cf85",
        "location": null,
        "message": "Cannot SLP vectorize list: vectorization was impossible with available vectorization factors",
        "name": "NotPossible",
        "pass": "slp-vectorizer",
        "unknown_fields": {}
      },
      {
        "arguments": [
          {
            "Callee": "atoi"
          },
          {
            "String": " will not be inlined into "
          },
          {
            "Caller": "main"
          },
          {
            "String": " because its definition is unavailable"
          }
        ],
        "category": "missed",
        "document_index": 1,
        "function": "main",
        "hotness": null,
        "identity": "876052067ad8a3de1fab3aebae547c878e5b078a8c3580c4b9fe6431ef1d7407",
        "location": null,
        "message": "atoi will not be inlined into main because its definition is unavailable",
        "name": "NoDefinition",
        "pass": "inline",
        "unknown_fields": {}
      },
      {
        "arguments": [
          {
            "Pass": "Machine Common Subexpression Elimination"
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
            "MIInstrsBefore": "39"
          },
          {
            "String": " to "
          },
          {
            "MIInstrsAfter": "38"
          },
          {
            "String": "; Delta: "
          },
          {
            "Delta": "-1"
          }
        ],
        "category": "analysis",
        "document_index": 15,
        "function": "main",
        "hotness": null,
        "identity": "9a1c7bfdffa1b839230aeb8f2891b704a7e7094f9d6d16077e000470a3a473e0",
        "location": null,
        "message": "Machine Common Subexpression Elimination: Function: main: MI Instruction count changed from 39 to 38; Delta: -1",
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
            "BasicBlock": "fib.exit"
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
        "document_index": 31,
        "function": "main",
        "hotness": null,
        "identity": "9b5de3ecb2857dc2072add0010341a2fe7acde5b4adbfaa71f73183eba06b908",
        "location": null,
        "message": "BasicBlock: fib.exit\n: 2",
        "name": "InstructionMix",
        "pass": "asm-printer",
        "unknown_fields": {}
      },
      {
        "arguments": [
          {
            "String": "BasicBlock: "
          },
          {
            "BasicBlock": "while.body1.i.preheader"
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
            "INST_": "3"
          },
          {
            "String": "\n"
          }
        ],
        "category": "analysis",
        "document_index": 29,
        "function": "main",
        "hotness": null,
        "identity": "a164b8cb963b16afea88471679e4f55e96759e81e55be48c629ce1ef4aca75de",
        "location": null,
        "message": "BasicBlock: while.body1.i.preheader\n: 3",
        "name": "InstructionMix",
        "pass": "asm-printer",
        "unknown_fields": {}
      },
      {
        "arguments": [
          {
            "NumVRCopies": "3"
          },
          {
            "String": " virtual registers copies "
          },
          {
            "TotalCopiesCost": "8.100000e+01"
          },
          {
            "String": " total copies cost "
          },
          {
            "String": "generated in loop"
          }
        ],
        "category": "missed",
        "document_index": 19,
        "function": "main",
        "hotness": null,
        "identity": "a7f08b2b9ef36618a10c78630c7263f99e2e373a5ce912a21e1f16770cd46ee5",
        "location": null,
        "message": "3 virtual registers copies 8.100000e+01 total copies cost generated in loop",
        "name": "LoopSpillReloadCopies",
        "pass": "regalloc",
        "unknown_fields": {}
      },
      {
        "arguments": [
          {
            "Pass": "Control Flow Optimizer"
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
            "MIInstrsBefore": "29"
          },
          {
            "String": " to "
          },
          {
            "MIInstrsAfter": "25"
          },
          {
            "String": "; Delta: "
          },
          {
            "Delta": "-4"
          }
        ],
        "category": "analysis",
        "document_index": 24,
        "function": "main",
        "hotness": null,
        "identity": "a925c8f4782148e59669c731749f58367a31db1ee85c430d34e52c2dec38de04",
        "location": null,
        "message": "Control Flow Optimizer: Function: main: MI Instruction count changed from 29 to 25; Delta: -4",
        "name": "FunctionMISizeChange",
        "pass": "size-info",
        "unknown_fields": {}
      },
      {
        "arguments": [
          {
            "Pass": "Two-Address instruction pass"
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
            "MIInstrsBefore": "49"
          },
          {
            "String": " to "
          },
          {
            "MIInstrsAfter": "51"
          },
          {
            "String": "; Delta: "
          },
          {
            "Delta": "2"
          }
        ],
        "category": "analysis",
        "document_index": 17,
        "function": "main",
        "hotness": null,
        "identity": "abbce5352103831304c4de1cd72afff1d80a74e656365ad801614c3ed17771c6",
        "location": null,
        "message": "Two-Address instruction pass: Function: main: MI Instruction count changed from 49 to 51; Delta: 2",
        "name": "FunctionMISizeChange",
        "pass": "size-info",
        "unknown_fields": {}
      },
      {
        "arguments": [
          {
            "NumStackBytes": "8"
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
        "document_index": 22,
        "function": "main",
        "hotness": null,
        "identity": "c8f62064d2ffcbc9053000e0f09bae284be5503daf6c6bf7a6d39d9fd3993e4d",
        "location": null,
        "message": "8 stack bytes in function 'main'",
        "name": "StackSize",
        "pass": "prologepilog",
        "unknown_fields": {}
      },
      {
        "arguments": [
          {
            "Pass": "Virtual Register Rewriter"
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
            "MIInstrsBefore": "35"
          },
          {
            "String": " to "
          },
          {
            "MIInstrsAfter": "31"
          },
          {
            "String": "; Delta: "
          },
          {
            "Delta": "-4"
          }
        ],
        "category": "analysis",
        "document_index": 21,
        "function": "main",
        "hotness": null,
        "identity": "ca74dc93be26e4e61b063eeeff19b9ba746a60fd928abb83683fc4858772724f",
        "location": null,
        "message": "Virtual Register Rewriter: Function: main: MI Instruction count changed from 35 to 31; Delta: -4",
        "name": "FunctionMISizeChange",
        "pass": "size-info",
        "unknown_fields": {}
      },
      {
        "arguments": [
          {
            "String": "loop not vectorized"
          }
        ],
        "category": "missed",
        "document_index": 5,
        "function": "main",
        "hotness": null,
        "identity": "cb8581095f8fd0bc35a5fe4067b46f89898fefbaad4922371b405936a6fb1a11",
        "location": null,
        "message": "loop not vectorized",
        "name": "MissedDetails",
        "pass": "loop-vectorize",
        "unknown_fields": {}
      },
      {
        "arguments": [
          {
            "Pass": "Canonicalize natural loops"
          },
          {
            "String": ": Function: "
          },
          {
            "Function": "main"
          },
          {
            "String": ": IR instruction count changed from "
          },
          {
            "IRInstrsBefore": "20"
          },
          {
            "String": " to "
          },
          {
            "IRInstrsAfter": "21"
          },
          {
            "String": "; Delta: "
          },
          {
            "DeltaInstrCount": "1"
          }
        ],
        "category": "analysis",
        "document_index": 11,
        "function": "main",
        "hotness": null,
        "identity": "d5cab28c4e646a02dc517581d0304338c6b965d95d72f8780db206b8cb2a60c6",
        "location": null,
        "message": "Canonicalize natural loops: Function: main: IR instruction count changed from 20 to 21; Delta: 1",
        "name": "FunctionIRSizeChange",
        "pass": "size-info",
        "unknown_fields": {}
      },
      {
        "arguments": [
          {
            "Pass": "CodeGen Prepare"
          },
          {
            "String": ": Function: "
          },
          {
            "Function": "main"
          },
          {
            "String": ": IR instruction count changed from "
          },
          {
            "IRInstrsBefore": "21"
          },
          {
            "String": " to "
          },
          {
            "IRInstrsAfter": "20"
          },
          {
            "String": "; Delta: "
          },
          {
            "DeltaInstrCount": "-1"
          }
        ],
        "category": "analysis",
        "document_index": 13,
        "function": "main",
        "hotness": null,
        "identity": "e00077a814ef12bde5a2587faa015928de40c0d16d69c6f084dd07e0e0909cb7",
        "location": null,
        "message": "CodeGen Prepare: Function: main: IR instruction count changed from 21 to 20; Delta: -1",
        "name": "FunctionIRSizeChange",
        "pass": "size-info",
        "unknown_fields": {}
      },
      {
        "arguments": [
          {
            "String": "\nFunction: main"
          },
          {
            "String": "\nOffset: [SP"
          },
          {
            "Offset": "-8"
          },
          {
            "String": "], Type: "
          },
          {
            "Type": "Spill"
          },
          {
            "String": ", Align: "
          },
          {
            "Align": "16"
          },
          {
            "String": ", Size: "
          },
          {
            "Size": "8"
          }
        ],
        "category": "analysis",
        "document_index": 25,
        "function": "main",
        "hotness": null,
        "identity": "e023a58868afcbd1c9687fff59ec7d2986d5be4f4f3b0fcfb9f48943a195e272",
        "location": null,
        "message": "Function: main\nOffset: [SP-8], Type: Spill, Align: 16, Size: 8",
        "name": "StackLayout",
        "pass": "stack-frame-layout",
        "unknown_fields": {}
      },
      {
        "arguments": [
          {
            "Callee": "getenv"
          },
          {
            "String": " will not be inlined into "
          },
          {
            "Caller": "main"
          },
          {
            "String": " because its definition is unavailable"
          }
        ],
        "category": "missed",
        "document_index": 0,
        "function": "main",
        "hotness": null,
        "identity": "f5daa68dc75949c6e89074f4f0128dc4a9fbe80137fc36775e82e26727b3e8f9",
        "location": null,
        "message": "getenv will not be inlined into main because its definition is unavailable",
        "name": "NoDefinition",
        "pass": "inline",
        "unknown_fields": {}
      }
    ],
    "summary": {
      "by_category": {
        "analysis": 23,
        "missed": 9,
        "passed": 1
      },
      "by_function": {
        "main": 33
      },
      "by_pass": {
        "asm-printer": 7,
        "inline": 3,
        "loop-vectorize": 3,
        "prologepilog": 1,
        "regalloc": 2,
        "size-info": 12,
        "slp-vectorizer": 4,
        "stack-frame-layout": 1
      },
      "by_pass_and_category": {
        "asm-printer": {
          "analysis": 7
        },
        "inline": {
          "missed": 2,
          "passed": 1
        },
        "loop-vectorize": {
          "analysis": 2,
          "missed": 1
        },
        "prologepilog": {
          "analysis": 1
        },
        "regalloc": {
          "missed": 2
        },
        "size-info": {
          "analysis": 12
        },
        "slp-vectorizer": {
          "missed": 4
        },
        "stack-frame-layout": {
          "analysis": 1
        }
      },
      "highest_value_missed": [
        {
          "category": "missed",
          "function": "main",
          "hotness": null,
          "identity": "876052067ad8a3de1fab3aebae547c878e5b078a8c3580c4b9fe6431ef1d7407",
          "location": null,
          "message": "atoi will not be inlined into main because its definition is unavailable",
          "name": "NoDefinition",
          "pass": "inline"
        },
        {
          "category": "missed",
          "function": "main",
          "hotness": null,
          "identity": "f5daa68dc75949c6e89074f4f0128dc4a9fbe80137fc36775e82e26727b3e8f9",
          "location": null,
          "message": "getenv will not be inlined into main because its definition is unavailable",
          "name": "NoDefinition",
          "pass": "inline"
        },
        {
          "category": "missed",
          "function": "main",
          "hotness": null,
          "identity": "cb8581095f8fd0bc35a5fe4067b46f89898fefbaad4922371b405936a6fb1a11",
          "location": null,
          "message": "loop not vectorized",
          "name": "MissedDetails",
          "pass": "loop-vectorize"
        },
        {
          "category": "missed",
          "function": "main",
          "hotness": null,
          "identity": "a7f08b2b9ef36618a10c78630c7263f99e2e373a5ce912a21e1f16770cd46ee5",
          "location": null,
          "message": "3 virtual registers copies 8.100000e+01 total copies cost generated in loop",
          "name": "LoopSpillReloadCopies",
          "pass": "regalloc"
        },
        {
          "category": "missed",
          "function": "main",
          "hotness": null,
          "identity": "472566c050e6e68c733ab8792d7daee5a4a11a63ce6839481f66f99ba7b43618",
          "location": null,
          "message": "5 virtual registers copies 8.193750e+01 total copies cost generated in function",
          "name": "SpillReloadCopies",
          "pass": "regalloc"
        },
        {
          "category": "missed",
          "function": "main",
          "hotness": null,
          "identity": "52a0e3e4ffc2ef877bde9cb097e088e336369219f2c1a63dc1f1bf76fd159492",
          "location": null,
          "message": "List vectorization was possible but not beneficial with cost 0 >= 0",
          "name": "NotBeneficial",
          "pass": "slp-vectorizer"
        },
        {
          "category": "missed",
          "function": "main",
          "hotness": null,
          "identity": "7ed021da2118269c35e6839ca7ffe2b6f41ead22540d2f2d9da735000ac1cf85",
          "location": null,
          "message": "Cannot SLP vectorize list: vectorization was impossible with available vectorization factors",
          "name": "NotPossible",
          "pass": "slp-vectorizer"
        },
        {
          "category": "missed",
          "function": "main",
          "hotness": null,
          "identity": "7ed021da2118269c35e6839ca7ffe2b6f41ead22540d2f2d9da735000ac1cf85",
          "location": null,
          "message": "Cannot SLP vectorize list: vectorization was impossible with available vectorization factors",
          "name": "NotPossible",
          "pass": "slp-vectorizer"
        },
        {
          "category": "missed",
          "function": "main",
          "hotness": null,
          "identity": "7ed021da2118269c35e6839ca7ffe2b6f41ead22540d2f2d9da735000ac1cf85",
          "location": null,
          "message": "Cannot SLP vectorize list: vectorization was impossible with available vectorization factors",
          "name": "NotPossible",
          "pass": "slp-vectorizer"
        }
      ],
      "total": 33
    },
    "valid": true
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
          "elapsed_seconds": 0.009223,
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
          "elapsed_seconds": 0.008768,
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
          "elapsed_seconds": 0.008881,
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
          "elapsed_seconds": 0.008988,
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
          "elapsed_seconds": 0.009041,
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
          "elapsed_seconds": 0.009156,
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
          "elapsed_seconds": 0.008692,
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
          "elapsed_seconds": 0.008934,
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
          "elapsed_seconds": 0.008981,
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
      "process_count": 115,
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
  },
  "wir": {
    "anonymous_identifiers": [],
    "available": true,
    "call_graph": {
      "fib": [],
      "main": [
        "atoi",
        "fib",
        "getenv"
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
          "block_delta": -3,
          "llvm_blocks": 7,
          "wir_blocks": 10
        }
      },
      "llvm_declarations": [
        "atoi",
        "getenv"
      ],
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
      "wir_externs": [
        "atoi",
        "getenv"
      ],
      "wir_functions": [
        "fib",
        "main"
      ]
    },
    "declarations": [
      {
        "kind": "extern",
        "name": "getenv",
        "params": [
          {
            "name": "name",
            "type": "ptr"
          }
        ],
        "returns": [
          "ptr"
        ]
      },
      {
        "kind": "extern",
        "name": "atoi",
        "params": [
          {
            "name": "text",
            "type": "ptr"
          }
        ],
        "returns": [
          "i32"
        ]
      },
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
              "end_byte": 468,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 455
            },
            {
              "end_byte": 463,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 456
            },
            {
              "end_byte": 467,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 464
            },
            {
              "end_byte": 528,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 473
            },
            {
              "end_byte": 480,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 474
            },
            {
              "end_byte": 485,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 481
            },
            {
              "end_byte": 509,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 490
            },
            {
              "end_byte": 497,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 491
            },
            {
              "end_byte": 508,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 498
            },
            {
              "end_byte": 503,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 499
            },
            {
              "end_byte": 507,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 504
            },
            {
              "end_byte": 527,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 514
            },
            {
              "end_byte": 522,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 515
            },
            {
              "end_byte": 526,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 523
            },
            {
              "end_byte": 1096,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 532
            },
            {
              "end_byte": 539,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 536
            },
            {
              "end_byte": 560,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 544
            },
            {
              "end_byte": 551,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 545
            },
            {
              "end_byte": 559,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 552
            },
            {
              "end_byte": 554,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 553
            },
            {
              "end_byte": 558,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 555
            },
            {
              "end_byte": 578,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 565
            },
            {
              "end_byte": 573,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 566
            },
            {
              "end_byte": 577,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 574
            },
            {
              "end_byte": 1095,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 583
            },
            {
              "end_byte": 725,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 593
            },
            {
              "end_byte": 596,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 594
            },
            {
              "end_byte": 641,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 605
            },
            {
              "end_byte": 615,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 606
            },
            {
              "end_byte": 640,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 616
            },
            {
              "end_byte": 623,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 617
            },
            {
              "end_byte": 625,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 624
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
            "instructions": 8,
            "opcodes": [
              "let",
              "call_ptr",
              "const_string_ptr",
              "let",
              "const_i32",
              "if",
              "ne_ptr",
              "const_null"
            ],
            "reachable": true,
            "role": "entry"
          },
          {
            "id": "b1",
            "instructions": 2,
            "opcodes": [
              "set",
              "call_i32"
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
            "instructions": 3,
            "opcodes": [
              "if",
              "lt_i32",
              "const_i32"
            ],
            "reachable": true,
            "role": "if-merge"
          },
          {
            "id": "b4",
            "instructions": 2,
            "opcodes": [
              "set",
              "const_i32"
            ],
            "reachable": true,
            "role": "if-then"
          },
          {
            "id": "b5",
            "instructions": 0,
            "opcodes": [],
            "reachable": true,
            "role": "if-else"
          },
          {
            "id": "b6",
            "instructions": 3,
            "opcodes": [
              "if",
              "gt_i32",
              "const_i32"
            ],
            "reachable": true,
            "role": "if-merge"
          },
          {
            "id": "b7",
            "instructions": 2,
            "opcodes": [
              "set",
              "const_i32"
            ],
            "reachable": true,
            "role": "if-then"
          },
          {
            "id": "b8",
            "instructions": 0,
            "opcodes": [],
            "reachable": true,
            "role": "if-else"
          },
          {
            "id": "b9",
            "instructions": 2,
            "opcodes": [
              "return",
              "call_i32"
            ],
            "reachable": true,
            "role": "if-merge"
          }
        ],
        "calls": [
          "atoi",
          "fib",
          "getenv"
        ],
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
            "source": "b1",
            "target": "b3"
          },
          {
            "kind": "fallthrough",
            "source": "b2",
            "target": "b3"
          },
          {
            "kind": "if-true",
            "source": "b3",
            "target": "b4"
          },
          {
            "kind": "if-false",
            "source": "b3",
            "target": "b5"
          },
          {
            "kind": "fallthrough",
            "source": "b4",
            "target": "b6"
          },
          {
            "kind": "fallthrough",
            "source": "b5",
            "target": "b6"
          },
          {
            "kind": "if-true",
            "source": "b6",
            "target": "b7"
          },
          {
            "kind": "if-false",
            "source": "b6",
            "target": "b8"
          },
          {
            "kind": "fallthrough",
            "source": "b7",
            "target": "b9"
          },
          {
            "kind": "fallthrough",
            "source": "b8",
            "target": "b9"
          }
        ],
        "locals": [
          "input",
          "n"
        ],
        "metrics": {
          "backedges": 0,
          "blocks": 10,
          "branches": 3,
          "calls": 3,
          "control_flow_edges": 12,
          "instructions": 22,
          "locals": 2,
          "loops": 0,
          "operands": 40,
          "reachable_blocks": 10,
          "returns": 1,
          "unreachable_blocks": 0,
          "unreachable_instructions": 0
        },
        "opcodes": {
          "call_i32": 2,
          "call_ptr": 1,
          "const_i32": 5,
          "const_null": 1,
          "const_string_ptr": 1,
          "gt_i32": 1,
          "if": 3,
          "let": 2,
          "lt_i32": 1,
          "ne_ptr": 1,
          "return": 1,
          "set": 3
        },
        "params": [],
        "provenance": {
          "mapped_instructions": 22,
          "spans": [
            {
              "end_byte": 639,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 626
            },
            {
              "end_byte": 636,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 627
            },
            {
              "end_byte": 638,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 637
            },
            {
              "end_byte": 694,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 650
            },
            {
              "end_byte": 655,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 651
            },
            {
              "end_byte": 693,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 666
            },
            {
              "end_byte": 692,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 682
            },
            {
              "end_byte": 691,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 690
            },
            {
              "end_byte": 724,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 703
            },
            {
              "end_byte": 708,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 704
            },
            {
              "end_byte": 723,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 719
            },
            {
              "end_byte": 765,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 733
            },
            {
              "end_byte": 746,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 738
            },
            {
              "end_byte": 764,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 751
            },
            {
              "end_byte": 761,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 752
            },
            {
              "end_byte": 763,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 762
            },
            {
              "end_byte": 803,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 772
            },
            {
              "end_byte": 784,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 777
            },
            {
              "end_byte": 802,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 789
            },
            {
              "end_byte": 799,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 790
            },
            {
              "end_byte": 801,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 800
            },
            {
              "end_byte": 839,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 810
            },
            {
              "end_byte": 820,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 815
            },
            {
              "end_byte": 838,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 825
            },
            {
              "end_byte": 835,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 826
            },
            {
              "end_byte": 837,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 836
            },
            {
              "end_byte": 1070,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 847
            },
            {
              "end_byte": 853,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 848
            },
            {
              "end_byte": 890,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 862
            },
            {
              "end_byte": 872,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 863
            },
            {
              "end_byte": 889,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 873
            },
            {
              "end_byte": 880,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 874
            },
            {
              "end_byte": 886,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 881
            },
            {
              "end_byte": 888,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 887
            },
            {
              "end_byte": 1069,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 899
            },
            {
              "end_byte": 954,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 913
            },
            {
              "end_byte": 922,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 918
            },
            {
              "end_byte": 953,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 927
            },
            {
              "end_byte": 935,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 928
            },
            {
              "end_byte": 944,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 936
            },
            {
              "end_byte": 952,
              "source_index": 0,
              "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
              "start_byte": 945
            }
          ]
        },
        "returns": [
          "i32"
        ],
        "types": {
          "i32": 11,
          "ptr": 4
        },
        "unresolved_symbols": []
      }
    },
    "metrics": {
      "anonymous_identifiers": 0,
      "backedges": 1,
      "blocks": 17,
      "branches": 5,
      "calls": 3,
      "control_flow_edges": 19,
      "declarations": 4,
      "duplicate_declarations": 0,
      "externs": 2,
      "functions": 2,
      "instructions": 42,
      "locals": 6,
      "loops": 1,
      "malformed_provenance": 99,
      "mapped_functions": 2,
      "mapped_instructions": 42,
      "operands": 78,
      "provenance_files": 1,
      "provenance_spans": 180,
      "reachable_blocks": 17,
      "returns": 3,
      "unknown_declarations": 0,
      "unreachable_blocks": 0,
      "unresolved_symbols": 0
    },
    "opcodes": {
      "add_i32": 2,
      "call_i32": 2,
      "call_ptr": 1,
      "const_i32": 10,
      "const_null": 1,
      "const_string_ptr": 1,
      "gt_i32": 1,
      "if": 4,
      "le_i32": 2,
      "let": 6,
      "lt_i32": 1,
      "ne_ptr": 1,
      "return": 3,
      "set": 6,
      "while": 1
    },
    "provenance": {
      "files": [
        {
          "index": 0,
          "path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave"
        }
      ],
      "malformed": [
        "span 1011..1015: no following WIR form",
        "span 1027..1068: no following WIR form",
        "span 1038..1067: no following WIR form",
        "span 1039..1046: no following WIR form",
        "span 1047..1052: no following WIR form",
        "span 1053..1066: no following WIR form",
        "span 1054..1063: no following WIR form",
        "span 1064..1065: no following WIR form",
        "span 1078..1094: no following WIR form",
        "span 1086..1093: no following WIR form",
        "span 1100..1778: no following WIR form",
        "span 1107..1111: no following WIR form",
        "span 1116..1124: no following WIR form",
        "span 1117..1123: no following WIR form",
        "span 1129..1142: no following WIR form",
        "span 1130..1137: no following WIR form",
        "span 1138..1141: no following WIR form",
        "span 1147..1777: no following WIR form",
        "span 1157..1243: no following WIR form",
        "span 1162..1167: no following WIR form",
        "span 1180..1242: no following WIR form",
        "span 1181..1189: no following WIR form",
        "span 1190..1196: no following WIR form",
        "span 1207..1241: no following WIR form",
        "span 1208..1224: no following WIR form",
        "span 1226..1239: no following WIR form",
        "span 1250..1276: no following WIR form",
        "span 1255..1256: no following WIR form",
        "span 1261..1275: no following WIR form",
        "span 1262..1271: no following WIR form",
        "span 1272..1274: no following WIR form",
        "span 1284..1438: no following WIR form",
        "span 1285..1287: no following WIR form",
        "span 1296..1335: no following WIR form",
        "span 1297..1306: no following WIR form",
        "span 1307..1334: no following WIR form",
        "span 1308..1314: no following WIR form",
        "span 1315..1320: no following WIR form",
        "span 1321..1333: no following WIR form",
        "span 1322..1332: no following WIR form",
        "span 1344..1407: no following WIR form",
        "span 1345..1349: no following WIR form",
        "span 1360..1406: no following WIR form",
        "span 1376..1405: no following WIR form",
        "span 1383..1404: no following WIR form",
        "span 1384..1392: no following WIR form",
        "span 1393..1397: no following WIR form",
        "span 1398..1403: no following WIR form",
        "span 1416..1437: no following WIR form",
        "span 1417..1421: no following WIR form",
        "span 1432..1436: no following WIR form",
        "span 1446..1590: no following WIR form",
        "span 1447..1449: no following WIR form",
        "span 1458..1494: no following WIR form",
        "span 1459..1468: no following WIR form",
        "span 1469..1493: no following WIR form",
        "span 1470..1476: no following WIR form",
        "span 1477..1478: no following WIR form",
        "span 1479..1492: no following WIR form",
        "span 1480..1489: no following WIR form",
        "span 1490..1491: no following WIR form",
        "span 1503..1559: no following WIR form",
        "span 1504..1508: no following WIR form",
        "span 1519..1558: no following WIR form",
        "span 1535..1557: no following WIR form",
        "span 1542..1556: no following WIR form",
        "span 1543..1552: no following WIR form",
        "span 1553..1555: no following WIR form",
        "span 1568..1589: no following WIR form",
        "span 1569..1573: no following WIR form",
        "span 1584..1588: no following WIR form",
        "span 1598..1743: no following WIR form",
        "span 1599..1601: no following WIR form",
        "span 1610..1647: no following WIR form",
        "span 1611..1620: no following WIR form",
        "span 1621..1646: no following WIR form",
        "span 1622..1628: no following WIR form",
        "span 1629..1630: no following WIR form",
        "span 1631..1645: no following WIR form",
        "span 1632..1641: no following WIR form",
        "span 1642..1644: no following WIR form",
        "span 1656..1712: no following WIR form",
        "span 1657..1661: no following WIR form",
        "span 1672..1711: no following WIR form",
        "span 1688..1710: no following WIR form",
        "span 1695..1709: no following WIR form",
        "span 1696..1705: no following WIR form",
        "span 1706..1708: no following WIR form",
        "span 1721..1742: no following WIR form",
        "span 1722..1726: no following WIR form",
        "span 1737..1741: no following WIR form",
        "span 1751..1776: no following WIR form",
        "span 1759..1775: no following WIR form",
        "span 1760..1768: no following WIR form",
        "span 1769..1772: no following WIR form",
        "span 1773..1774: no following WIR form",
        "span 965..987: no following WIR form",
        "span 979..986: no following WIR form",
        "span 998..1016: no following WIR form"
      ],
      "spans": [
        {
          "end_byte": 469,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 412
        },
        {
          "end_byte": 419,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 413
        },
        {
          "end_byte": 426,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 420
        },
        {
          "end_byte": 450,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 431
        },
        {
          "end_byte": 438,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 432
        },
        {
          "end_byte": 449,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 439
        },
        {
          "end_byte": 444,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 440
        },
        {
          "end_byte": 448,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 445
        },
        {
          "end_byte": 468,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 455
        },
        {
          "end_byte": 463,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 456
        },
        {
          "end_byte": 467,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 464
        },
        {
          "end_byte": 528,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 473
        },
        {
          "end_byte": 480,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 474
        },
        {
          "end_byte": 485,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 481
        },
        {
          "end_byte": 509,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 490
        },
        {
          "end_byte": 497,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 491
        },
        {
          "end_byte": 508,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 498
        },
        {
          "end_byte": 503,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 499
        },
        {
          "end_byte": 507,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 504
        },
        {
          "end_byte": 527,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 514
        },
        {
          "end_byte": 522,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 515
        },
        {
          "end_byte": 526,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 523
        },
        {
          "end_byte": 1096,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 532
        },
        {
          "end_byte": 539,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 536
        },
        {
          "end_byte": 560,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 544
        },
        {
          "end_byte": 551,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 545
        },
        {
          "end_byte": 559,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 552
        },
        {
          "end_byte": 554,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 553
        },
        {
          "end_byte": 558,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 555
        },
        {
          "end_byte": 578,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 565
        },
        {
          "end_byte": 573,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 566
        },
        {
          "end_byte": 577,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 574
        },
        {
          "end_byte": 1095,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 583
        },
        {
          "end_byte": 725,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 593
        },
        {
          "end_byte": 596,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 594
        },
        {
          "end_byte": 641,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 605
        },
        {
          "end_byte": 615,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 606
        },
        {
          "end_byte": 640,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 616
        },
        {
          "end_byte": 623,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 617
        },
        {
          "end_byte": 625,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 624
        },
        {
          "end_byte": 639,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 626
        },
        {
          "end_byte": 636,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 627
        },
        {
          "end_byte": 638,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 637
        },
        {
          "end_byte": 694,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 650
        },
        {
          "end_byte": 655,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 651
        },
        {
          "end_byte": 693,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 666
        },
        {
          "end_byte": 692,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 682
        },
        {
          "end_byte": 691,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 690
        },
        {
          "end_byte": 724,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 703
        },
        {
          "end_byte": 708,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 704
        },
        {
          "end_byte": 723,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 719
        },
        {
          "end_byte": 765,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 733
        },
        {
          "end_byte": 746,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 738
        },
        {
          "end_byte": 764,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 751
        },
        {
          "end_byte": 761,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 752
        },
        {
          "end_byte": 763,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 762
        },
        {
          "end_byte": 803,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 772
        },
        {
          "end_byte": 784,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 777
        },
        {
          "end_byte": 802,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 789
        },
        {
          "end_byte": 799,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 790
        },
        {
          "end_byte": 801,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 800
        },
        {
          "end_byte": 839,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 810
        },
        {
          "end_byte": 820,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 815
        },
        {
          "end_byte": 838,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 825
        },
        {
          "end_byte": 835,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 826
        },
        {
          "end_byte": 837,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 836
        },
        {
          "end_byte": 1070,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 847
        },
        {
          "end_byte": 853,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 848
        },
        {
          "end_byte": 890,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 862
        },
        {
          "end_byte": 872,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 863
        },
        {
          "end_byte": 889,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 873
        },
        {
          "end_byte": 880,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 874
        },
        {
          "end_byte": 886,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 881
        },
        {
          "end_byte": 888,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 887
        },
        {
          "end_byte": 1069,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 899
        },
        {
          "end_byte": 954,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 913
        },
        {
          "end_byte": 922,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 918
        },
        {
          "end_byte": 953,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 927
        },
        {
          "end_byte": 935,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 928
        },
        {
          "end_byte": 944,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 936
        },
        {
          "end_byte": 952,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 945
        },
        {
          "end_byte": 987,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 965
        },
        {
          "end_byte": 986,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 979
        },
        {
          "end_byte": 1016,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 998
        },
        {
          "end_byte": 1015,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1011
        },
        {
          "end_byte": 1068,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1027
        },
        {
          "end_byte": 1067,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1038
        },
        {
          "end_byte": 1046,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1039
        },
        {
          "end_byte": 1052,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1047
        },
        {
          "end_byte": 1066,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1053
        },
        {
          "end_byte": 1063,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1054
        },
        {
          "end_byte": 1065,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1064
        },
        {
          "end_byte": 1094,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1078
        },
        {
          "end_byte": 1093,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1086
        },
        {
          "end_byte": 1778,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1100
        },
        {
          "end_byte": 1111,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1107
        },
        {
          "end_byte": 1124,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1116
        },
        {
          "end_byte": 1123,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1117
        },
        {
          "end_byte": 1142,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1129
        },
        {
          "end_byte": 1137,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1130
        },
        {
          "end_byte": 1141,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1138
        },
        {
          "end_byte": 1777,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1147
        },
        {
          "end_byte": 1243,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1157
        },
        {
          "end_byte": 1167,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1162
        },
        {
          "end_byte": 1242,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1180
        },
        {
          "end_byte": 1189,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1181
        },
        {
          "end_byte": 1196,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1190
        },
        {
          "end_byte": 1241,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1207
        },
        {
          "end_byte": 1224,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1208
        },
        {
          "end_byte": 1239,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1226
        },
        {
          "end_byte": 1276,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1250
        },
        {
          "end_byte": 1256,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1255
        },
        {
          "end_byte": 1275,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1261
        },
        {
          "end_byte": 1271,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1262
        },
        {
          "end_byte": 1274,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1272
        },
        {
          "end_byte": 1438,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1284
        },
        {
          "end_byte": 1287,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1285
        },
        {
          "end_byte": 1335,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1296
        },
        {
          "end_byte": 1306,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1297
        },
        {
          "end_byte": 1334,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1307
        },
        {
          "end_byte": 1314,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1308
        },
        {
          "end_byte": 1320,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1315
        },
        {
          "end_byte": 1333,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1321
        },
        {
          "end_byte": 1332,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1322
        },
        {
          "end_byte": 1407,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1344
        },
        {
          "end_byte": 1349,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1345
        },
        {
          "end_byte": 1406,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1360
        },
        {
          "end_byte": 1405,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1376
        },
        {
          "end_byte": 1404,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1383
        },
        {
          "end_byte": 1392,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1384
        },
        {
          "end_byte": 1397,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1393
        },
        {
          "end_byte": 1403,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1398
        },
        {
          "end_byte": 1437,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1416
        },
        {
          "end_byte": 1421,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1417
        },
        {
          "end_byte": 1436,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1432
        },
        {
          "end_byte": 1590,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1446
        },
        {
          "end_byte": 1449,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1447
        },
        {
          "end_byte": 1494,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1458
        },
        {
          "end_byte": 1468,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1459
        },
        {
          "end_byte": 1493,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1469
        },
        {
          "end_byte": 1476,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1470
        },
        {
          "end_byte": 1478,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1477
        },
        {
          "end_byte": 1492,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1479
        },
        {
          "end_byte": 1489,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1480
        },
        {
          "end_byte": 1491,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1490
        },
        {
          "end_byte": 1559,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1503
        },
        {
          "end_byte": 1508,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1504
        },
        {
          "end_byte": 1558,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1519
        },
        {
          "end_byte": 1557,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1535
        },
        {
          "end_byte": 1556,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1542
        },
        {
          "end_byte": 1552,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1543
        },
        {
          "end_byte": 1555,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1553
        },
        {
          "end_byte": 1589,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1568
        },
        {
          "end_byte": 1573,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1569
        },
        {
          "end_byte": 1588,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1584
        },
        {
          "end_byte": 1743,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1598
        },
        {
          "end_byte": 1601,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1599
        },
        {
          "end_byte": 1647,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1610
        },
        {
          "end_byte": 1620,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1611
        },
        {
          "end_byte": 1646,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1621
        },
        {
          "end_byte": 1628,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1622
        },
        {
          "end_byte": 1630,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1629
        },
        {
          "end_byte": 1645,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1631
        },
        {
          "end_byte": 1641,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1632
        },
        {
          "end_byte": 1644,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1642
        },
        {
          "end_byte": 1712,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1656
        },
        {
          "end_byte": 1661,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1657
        },
        {
          "end_byte": 1711,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1672
        },
        {
          "end_byte": 1710,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1688
        },
        {
          "end_byte": 1709,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1695
        },
        {
          "end_byte": 1705,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1696
        },
        {
          "end_byte": 1708,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1706
        },
        {
          "end_byte": 1742,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1721
        },
        {
          "end_byte": 1726,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1722
        },
        {
          "end_byte": 1741,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1737
        },
        {
          "end_byte": 1776,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1751
        },
        {
          "end_byte": 1775,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1759
        },
        {
          "end_byte": 1768,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1760
        },
        {
          "end_byte": 1772,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1769
        },
        {
          "end_byte": 1774,
          "source_index": 0,
          "source_path": "/home/runner/work/weave-loupe/weave-loupe/docs/audit/fibonacci_runtime.weave",
          "start_byte": 1773
        }
      ]
    },
    "types": {
      "i32": 26,
      "ptr": 4
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
  "output": "/tmp/loupe-audit-bmu9fd9l/.audit.loupe.9xf2xwua/artifacts/program",
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

# Weave Compiler Final Adversarial Release-Gate Audit Review

## 1. Executive Summary

The deterministic audit summary and all associated artifact reviews have been synthesized. The Weave compiler pipeline successfully compiled the `fibonacci-runtime` test case targeting `x86_64-unknown-linux-gnu` with an exit code of 0 and no diagnostics. All configured deterministic gates (native budget, optimized LLVM budget, and runtime matrix) passed. The complete evidence chain is present, hash-addressed, and cross-stage consistent. No blocking findings were identified across the WIR, raw LLVM, optimized LLVM, assembly, disassembly, optimization records, or runtime trace artifacts. The release gate is cleared.

## 2. Verification Matrix

| Artifact | Byte Range | SHA-256 | Status | Cross-Stage Verification |
| :--- | :--- | :--- | :--- | :--- |
| **metadata** | `[0, 10623)` | `cf0c0073...` | REVIEWED | Auditor identity, bundle format, and all 49 auditor files verified. Source/loupe repository SHAs match (`6ee1ebaceb...`). WeaveC pinned at `v0.3.0+git.1ba3dc73a459`. |
| **source** | `[0, 1822)` | `344883c0...` | REVIEWED | Defines `fib` and `main`. Uses `getenv`/`atoi` to prevent constant folding. Clamps `n` to `[0, 46]` with default 10. Matches WIR/LLVM behavior. |
| **wir** | `[0, 1269)` | `66955504...` | REVIEWED | Defines externs `getenv`/`atoi`. Iterative `fib` loop matches source. `main` clamps values as expected. |
| **raw_llvm** | `[0, 5767)` | `d5435d2d...` | REVIEWED | Unoptimized IR retains `fib` and `main` signatures. `@.str0` = `WEAVE_AUDIT_N`. Control flow accurately reflects source clamping. |
| **optimized_llvm**| `[0, 2227)` | `7bda6a3a...` | REVIEWED | `fib` successfully inlined into `main`. Target triple `x86_64-pc-linux-gnu`. Loop logic and bounds checks preserved. |
| **assembly** | `[0, 1262)` | `355551c6...` | REVIEWED | x86_64 instructions reflect optimized IR. `getenv@PLT` and `atoi@PLT` called. Loop uses `%eax`/`%edx`/`%ecx`. |
| **disassembly** | `[0, 7537)` | `fc79aff6...` | REVIEWED | Confirms assembly layout. `main` at `0x1150`-`0x119f`. 0 indirect calls. Reachability complete. |
| **optimization_record** | `[0, 11024)` | `c1eed531...` | REVIEWED | `fib` inlined (cost=-15005). `getenv`/`atoi` missed due to `NoDefinition` (expected). Regalloc spills documented. |
| **diagnostics** | `[0, 148)` | `9683b322...` | REVIEWED | `exit_code: 0`, `status: "succeeded"`, empty diagnostics array. |
| **analysis** | `[0, 86496)` | `013954af...` | REVIEWED | 9/9 runtime cases passed. 0 missing/unexpected externs. WIR-to-LLVM block deltas explained by inlining. |
| **analysis** | `[86496, 127084)`| `839a4bbc...` | REVIEWED | WIR provenance reports 99 malformed spans in trailing source region, but all 42 WIR instructions mapped. |
| **build_manifest**| `[0, 696)` | `99f69f03...` | REVIEWED | `status: "succeeded"`, `phase: "complete"`. Toolchain: `weavec`, `clang`, `llc`, `llvm-objdump`. `O3` optimization. |
| **trace** | `[0, 213)` | `c93c225d...` | REVIEWED | `weavec-compilation-trace-v1` reports success. Empty events array consistent with clean compile. |

## 3. Blocking Findings

**None.** All artifact reviews returned `REVIEWED` with no blocking codes. The supplied summaries sufficiently support all essential correctness, safety, ABI, target, runtime, and final-code claims.

## 4. Non-Blocking Opportunities

1. **WIR Span Mapping Diagnostics**: The `analysis` artifact reports 99 malformed spans (e.g., "span 1011..1015: no following WIR form") in the trailing source region of `docs/audit/fibonacci_runtime.weave`. While all 42 WIR instructions are correctly mapped and this does not block the release, the Weave compiler front-end could improve source-to-WIR span tracking fidelity to reduce noise in audit analyses.
2. **Vectorization Misses**: The `optimization_record` indicates that `loop-vectorize` and `slp-vectorizer` missed opportunities in `main` due to `NonReductionValueUsedOutsideLoop` and `CantComputeNumberOfIterations`. As the Fibonacci calculation is inherently sequential and dependent on previous iterations, this is expected behavior, but future compiler passes could explore loop transformations if performance benchmarks justify it.
3. **Register Allocation Spills**: The `optimization_record` notes `LoopSpillReloadCopies` and `SpillReloadCopies` in `main` under `O3` optimization. Given the small register footprint of this specific test case, this is non-critical, but it may be worth reviewing the register allocator heuristics for more complex loops.

## 5. Suggested Verification

1. **Runtime Matrix Integrity**: Future audits should continue to execute the 9-case runtime matrix in a bubblewrap sandbox (network disabled, read-only filesystem) as performed here. The cases covering missing input, `0`, `1`, `2`, `10`, `12`, `-1`, `47`, and non-numeric `abc` provide excellent boundary and fallback coverage for the clamping logic.
2. **Cross-Stage Hash Chaining**: Maintain the strict hash-addressed UTF-8 byte range verification used in this audit. The ability to trace `source` -> `wir` -> `raw_llvm` -> `optimized_llvm` -> `assembly` -> `disassembly` via cryptographic hashes is critical for deterministic release gates.
3. **Inlining Threshold Validation**: The `fib` function was inlined with a cost of -15005 against a threshold of 250. While correct, it is recommended to periodically audit the Weave compiler's inlining cost model against larger workloads to ensure aggressive inlining does not lead to excessive code bloat in production binaries.

<details>
<summary>Raw model response</summary>

```text
OK

# Weave Compiler Final Adversarial Release-Gate Audit Review

## 1. Executive Summary

The deterministic audit summary and all associated artifact reviews have been synthesized. The Weave compiler pipeline successfully compiled the `fibonacci-runtime` test case targeting `x86_64-unknown-linux-gnu` with an exit code of 0 and no diagnostics. All configured deterministic gates (native budget, optimized LLVM budget, and runtime matrix) passed. The complete evidence chain is present, hash-addressed, and cross-stage consistent. No blocking findings were identified across the WIR, raw LLVM, optimized LLVM, assembly, disassembly, optimization records, or runtime trace artifacts. The release gate is cleared.

## 2. Verification Matrix

| Artifact | Byte Range | SHA-256 | Status | Cross-Stage Verification |
| :--- | :--- | :--- | :--- | :--- |
| **metadata** | `[0, 10623)` | `cf0c0073...` | REVIEWED | Auditor identity, bundle format, and all 49 auditor files verified. Source/loupe repository SHAs match (`6ee1ebaceb...`). WeaveC pinned at `v0.3.0+git.1ba3dc73a459`. |
| **source** | `[0, 1822)` | `344883c0...` | REVIEWED | Defines `fib` and `main`. Uses `getenv`/`atoi` to prevent constant folding. Clamps `n` to `[0, 46]` with default 10. Matches WIR/LLVM behavior. |
| **wir** | `[0, 1269)` | `66955504...` | REVIEWED | Defines externs `getenv`/`atoi`. Iterative `fib` loop matches source. `main` clamps values as expected. |
| **raw_llvm** | `[0, 5767)` | `d5435d2d...` | REVIEWED | Unoptimized IR retains `fib` and `main` signatures. `@.str0` = `WEAVE_AUDIT_N`. Control flow accurately reflects source clamping. |
| **optimized_llvm**| `[0, 2227)` | `7bda6a3a...` | REVIEWED | `fib` successfully inlined into `main`. Target triple `x86_64-pc-linux-gnu`. Loop logic and bounds checks preserved. |
| **assembly** | `[0, 1262)` | `355551c6...` | REVIEWED | x86_64 instructions reflect optimized IR. `getenv@PLT` and `atoi@PLT` called. Loop uses `%eax`/`%edx`/`%ecx`. |
| **disassembly** | `[0, 7537)` | `fc79aff6...` | REVIEWED | Confirms assembly layout. `main` at `0x1150`-`0x119f`. 0 indirect calls. Reachability complete. |
| **optimization_record** | `[0, 11024)` | `c1eed531...` | REVIEWED | `fib` inlined (cost=-15005). `getenv`/`atoi` missed due to `NoDefinition` (expected). Regalloc spills documented. |
| **diagnostics** | `[0, 148)` | `9683b322...` | REVIEWED | `exit_code: 0`, `status: "succeeded"`, empty diagnostics array. |
| **analysis** | `[0, 86496)` | `013954af...` | REVIEWED | 9/9 runtime cases passed. 0 missing/unexpected externs. WIR-to-LLVM block deltas explained by inlining. |
| **analysis** | `[86496, 127084)`| `839a4bbc...` | REVIEWED | WIR provenance reports 99 malformed spans in trailing source region, but all 42 WIR instructions mapped. |
| **build_manifest**| `[0, 696)` | `99f69f03...` | REVIEWED | `status: "succeeded"`, `phase: "complete"`. Toolchain: `weavec`, `clang`, `llc`, `llvm-objdump`. `O3` optimization. |
| **trace** | `[0, 213)` | `c93c225d...` | REVIEWED | `weavec-compilation-trace-v1` reports success. Empty events array consistent with clean compile. |

## 3. Blocking Findings

**None.** All artifact reviews returned `REVIEWED` with no blocking codes. The supplied summaries sufficiently support all essential correctness, safety, ABI, target, runtime, and final-code claims.

## 4. Non-Blocking Opportunities

1. **WIR Span Mapping Diagnostics**: The `analysis` artifact reports 99 malformed spans (e.g., "span 1011..1015: no following WIR form") in the trailing source region of `docs/audit/fibonacci_runtime.weave`. While all 42 WIR instructions are correctly mapped and this does not block the release, the Weave compiler front-end could improve source-to-WIR span tracking fidelity to reduce noise in audit analyses.
2. **Vectorization Misses**: The `optimization_record` indicates that `loop-vectorize` and `slp-vectorizer` missed opportunities in `main` due to `NonReductionValueUsedOutsideLoop` and `CantComputeNumberOfIterations`. As the Fibonacci calculation is inherently sequential and dependent on previous iterations, this is expected behavior, but future compiler passes could explore loop transformations if performance benchmarks justify it.
3. **Register Allocation Spills**: The `optimization_record` notes `LoopSpillReloadCopies` and `SpillReloadCopies` in `main` under `O3` optimization. Given the small register footprint of this specific test case, this is non-critical, but it may be worth reviewing the register allocator heuristics for more complex loops.

## 5. Suggested Verification

1. **Runtime Matrix Integrity**: Future audits should continue to execute the 9-case runtime matrix in a bubblewrap sandbox (network disabled, read-only filesystem) as performed here. The cases covering missing input, `0`, `1`, `2`, `10`, `12`, `-1`, `47`, and non-numeric `abc` provide excellent boundary and fallback coverage for the clamping logic.
2. **Cross-Stage Hash Chaining**: Maintain the strict hash-addressed UTF-8 byte range verification used in this audit. The ability to trace `source` -> `wir` -> `raw_llvm` -> `optimized_llvm` -> `assembly` -> `disassembly` via cryptographic hashes is critical for deterministic release gates.
3. **Inlining Threshold Validation**: The `fib` function was inlined with a cost of -15005 against a threshold of 250. While correct, it is recommended to periodically audit the Weave compiler's inlining cost model against larger workloads to ensure aggressive inlining does not lead to excessive code bloat in production binaries.
```
</details>
