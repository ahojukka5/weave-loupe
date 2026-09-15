#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Independent oracle: weavec fmt must preserve decimal literals.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=experiments/compiler-evidence/oracles/_lib.sh
source "$SCRIPT_DIR/_lib.sh"
require_weavec

TMP="$(mktemp -d "${TMPDIR:-/tmp}/loupe-oracle-fmt-decimal-XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

cat > "$TMP/input.weave" <<'EOF'
(program
  (name "decimals")
  (version "0.1")
  (entry main
    (params)
    (returns i32)
    (do
      (let x 1.5)
      (return 0))))
EOF

"$WEAVEC" fmt --output "$TMP/formatted.weave" "$TMP/input.weave"
if ! grep -Fq '1.5' "$TMP/formatted.weave"; then
  oracle_fail "formatter dropped decimal literal 1.5"
fi

"$WEAVEC" --frontend "$TMP/formatted.wir" "$TMP/formatted.weave" \
  2>"$TMP/frontend.err" || {
  cat "$TMP/frontend.err" >&2
  oracle_fail "formatted decimal source failed to compile"
}
