# Shared helpers for independent historical weavec oracles.
# SPDX-License-Identifier: Apache-2.0

oracle_fail() {
  printf '%s\n' "$*" >&2
  exit 1
}

require_weavec_root() {
  if [[ -z "${WEAVEC_ROOT:-}" ]]; then
    oracle_fail "WEAVEC_ROOT is required"
  fi
}

require_weavec() {
  require_weavec_root
  WEAVEC="${WEAVEC:-$WEAVEC_ROOT/build/weavec}"
  if [[ ! -x "$WEAVEC" ]]; then
    oracle_fail "compiler not found: $WEAVEC"
  fi
}
