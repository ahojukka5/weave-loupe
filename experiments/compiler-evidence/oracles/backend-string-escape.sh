#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Independent oracle: unknown WIR string escapes must not emit invalid LLVM.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=experiments/compiler-evidence/oracles/_lib.sh
source "$SCRIPT_DIR/_lib.sh"
require_weavec

TMP="$(mktemp -d "${TMPDIR:-/tmp}/loupe-oracle-string-escape-XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

cat > "$TMP/tab.wir" <<'EOF'
(core-module
  (core-version 3)
  (decls
    (extern puts (params (s ptr)) (returns i32))
    (fn main (params) (returns i32)
      (do
        (call_i32 puts (const_string_ptr "hello\tworld"))
        (return (const_i32 0))))))
EOF

set +e
"$WEAVEC" --backend "$TMP/tab.wir" "$TMP/tab.ll" 2>"$TMP/tab.err"
status="$?"
set -e

if [[ "$status" -eq 0 ]]; then
  if command -v llvm-as >/dev/null 2>&1 && [[ -f "$TMP/tab.ll" ]]; then
    if ! llvm-as "$TMP/tab.ll" -o "$TMP/tab.bc" 2>"$TMP/as.err"; then
      oracle_fail "unknown escape produced LLVM that llvm-as rejected"
    fi
  fi
  oracle_fail "unknown string escape \\t was accepted"
fi
if [[ -f "$TMP/tab.ll" ]]; then
  oracle_fail "backend published LLVM after an unknown string escape"
fi
