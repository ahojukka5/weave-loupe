#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Independent oracle: float-to-i32 casts in call position must type as i32.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=experiments/compiler-evidence/oracles/_lib.sh
source "$SCRIPT_DIR/_lib.sh"
require_weavec

TMP="$(mktemp -d "${TMPDIR:-/tmp}/loupe-oracle-float-cast-XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

cat > "$TMP/cast-arg.wir" <<'EOF'
(core-module
  (core-version 3)
  (decls
    (fn take_i32 (params (v i32)) (returns i32)
      (do (return (param_get v))))
    (fn main (params) (returns i32)
      (do
        (let a f64 (const_f64 2.5))
        (let r1 i32 (call_i32 take_i32 (cast_f64_to_i32 (local_get a))))
        (return (local_get r1))))))
EOF

"$WEAVEC" --backend "$TMP/cast-arg.wir" "$TMP/cast-arg.ll" \
  2>"$TMP/backend.err" || {
  cat "$TMP/backend.err" >&2
  oracle_fail "float-to-i32 call-argument module was rejected"
}

if ! grep -Fq 'call i32 @take_i32(i32' "$TMP/cast-arg.ll"; then
  oracle_fail "call site was not typed as i32"
fi
if grep -E 'call i32 @take_i32\((double|float) ' "$TMP/cast-arg.ll"; then
  oracle_fail "call site was typed from the pre-cast float"
fi

if command -v llvm-as >/dev/null 2>&1; then
  llvm-as "$TMP/cast-arg.ll" -o "$TMP/cast-arg.bc" || {
    oracle_fail "llvm-as rejected the emitted call-site types"
  }
fi
