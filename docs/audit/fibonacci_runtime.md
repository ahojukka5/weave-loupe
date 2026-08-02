# Weave Loupe Audit Report

## Verdict

- **Status:** OK
- **Code:** none
- **Reason:** No blocking defect found.

## Reproducibility

- **Report content SHA-256:** `cbe1ef2b19b34d4a3eacf5067d4e702e364369494523e8d9d1d36dcf421c1471`
- **Audit timestamp (UTC):** `2026-08-02T15:46:05+00:00`
- **Re-audit no later than (UTC):** `2026-09-01T15:46:05+00:00`
- **Maximum audit age:** `30` days
- **Audited input invalidation:** `any source or runtime matrix hash change`
- **Compiler binary invalidation:** `any compiler binary hash change`
- **Auditor invalidation:** `any audit implementation fingerprint change`
- **Model invalidation:** `any configured LLM model or endpoint change`
- **Request limit invalidation:** `any configured LLM max-token change`
- **Development compiler invalidation:** `any compiler version change`
- **Identity attestation upgrade:** `required when command identity becomes available`
- **Audited source Git SHA:** `7795ab77bdce4ab2cfa0c8fa415caf435def071a`
- **Source tree state:** `clean`
- **Weave Loupe Git SHA:** `7795ab77bdce4ab2cfa0c8fa415caf435def071a`
- **Auditor content SHA-256:** `f14fe2e8261f65fc26968d7d7a9418732863631a205d54d3602313bd24a8912d`
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
- **LLM prompt SHA-256:** `98b65a68c26d6a6098d54701bc8d6d7830bbe5ac7ed87348227737c2833705f7`
- **LLM request SHA-256:** `f003aac123891f4e3a343736f6a52e28a6697376e4332c40371fbf789a99f741`
- **Provider-reported model:** `z-ai/glm-5.2`
- **Provider response ID:** `chatcmpl-5d288e38-4852-445e-b64b-c779afc44411`
- **Provider system fingerprint:** `unavailable`
- **Provider finish reason:** `stop`
- **Provider created (Unix):** `1785685724`
- **Provider prompt tokens:** `11200`
- **Provider completion tokens:** `1394`
- **Provider total tokens:** `12594`
- **GitHub run ID:** `30754646619`
- **GitHub workflow SHA:** `63392d7157d473e9da82df6ddc07e2f3448e8d86`

## Machine and running conditions

- **Operating system:** `Ubuntu 24.04.4 LTS`
- **Kernel:** `Linux 6.17.0-1020-azure`
- **Architecture:** `x86_64`
- **CPU:** `AMD EPYC 7763 64-Core Processor`
- **Logical CPUs:** `4`
- **Memory:** `16770756608` bytes
- **Python:** `3.12.13`
- **libc:** `glibc 2.39`

## Audited inputs

- Source `docs/audit/fibonacci_runtime.weave` — SHA-256 `a0df013d2e54ac1426498c7fda686d113ae4ca4f7371fe3836c490ccf9343ba4` — 1779 bytes
- Runtime matrix `docs/audit/fibonacci_runtime.audit.json` — SHA-256 `dc8e5b6d2d6234628a045cdf49a535825fd337815af4d3fa5f53adfc59c0d7d2`

## Captured evidence

- `assembly` — SHA-256 `355551c6d11759a2137d794f6154bee9f187aff00d09f7f13887d82a052f3bf1`
- `build_manifest` — SHA-256 `5d94dd2985534cfc5477bcb395a73c8eb189df41637db7bf4f6e95eaed98c4e1`
- `diagnostics` — SHA-256 `a40b573053cda943c381742ad672108b1c8985ecc97e2f21dfa604094e31ff63`
- `disassembly` — SHA-256 `fc79aff611b518050aabf8fba9f4e4d9206bbb333c222fa01363938355cb582a`
- `executable` — SHA-256 `8096a9e86313b02d5038903d99f134a5e00416c11de2752492f204fc927fec8d`
- `llvm` — SHA-256 `7d5f93fc6f34eef9c40b3f0e2d14250039f9ca9b2659d70eb67dcc46e4b3851d`
- `optimization_record` — SHA-256 `c1eed531ffbbd0e9d7c3558ecea6e951283dcb7e51ce4ebf7c1144aa66d37c6d`
- `optimized_llvm` — SHA-256 `7bda6a3ae32ec72bf1ac4f39971bba88d5f34fff09f56798c9cdbbf76414598e`
- `trace` — SHA-256 `c93c225da4447178c911c30bbeb170036679a5508fff214878cd7aef5013a3b8`
- `wir` — SHA-256 `071f042e6b7c27df63e03cc4dcc83f39b6061c37ad6802a417bde46133d70fb5`

## Model review coverage and requests

- **Review format:** `weave-loupe-review-plan-v1`
- **Review mode:** `staged`
- **Token estimator:** `utf8-byte-upper-bound-v1`
- **Estimated complete review tokens:** `313702`
- **Request count:** `14`
- **Maximum total tokens:** `524288`
- **Maximum request tokens:** `98304`
- **Maximum artifact tokens:** `262144`
- **Artifact-review completion tokens:** `1024`

### Artifact coverage

#### `metadata` — Reproducibility metadata

- Language: `json`
- UTF-8 bytes: `10295`
- Estimated tokens: `10311`
- SHA-256: `46a8deebcb1b93d5605e8cabf686ba73934614290ba76f8ea2ee7416b48ebaad`
- Complete coverage: `True`
- Covered ranges: `metadata:[0, 10295)@46a8deebcb1b93d5605e8cabf686ba73934614290ba76f8ea2ee7416b48ebaad`

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
- SHA-256: `7d5f93fc6f34eef9c40b3f0e2d14250039f9ca9b2659d70eb67dcc46e4b3851d`
- Complete coverage: `True`
- Covered ranges: `raw_llvm:[0, 5767)@7d5f93fc6f34eef9c40b3f0e2d14250039f9ca9b2659d70eb67dcc46e4b3851d`

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
- UTF-8 bytes: `93622`
- Estimated tokens: `93638`
- SHA-256: `0658b6d3ee570ce39d938cb12d770e94209d57d7b9e09a12fc208f2459a73e0c`
- Complete coverage: `True`
- Covered ranges: `analysis:[0, 86755)@fe4425d7ffeb0f79f73655d63239705d230ad68efd4d3bb9e886e20f64e0755d`, `analysis:[86755, 93622)@28b45c1fdea4e929c19c6c4f5536fc8a1fb04777f757d1ebd4cdd10ef0c5ab25`

#### `build_manifest` — Compiler build manifest

- Language: `json`
- UTF-8 bytes: `696`
- Estimated tokens: `712`
- SHA-256: `5d94dd2985534cfc5477bcb395a73c8eb189df41637db7bf4f6e95eaed98c4e1`
- Complete coverage: `True`
- Covered ranges: `build_manifest:[0, 696)@5d94dd2985534cfc5477bcb395a73c8eb189df41637db7bf4f6e95eaed98c4e1`

#### `trace` — Compiler trace

- Language: `json`
- UTF-8 bytes: `213`
- Estimated tokens: `229`
- SHA-256: `c93c225da4447178c911c30bbeb170036679a5508fff214878cd7aef5013a3b8`
- Complete coverage: `True`
- Covered ranges: `trace:[0, 213)@c93c225da4447178c911c30bbeb170036679a5508fff214878cd7aef5013a3b8`


### Review requests

#### `artifact-0001` — artifact

- Estimated input tokens: `20286`
- Reserved output tokens: `1024`
- Depends on: none
- Covered ranges: `metadata:[0, 10295)@46a8deebcb1b93d5605e8cabf686ba73934614290ba76f8ea2ee7416b48ebaad`
- Prompt SHA-256: `dbcba39a225b017f923481c39edf5ffcc7f6a72003e956f094f1146b6418b6b5`
- Request SHA-256: `06d893982b19cd3fbfe163d92946086e811ba23cb641b7c1021287ce9ed1d00c`
- Requested model: `z-ai/glm-5.2`
- Provider model: `z-ai/glm-5.2`
- Provider response ID: `chatcmpl-70098a8f-5628-4e4a-b27f-42bd9890dac5`
- Finish reason: `stop`
- Provider prompt tokens: `9209`
- Provider completion tokens: `502`
- Provider total tokens: `9711`

#### `artifact-0002` — artifact

- Estimated input tokens: `11798`
- Reserved output tokens: `1024`
- Depends on: none
- Covered ranges: `source:[0, 1822)@344883c033044766e2bfbac4a1bf838b9e07900faffb15f9fe919da6fe69b759`
- Prompt SHA-256: `f134aed7bef32270ae4d9c92dfae34581fe5cb1a10deb1b554dcd8477e5e8248`
- Request SHA-256: `c78c63147f109c3f8feb19e7896fede23cca1f65a6b58a9f81bbd3b879d6b643`
- Requested model: `z-ai/glm-5.2`
- Provider model: `z-ai/glm-5.2`
- Provider response ID: `chatcmpl-5427be6c-441e-415d-aafe-83e6d5700006`
- Finish reason: `stop`
- Provider prompt tokens: `5008`
- Provider completion tokens: `241`
- Provider total tokens: `5249`

#### `artifact-0003` — artifact

- Estimated input tokens: `11251`
- Reserved output tokens: `1024`
- Depends on: none
- Covered ranges: `wir:[0, 1269)@66955504c5683801f61dc176cc98d0c0c27909698197099712ef53956b70d471`
- Prompt SHA-256: `19edc2dafb38e7bc5c99bee1044a8da455b46e5a7ceaf66ab1bbaee2b9ebdca2`
- Request SHA-256: `e59444a8f0d5336ec49ca0f593b59162820624640e72f990a715919668952557`
- Requested model: `z-ai/glm-5.2`
- Provider model: `z-ai/glm-5.2`
- Provider response ID: `chatcmpl-dbfb5a70-9a3f-4266-96f3-5c5ac8675edf`
- Finish reason: `stop`
- Provider prompt tokens: `4873`
- Provider completion tokens: `234`
- Provider total tokens: `5107`

#### `artifact-0004` — artifact

- Estimated input tokens: `15744`
- Reserved output tokens: `1024`
- Depends on: none
- Covered ranges: `raw_llvm:[0, 5767)@7d5f93fc6f34eef9c40b3f0e2d14250039f9ca9b2659d70eb67dcc46e4b3851d`
- Prompt SHA-256: `9b548cc3f754ab830e49a45faff187fbd923376d0359d56be433be27dd4ba77e`
- Request SHA-256: `89bda11979e78c9eb31643f5d07218185f711bd9deeba56a2a013f16860c1a6e`
- Requested model: `z-ai/glm-5.2`
- Provider model: `z-ai/glm-5.2`
- Provider response ID: `chatcmpl-ca50bab3-400a-4297-9ebe-81edeaf68732`
- Finish reason: `stop`
- Provider prompt tokens: `6561`
- Provider completion tokens: `241`
- Provider total tokens: `6802`

#### `artifact-0005` — artifact

- Estimated input tokens: `12216`
- Reserved output tokens: `1024`
- Depends on: none
- Covered ranges: `optimized_llvm:[0, 2227)@7bda6a3ae32ec72bf1ac4f39971bba88d5f34fff09f56798c9cdbbf76414598e`
- Prompt SHA-256: `3ab1448b9ab7d2f9824e8c6fdb6ae54039c561f03ab7edb60d321e38b5731f75`
- Request SHA-256: `8439fb8315722f950dd51b27aa827a1bc01c0a492908c68ae8c085e4a1313601`
- Requested model: `z-ai/glm-5.2`
- Provider model: `z-ai/glm-5.2`
- Provider response ID: `chatcmpl-10ed0ec6-db3c-4473-839b-7ec93a9af2cf`
- Finish reason: `stop`
- Provider prompt tokens: `5238`
- Provider completion tokens: `217`
- Provider total tokens: `5455`

#### `artifact-0006` — artifact

- Estimated input tokens: `11242`
- Reserved output tokens: `1024`
- Depends on: none
- Covered ranges: `assembly:[0, 1262)@355551c6d11759a2137d794f6154bee9f187aff00d09f7f13887d82a052f3bf1`
- Prompt SHA-256: `ae0321aee86662890589626525ffc11fe2ced03b7fce8dde2de7c1f715e81d0a`
- Request SHA-256: `b13b18c7940cffb36919d2c1359621b72c84deeed7d0c97ce0cbce4a4d671fdc`
- Requested model: `z-ai/glm-5.2`
- Provider model: `z-ai/glm-5.2`
- Provider response ID: `chatcmpl-6fd23709-74e9-49bb-a68b-eebd76f212ee`
- Finish reason: `stop`
- Provider prompt tokens: `4948`
- Provider completion tokens: `514`
- Provider total tokens: `5462`

#### `artifact-0007` — artifact

- Estimated input tokens: `17534`
- Reserved output tokens: `1024`
- Depends on: none
- Covered ranges: `disassembly:[0, 7537)@fc79aff611b518050aabf8fba9f4e4d9206bbb333c222fa01363938355cb582a`
- Prompt SHA-256: `65ed9f9ef7914fd196c32159fafac7454342e38a3dd43068edd24e2c400045b6`
- Request SHA-256: `fc45c693f9313a539d2882c8ec5842a10bea07d27eecac40365228c4a2d9ed9a`
- Requested model: `z-ai/glm-5.2`
- Provider model: `z-ai/glm-5.2`
- Provider response ID: `chatcmpl-91272a0c-4299-4e0e-9cb9-d235756c460a`
- Finish reason: `stop`
- Provider prompt tokens: `7712`
- Provider completion tokens: `231`
- Provider total tokens: `7943`

#### `artifact-0008` — artifact

- Estimated input tokens: `21026`
- Reserved output tokens: `1024`
- Depends on: none
- Covered ranges: `optimization_record:[0, 11024)@c1eed531ffbbd0e9d7c3558ecea6e951283dcb7e51ce4ebf7c1144aa66d37c6d`
- Prompt SHA-256: `f21a711c9bbc9b9c6aac2ced53875b0a2df86d6a4f398646823e27b91f89f83f`
- Request SHA-256: `f421d2fd8c1f47248795ec780c62894a23b7e42289cc9eedfe653c05b56f50fd`
- Requested model: `z-ai/glm-5.2`
- Provider model: `z-ai/glm-5.2`
- Provider response ID: `chatcmpl-471047d8-b13a-499e-82aa-852082559c6d`
- Finish reason: `stop`
- Provider prompt tokens: `7403`
- Provider completion tokens: `197`
- Provider total tokens: `7600`

#### `artifact-0009` — artifact

- Estimated input tokens: `10127`
- Reserved output tokens: `1024`
- Depends on: none
- Covered ranges: `diagnostics:[0, 148)@9683b322333373cb4d9534fef10e27edba462e771e2b03e02108d5c6a7fc71ca`
- Prompt SHA-256: `d87d09d55d176315887fea10c303baae911d4bdf43451ae647915d0994fb3447`
- Request SHA-256: `196807074d62aaf9177b0a43f234e7ba4df92372465f584c62c4b9cbdd8a4133`
- Requested model: `z-ai/glm-5.2`
- Provider model: `z-ai/glm-5.2`
- Provider response ID: `chatcmpl-1cc53caf-a7d6-41f3-8e84-704eb4b6f469`
- Finish reason: `stop`
- Provider prompt tokens: `4544`
- Provider completion tokens: `115`
- Provider total tokens: `4659`

#### `artifact-0010` — artifact

- Estimated input tokens: `96753`
- Reserved output tokens: `1024`
- Depends on: none
- Covered ranges: `analysis:[0, 86755)@fe4425d7ffeb0f79f73655d63239705d230ad68efd4d3bb9e886e20f64e0755d`
- Prompt SHA-256: `b44ec6c72487f568794ca865e2ebaf77e5e323f928ffd5c1f54c6d07b4df34ff`
- Request SHA-256: `cd53bdf88029e1d791d7c9d7c890732c7ea142421b4ec415fe0b88612a53e636`
- Requested model: `z-ai/glm-5.2`
- Provider model: `z-ai/glm-5.2`
- Provider response ID: `chatcmpl-926f6d42-83a6-4994-afb4-53b5f49b6df4`
- Finish reason: `stop`
- Provider prompt tokens: `28889`
- Provider completion tokens: `369`
- Provider total tokens: `29258`

#### `artifact-0011` — artifact

- Estimated input tokens: `16869`
- Reserved output tokens: `1024`
- Depends on: none
- Covered ranges: `analysis:[86755, 93622)@28b45c1fdea4e929c19c6c4f5536fc8a1fb04777f757d1ebd4cdd10ef0c5ab25`
- Prompt SHA-256: `3080413d316293121ade64c6e549c56fd6ae5c130bf19b92cfe699da3a7190b7`
- Request SHA-256: `036094836ddbacbd557085a52ea5c9774972becc1b03904da405fbb530aae8aa`
- Requested model: `z-ai/glm-5.2`
- Provider model: `z-ai/glm-5.2`
- Provider response ID: `chatcmpl-dba7804c-9875-4b46-9500-b1840e0b94da`
- Finish reason: `stop`
- Provider prompt tokens: `6451`
- Provider completion tokens: `168`
- Provider total tokens: `6619`

#### `artifact-0012` — artifact

- Estimated input tokens: `10690`
- Reserved output tokens: `1024`
- Depends on: none
- Covered ranges: `build_manifest:[0, 696)@5d94dd2985534cfc5477bcb395a73c8eb189df41637db7bf4f6e95eaed98c4e1`
- Prompt SHA-256: `db7419b5a6f9f978aa5a989d6326bfd45d4fe0dd622d47c9195c5e8f8f3c1971`
- Request SHA-256: `2b7f50bb2f789f675813724e297681363dce6f3322a74fc9eeac24931384a986`
- Requested model: `z-ai/glm-5.2`
- Provider model: `z-ai/glm-5.2`
- Provider response ID: `chatcmpl-373a3060-8aa1-4135-b30c-e6449bcd7eda`
- Finish reason: `stop`
- Provider prompt tokens: `4734`
- Provider completion tokens: `117`
- Provider total tokens: `4851`

#### `artifact-0013` — artifact

- Estimated input tokens: `10189`
- Reserved output tokens: `1024`
- Depends on: none
- Covered ranges: `trace:[0, 213)@c93c225da4447178c911c30bbeb170036679a5508fff214878cd7aef5013a3b8`
- Prompt SHA-256: `bfe68acdf3ecee8c98167682668396fc2562545900372d3229f9ea15cfa49f60`
- Request SHA-256: `69ced0cbab83c70e39b0e993659a9c9f4b9b5640669a1927b9fc527eaa44f06c`
- Requested model: `z-ai/glm-5.2`
- Provider model: `z-ai/glm-5.2`
- Provider response ID: `chatcmpl-79bc7f34-e0ba-4227-b268-544281e69563`
- Finish reason: `stop`
- Provider prompt tokens: `4557`
- Provider completion tokens: `156`
- Provider total tokens: `4713`

#### `synthesis-0001` — synthesis

- Estimated input tokens: `30569`
- Reserved output tokens: `4096`
- Depends on: `artifact-0001`, `artifact-0002`, `artifact-0003`, `artifact-0004`, `artifact-0005`, `artifact-0006`, `artifact-0007`, `artifact-0008`, `artifact-0009`, `artifact-0010`, `artifact-0011`, `artifact-0012`, `artifact-0013`
- Covered ranges: none
- Prompt SHA-256: `98b65a68c26d6a6098d54701bc8d6d7830bbe5ac7ed87348227737c2833705f7`
- Request SHA-256: `f003aac123891f4e3a343736f6a52e28a6697376e4332c40371fbf789a99f741`
- Requested model: `z-ai/glm-5.2`
- Provider model: `z-ai/glm-5.2`
- Provider response ID: `chatcmpl-5d288e38-4852-445e-b64b-c779afc44411`
- Finish reason: `stop`
- Provider prompt tokens: `11200`
- Provider completion tokens: `1394`
- Provider total tokens: `12594`

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
; source: /tmp/weavec-build-ANIEGt/program.wir
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
        "elapsed_seconds": 0.010824,
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
        "elapsed_seconds": 0.009855,
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
        "elapsed_seconds": 0.009546,
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
        "elapsed_seconds": 0.009587,
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
        "elapsed_seconds": 0.009445,
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
        "elapsed_seconds": 0.009828,
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
        "elapsed_seconds": 0.009396,
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
        "elapsed_seconds": 0.009675,
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
        "elapsed_seconds": 0.009544,
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
          "elapsed_seconds": 0.010824,
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
          "elapsed_seconds": 0.009855,
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
          "elapsed_seconds": 0.009546,
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
          "elapsed_seconds": 0.009587,
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
          "elapsed_seconds": 0.009445,
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
          "elapsed_seconds": 0.009828,
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
          "elapsed_seconds": 0.009396,
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
          "elapsed_seconds": 0.009675,
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
          "elapsed_seconds": 0.009544,
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
  "output": "/tmp/loupe-audit-tkzxh2o4/.audit.loupe.tg9f3eqn/artifacts/program",
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

This final adversarial release-gate review synthesizes the deterministic evidence and exact byte-range artifact reviews for the Weave compiler audit of `docs/audit/fibonacci_runtime.weave`. The compilation pipeline executed successfully with an exit code of 0. All deterministic gates (native budget, optimized LLVM budget, and runtime matrix) passed with zero failures. Cross-stage projection from source to WIR, raw LLVM, optimized LLVM, assembly, and native disassembly is consistent and semantically verified. No blocking findings were identified. The release gate is cleared.

## 2. Verification Matrix

| Artifact | Byte Range | SHA-256 | Status | Cross-Stage Verification |
| :--- | :--- | :--- | :--- | :--- |
| **Metadata** | `[0, 10295)` | `46a8deeb...` | REVIEWED | Auditor identity, bundle hashes, and deterministic gate summary verified. `disassembler_version` is null but `supported: true` with no `failure_reason`. |
| **Source** | `[0, 1822)` | `344883c0...` | REVIEWED | `fib` and `main` defined. Runtime-dependent `while` loop and external `getenv`/`atoi` calls resist constant folding. Input clamped to `[0, 46]`. |
| **WIR** | `[0, 1269)` | `66955504...` | REVIEWED | Externs match source. `fib` early return and iterative loop match source. `main` env parsing and clamping logic intact. |
| **Raw LLVM** | `[0, 5767)` | `7d5f93fc...` | REVIEWED | Well-formed IR. `@main` and `@fib` functions match WIR. Control flow blocks properly branched with no unreachable instructions. |
| **Optimized LLVM** | `[0, 2227)` | `7bda6a3a...` | REVIEWED | `@fib` inlined into `@main`. `getenv`/`atoi` retained. Bounds check (`u > 46`) and base-case (`u < 2`) logic preserved. |
| **Assembly** | `[0, 1262)` | `355551c6...` | REVIEWED | 6 basic blocks. `getenv@PLT`/`atoi@PLT` called. Input defaults to 10, clamps to 46, skips loop if `< 2`. Iterative Fibonacci loop intact. |
| **Disassembly** | `[0, 7537)` | `fc79aff6...` | REVIEWED | Standard ELF64 startup/runtime support verified. User `main` at `0x1150` matches assembly. 0 indirect calls, 0 unreachable instructions. |
| **Optimization Record**| `[0, 11024)` | `c1eed531...` | REVIEWED | `fib` inlining succeeded. External calls not inlined (expected). Vectorization missed (expected for recursive logic). 25 final instructions. |
| **Diagnostics** | `[0, 148)` | `9683b322...` | REVIEWED | Phase "complete", status "succeeded". Empty diagnostics array. Consistent with exit code 0. |
| **Analysis** | `[0, 86755)` | `fe4425d7...` | REVIEWED | WIR to LLVM block deltas verified. `fib` inlined in optimized LLVM. 99 malformed spans reported (likely unmapped source comments). |
| **Analysis** | `[86755, 93622)` | `28b45c1f...` | REVIEWED | Source mapping terminates cleanly. `unresolved_symbols: []`, `valid: true`. |
| **Build Manifest** | `[0, 696)` | `5d94dd29...` | REVIEWED | Target `x86_64-unknown-linux-gnu`. Tools: `weavec`, `clang`, `llc`, `llvm-objdump`. Optimization `O3`. |
| **Trace** | `[0, 213)` | `c93c225d...` | REVIEWED | `weavec-compilation-trace-v1`. Empty events array. Consistent with successful compilation. |

## 3. Blocking Findings

None. All artifact reviews returned `REVIEWED` with no blocking reasons. All essential correctness, safety, ABI, target, runtime, and final-code claims are supported by the supplied deterministic evidence.

## 4. Non-Blocking Opportunities

*   **Disassembler Version Omission**: The metadata artifact reports `disassembler_version: null` while using `llvm-objdump`. While this does not invalidate the native disassembly evidence (as `supported: true` and `failure_reason: null`), capturing the exact disassembler version in future audits would strictly improve reproducibility guarantees.
*   **Malformed Source Spans**: The analysis artifact reported 99 malformed spans (bytes 965-1778) with "no following WIR form". This is almost certainly due to unmapped source comments or trailing documentation in the `.weave` file. While harmless, enhancing the provenance mapper to explicitly classify non-code spans would reduce noise in the analysis report.
*   **Missed Vectorization Logging**: The optimization record notes missed loop and SLP vectorization for `main`. This is expected behavior for recursive/iterative Fibonacci logic that cannot be easily vectorized, but documenting this as an expected optimization constraint in the audit policy could prevent false positives in automated regression checks.

## 5. Suggested Verification

*   **Runtime Matrix Integrity**: Confirm that the 9 cases in `docs/audit/fibonacci_runtime.audit.json` (SHA `dc8e5b6d...`) explicitly cover the default path (`WEAVE_AUDIT_N` unset), the null path, the parsing path, and the lower/upper bound clamping logic (`[0, 46]`).
*   **ABI Compliance**: Verify that the `x86_64` System V ABI is strictly adhered to in the assembly/disassembly, specifically regarding the preservation of callee-saved registers (e.g., `%rbx`) across the `getenv@PLT` and `atoi@PLT` calls.
*   **Deterministic Native Budget**: Ensure the `native_budget` gate configuration explicitly enforces the observed 25-instruction count and 0 indirect calls for this specific audit case to prevent future regressions.

<details>
<summary>Raw model response</summary>

```text
OK

# Weave Compiler Final Adversarial Release-Gate Audit Review

## 1. Executive Summary

This final adversarial release-gate review synthesizes the deterministic evidence and exact byte-range artifact reviews for the Weave compiler audit of `docs/audit/fibonacci_runtime.weave`. The compilation pipeline executed successfully with an exit code of 0. All deterministic gates (native budget, optimized LLVM budget, and runtime matrix) passed with zero failures. Cross-stage projection from source to WIR, raw LLVM, optimized LLVM, assembly, and native disassembly is consistent and semantically verified. No blocking findings were identified. The release gate is cleared.

## 2. Verification Matrix

| Artifact | Byte Range | SHA-256 | Status | Cross-Stage Verification |
| :--- | :--- | :--- | :--- | :--- |
| **Metadata** | `[0, 10295)` | `46a8deeb...` | REVIEWED | Auditor identity, bundle hashes, and deterministic gate summary verified. `disassembler_version` is null but `supported: true` with no `failure_reason`. |
| **Source** | `[0, 1822)` | `344883c0...` | REVIEWED | `fib` and `main` defined. Runtime-dependent `while` loop and external `getenv`/`atoi` calls resist constant folding. Input clamped to `[0, 46]`. |
| **WIR** | `[0, 1269)` | `66955504...` | REVIEWED | Externs match source. `fib` early return and iterative loop match source. `main` env parsing and clamping logic intact. |
| **Raw LLVM** | `[0, 5767)` | `7d5f93fc...` | REVIEWED | Well-formed IR. `@main` and `@fib` functions match WIR. Control flow blocks properly branched with no unreachable instructions. |
| **Optimized LLVM** | `[0, 2227)` | `7bda6a3a...` | REVIEWED | `@fib` inlined into `@main`. `getenv`/`atoi` retained. Bounds check (`u > 46`) and base-case (`u < 2`) logic preserved. |
| **Assembly** | `[0, 1262)` | `355551c6...` | REVIEWED | 6 basic blocks. `getenv@PLT`/`atoi@PLT` called. Input defaults to 10, clamps to 46, skips loop if `< 2`. Iterative Fibonacci loop intact. |
| **Disassembly** | `[0, 7537)` | `fc79aff6...` | REVIEWED | Standard ELF64 startup/runtime support verified. User `main` at `0x1150` matches assembly. 0 indirect calls, 0 unreachable instructions. |
| **Optimization Record**| `[0, 11024)` | `c1eed531...` | REVIEWED | `fib` inlining succeeded. External calls not inlined (expected). Vectorization missed (expected for recursive logic). 25 final instructions. |
| **Diagnostics** | `[0, 148)` | `9683b322...` | REVIEWED | Phase "complete", status "succeeded". Empty diagnostics array. Consistent with exit code 0. |
| **Analysis** | `[0, 86755)` | `fe4425d7...` | REVIEWED | WIR to LLVM block deltas verified. `fib` inlined in optimized LLVM. 99 malformed spans reported (likely unmapped source comments). |
| **Analysis** | `[86755, 93622)` | `28b45c1f...` | REVIEWED | Source mapping terminates cleanly. `unresolved_symbols: []`, `valid: true`. |
| **Build Manifest** | `[0, 696)` | `5d94dd29...` | REVIEWED | Target `x86_64-unknown-linux-gnu`. Tools: `weavec`, `clang`, `llc`, `llvm-objdump`. Optimization `O3`. |
| **Trace** | `[0, 213)` | `c93c225d...` | REVIEWED | `weavec-compilation-trace-v1`. Empty events array. Consistent with successful compilation. |

## 3. Blocking Findings

None. All artifact reviews returned `REVIEWED` with no blocking reasons. All essential correctness, safety, ABI, target, runtime, and final-code claims are supported by the supplied deterministic evidence.

## 4. Non-Blocking Opportunities

*   **Disassembler Version Omission**: The metadata artifact reports `disassembler_version: null` while using `llvm-objdump`. While this does not invalidate the native disassembly evidence (as `supported: true` and `failure_reason: null`), capturing the exact disassembler version in future audits would strictly improve reproducibility guarantees.
*   **Malformed Source Spans**: The analysis artifact reported 99 malformed spans (bytes 965-1778) with "no following WIR form". This is almost certainly due to unmapped source comments or trailing documentation in the `.weave` file. While harmless, enhancing the provenance mapper to explicitly classify non-code spans would reduce noise in the analysis report.
*   **Missed Vectorization Logging**: The optimization record notes missed loop and SLP vectorization for `main`. This is expected behavior for recursive/iterative Fibonacci logic that cannot be easily vectorized, but documenting this as an expected optimization constraint in the audit policy could prevent false positives in automated regression checks.

## 5. Suggested Verification

*   **Runtime Matrix Integrity**: Confirm that the 9 cases in `docs/audit/fibonacci_runtime.audit.json` (SHA `dc8e5b6d...`) explicitly cover the default path (`WEAVE_AUDIT_N` unset), the null path, the parsing path, and the lower/upper bound clamping logic (`[0, 46]`).
*   **ABI Compliance**: Verify that the `x86_64` System V ABI is strictly adhered to in the assembly/disassembly, specifically regarding the preservation of callee-saved registers (e.g., `%rbx`) across the `getenv@PLT` and `atoi@PLT` calls.
*   **Deterministic Native Budget**: Ensure the `native_budget` gate configuration explicitly enforces the observed 25-instruction count and 0 indirect calls for this specific audit case to prevent future regressions.
```
</details>
