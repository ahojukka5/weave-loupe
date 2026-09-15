#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Independent oracle: Option/Result helpers must emit balanced WIR.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=experiments/compiler-evidence/oracles/_lib.sh
source "$SCRIPT_DIR/_lib.sh"
require_weavec

OPTION="$WEAVEC_ROOT/stdlib/option.weave"
RESULT="$WEAVEC_ROOT/stdlib/result.weave"
[[ -f "$OPTION" && -f "$RESULT" ]] || oracle_fail "stdlib Option/Result missing"

TMP="$(mktemp -d "${TMPDIR:-/tmp}/loupe-oracle-enum-XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

cat > "$TMP/app.weave" <<'EOF'
(program
  (name "helpers")
  (version "0.1")
  (entry main
    (params)
    (returns i32)
    (do
      (let some (type-app Option i32) (variant Option (type-args i32) Some 4))
      (let none (type-app Option i32) (variant Option (type-args i32) None))
      (let ok (type-app Result i32 i32) (variant Result (type-args i32 i32) Ok 5))
      (let err (type-app Result i32 i32) (variant Result (type-args i32 i32) Err 1))
      (if
        (condition (op not (call option_is_some (type-args i32) some)))
        (then (do (return 10))))
      (if
        (condition (op not (call option_is_none (type-args i32) none)))
        (then (do (return 11))))
      (if
        (condition (op not (call result_is_ok (type-args i32 i32) ok)))
        (then (do (return 12))))
      (if
        (condition (op not (call result_is_err (type-args i32 i32) err)))
        (then (do (return 13))))
      (let a i32 (call option_unwrap_or (type-args i32) some 0))
      (let b i32 (call option_unwrap_or (type-args i32) none 2))
      (let c i32 (call result_unwrap_or (type-args i32 i32) ok 0))
      (let d i32 (call result_unwrap_or (type-args i32 i32) err 3))
      (return (op add (op add a b) (op add c d))))))
EOF

"$WEAVEC" --frontend "$TMP/app.wir" "$OPTION" "$RESULT" "$TMP/app.weave" \
  2>"$TMP/frontend.err" || {
  cat "$TMP/frontend.err" >&2
  oracle_fail "Option/Result helper frontend failed"
}

for needle in \
  '(fn option_is_some__s__i32' \
  '(fn option_is_none__s__i32' \
  '(fn option_unwrap_or__s__i32' \
  '(fn result_is_ok__s__i32__i32' \
  '(fn result_is_err__s__i32__i32' \
  '(fn result_unwrap_or__s__i32__i32'; do
  if ! grep -Fq "$needle" "$TMP/app.wir"; then
    oracle_fail "missing specialized helper $needle"
  fi
done

"$WEAVEC" --backend "$TMP/app.wir" "$TMP/app.ll" 2>"$TMP/backend.err" || {
  cat "$TMP/backend.err" >&2
  oracle_fail "Option/Result helper backend failed"
}
