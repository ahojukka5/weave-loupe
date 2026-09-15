#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Independent oracle: qmeasure must not resolve as an ordinary call.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=experiments/compiler-evidence/oracles/_lib.sh
source "$SCRIPT_DIR/_lib.sh"
require_weavec

TMP="$(mktemp -d "${TMPDIR:-/tmp}/loupe-oracle-qmeasure-XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

cat > "$TMP/measure.weave" <<'EOF'
(program
  (name "test-hadamard-measure")
  (version "0.1")
  (extern qrt_ry (params (q i64) (theta_nr i64)) (returns void))
  (extern qrt_rz (params (q i64) (phi_nr i64)) (returns void))
  (extern qrt_measure (params (q i64)) (returns i32))
  (entry main
    (params)
    (returns i32)
    (do
      (let q0 Qubit (const_i64 0))
      (qgate H q0)
      (qmeasure q0 c0)
      (return (local_get c0)))))
EOF

set +e
"$WEAVEC" --frontend "$TMP/measure.wir" "$TMP/measure.weave" \
  >"$TMP/out" 2>"$TMP/err"
status="$?"
set -e
if grep -Fq 'unresolved function qmeasure' "$TMP/err"; then
  oracle_fail "qmeasure was claimed as an ordinary function"
fi
if [[ "$status" -ne 0 ]]; then
  cat "$TMP/err" >&2
  oracle_fail "qmeasure frontend failed"
fi
