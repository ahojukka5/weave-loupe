#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Independent oracle: a tool that refuses --version must not abort build.sh.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=experiments/compiler-evidence/oracles/_lib.sh
source "$SCRIPT_DIR/_lib.sh"
require_weavec_root

BUILD_SH="$WEAVEC_ROOT/scripts/build.sh"
[[ -f "$BUILD_SH" ]] || oracle_fail "scripts/build.sh missing"

TMP="$(mktemp -d "${TMPDIR:-/tmp}/loupe-oracle-build-probe-XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

printf '#!/bin/sh\nexit 1\n' > "$TMP/refuses-version"
printf '#!/bin/sh\necho "llc version 18.1.0"\nexit 0\n' > "$TMP/llc-ok"
chmod +x "$TMP/refuses-version" "$TMP/llc-ok"

set +e
WEAVEC_OPTIMIZER="$TMP/refuses-version" \
  WEAVEC_TARGET_CODEGEN="$TMP/llc-ok" \
  bash "$BUILD_SH" >"$TMP/out" 2>"$TMP/err" &
pid=$!
saw_progress=0
for _ in $(seq 1 45); do
  if grep -qE 'weavec1|SDK|required tool|Downloading|extract' "$TMP/err" \
      2>/dev/null; then
    saw_progress=1
    kill "$pid" 2>/dev/null || true
    wait "$pid" 2>/dev/null || true
    break
  fi
  if ! kill -0 "$pid" 2>/dev/null; then
    wait "$pid" 2>/dev/null || true
    break
  fi
  sleep 1
done
if kill -0 "$pid" 2>/dev/null; then
  kill "$pid" 2>/dev/null || true
  wait "$pid" 2>/dev/null || true
fi
set -e

if [[ "$saw_progress" -ne 1 ]]; then
  cat "$TMP/err" >&2
  oracle_fail "version probe stopped the build before any later work"
fi
