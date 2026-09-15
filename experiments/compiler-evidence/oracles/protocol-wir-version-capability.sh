#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Independent oracle: advertised WIR core version must match emitted WIR.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=experiments/compiler-evidence/oracles/_lib.sh
source "$SCRIPT_DIR/_lib.sh"
require_weavec

TMP="$(mktemp -d "${TMPDIR:-/tmp}/loupe-oracle-wir-cap-XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

"$WEAVEC" capabilities --json > "$TMP/capabilities.json"

cat > "$TMP/trivial.weave" <<'EOF'
(program
  (name "trivial")
  (version "0.1")
  (entry main (params) (returns i32) (do (return 0))))
EOF

"$WEAVEC" --frontend "$TMP/trivial.wir" "$TMP/trivial.weave" \
  2>"$TMP/frontend.err" || {
  cat "$TMP/frontend.err" >&2
  oracle_fail "frontend failed while checking WIR capability identity"
}

python3 - "$TMP/capabilities.json" "$TMP/trivial.wir" <<'PY'
import json
import pathlib
import re
import sys

caps = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
wir = pathlib.Path(sys.argv[2]).read_text(encoding="utf-8")
advertised = caps["language"]["wir_core_version"]
match = re.search(r"\(core-version\s+(\d+)\)", wir)
if match is None:
    raise SystemExit("emitted WIR has no core-version")
emitted = int(match.group(1))
if int(advertised) != emitted:
    raise SystemExit(
        f"capabilities advertise WIR core {advertised}, frontend emitted {emitted}"
    )
PY
