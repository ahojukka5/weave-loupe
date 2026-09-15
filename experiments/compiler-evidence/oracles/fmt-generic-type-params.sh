#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Independent oracle: compact fmt must keep (type-params ...).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=experiments/compiler-evidence/oracles/_lib.sh
source "$SCRIPT_DIR/_lib.sh"
require_weavec

TMP="$(mktemp -d "${TMPDIR:-/tmp}/loupe-oracle-fmt-generic-XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

cat > "$TMP/input.weave" <<'EOF'
(program
  (name "unused-generic")
  (version "0.1")
  (fn identity
    (type-params T)
    (params (value T))
    (returns T)
    (do (return value)))
  (entry main (params) (returns i32) (do (return 0))))
EOF

"$WEAVEC" fmt --output "$TMP/formatted.weave" "$TMP/input.weave"
if ! grep -Fq '(type-params T)' "$TMP/formatted.weave"; then
  oracle_fail "formatter dropped type-params"
fi

"$WEAVEC" --frontend "$TMP/formatted.wir" "$TMP/formatted.weave" \
  2>"$TMP/frontend.err" || {
  cat "$TMP/frontend.err" >&2
  oracle_fail "formatted generic source failed to compile"
}
