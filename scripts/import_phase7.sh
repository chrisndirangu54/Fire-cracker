#!/usr/bin/env bash
set -euo pipefail
# Run from the root of a clone of chrisndirangu54/Fire-cracker
# Usage: bash scripts/import_phase7.sh /path/to/fire_rescue_drone_phase7_rescue_assist.zip
ARCHIVE="${1:?Provide full path to the Phase 7 ZIP archive}"
test -f "$ARCHIVE" || { echo "Archive not found"; exit 1; }
ROOT="$(pwd)"
test -d .git || { echo "Run from the repository root"; exit 1; }
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
python3 - "$ARCHIVE" "$TMP" <<'PY'
import sys, zipfile
from pathlib import Path
archive, destination = sys.argv[1:]
with zipfile.ZipFile(archive) as z:
    for name in z.namelist():
        item = Path(name)
        if item.is_absolute() or '..' in item.parts:
            raise ValueError('Unsafe ZIP path')
        z.extract(name, destination)
PY
SOURCE="$TMP/fire_rescue_drone"
test -f "$SOURCE/app.py"
test -f "$SOURCE/static/index.html"
cp -R "$SOURCE/." "$ROOT/"
rm -rf "$ROOT/__pycache__" "$ROOT/.pytest_cache" "$ROOT/tests/__pycache__"
python3 -m pytest -q
git add app.py static docs ros2_bridge requirements.txt pytest.ini README.md \
  rescue_assistance.py suppression_planner.py safety.py payload.py \
  payload_controller.py drop_zone_validator.py drop_safety.py gas_suppression_sim.py tests
git status --short
echo "Review the staged files, then commit and push to your branch:"
echo "git commit -m 'Import complete Phase 7 indoor rescue simulator'"
echo "git push origin HEAD"
