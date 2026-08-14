#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/dashboard.XXXXXX")"
ARCHIVE_TMP="$TMP_DIR/dashboard.zip"
trap 'rm -f "$ARCHIVE_TMP"; rmdir "$TMP_DIR" 2>/dev/null || true' EXIT

cd "$ROOT_DIR/dashboard"
zip -qr "$ARCHIVE_TMP" app.py requirements.txt README.md analysis assets .streamlit \
  -x '*/__pycache__/*' '*.pyc'
cd "$ROOT_DIR"
# Les données sources et les liens officiels rendent le pipeline inclus dans
# l'archive réellement reproductible, sans dépendre du dépôt parent.
zip -qr "$ARCHIVE_TMP" data docs/liens_data.md \
  -x '*/__pycache__/*' '*.pyc'
mv "$ARCHIVE_TMP" "$ROOT_DIR/dashboard.zip"
trap - EXIT
echo "Archive créée : $ROOT_DIR/dashboard.zip"
