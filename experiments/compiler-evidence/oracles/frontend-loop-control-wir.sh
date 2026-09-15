#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Independent oracle: for/break/continue must emit runnable WIR.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=experiments/compiler-evidence/oracles/_lib.sh
source "$SCRIPT_DIR/_lib.sh"
require_weavec

TMP="$(mktemp -d "${TMPDIR:-/tmp}/loupe-oracle-loop-XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

cat > "$TMP/sum.weave" <<'EOF'
(program
  (name "sum")
  (version "0.1")
  (entry main
    (params)
    (returns i32)
    (do
      (let total 0)
      (for (range i 0 4)
        (do
          (set total (op add total i))))
      (return total))))
EOF

"$WEAVEC" --frontend "$TMP/sum.wir" "$TMP/sum.weave" 2>"$TMP/sum.err" || {
  cat "$TMP/sum.err" >&2
  oracle_fail "for-range frontend failed"
}

cat > "$TMP/break.weave" <<'EOF'
(program
  (name "break")
  (version "0.1")
  (entry main
    (params)
    (returns i32)
    (do
      (let total 0)
      (for (range i 0 10)
        (do
          (if (condition (op equal i 3))
            (then (do (break))))
          (set total (op add total i))))
      (return total))))
EOF

"$WEAVEC" --frontend "$TMP/break.wir" "$TMP/break.weave" 2>"$TMP/break.err" || {
  cat "$TMP/break.err" >&2
  oracle_fail "break frontend failed"
}

"$WEAVEC" build "$TMP/sum.weave" -o "$TMP/sum" 2>"$TMP/build.err" || {
  cat "$TMP/build.err" >&2
  oracle_fail "for-range native build failed"
}
set +e
"$TMP/sum"
status="$?"
set -e
# 0+1+2+3 == 6
if [[ "$status" -ne 6 ]]; then
  oracle_fail "for-range program exited $status, expected 6"
fi
