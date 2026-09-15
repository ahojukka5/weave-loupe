#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Independent oracle: --cache-report must publish bypassed status.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=experiments/compiler-evidence/oracles/_lib.sh
source "$SCRIPT_DIR/_lib.sh"
require_weavec

TMP="$(mktemp -d "${TMPDIR:-/tmp}/loupe-oracle-cache-XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

PROJ="$TMP/app"
mkdir -p "$PROJ/src"
cat > "$PROJ/weave.project" <<'EOF'
(weave-project
  (format 1)
  (name cache-bypass)
  (kind executable)
  (source-roots "src")
  (entry application)
  (output "cache-bypass"))
EOF
cat > "$PROJ/src/application.weave" <<'EOF'
(module application
  (entry main
    (params)
    (returns i32)
    (do (return 0))))
EOF

REPORT="$TMP/cache-report.json"
"$WEAVEC" build --project "$PROJ" \
  --emit-wir "$TMP/app.wir" \
  --cache-dir "$TMP/cache" \
  --cache-report "$REPORT" \
  2>"$TMP/build.err" || {
  cat "$TMP/build.err" >&2
  oracle_fail "project build with --emit-wir failed"
}

if [[ ! -f "$REPORT" ]]; then
  oracle_fail "--cache-report wrote no file"
fi

python3 - "$REPORT" <<'PY'
import json
import pathlib
import sys

report = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
status = report.get("status")
if status != "bypassed":
    raise SystemExit(f"cache report status is {status!r}, expected 'bypassed'")
bypassed_by = report.get("bypassed_by")
if not bypassed_by:
    raise SystemExit("cache report missing bypassed_by")
PY
