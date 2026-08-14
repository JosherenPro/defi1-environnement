#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/code_source.XXXXXX")"
ARCHIVE_TMP="$TMP_DIR/code_source.zip"
trap 'rm -f "$ARCHIVE_TMP"; rmdir "$TMP_DIR" 2>/dev/null || true' EXIT

cd "$ROOT_DIR"
zip -qr "$ARCHIVE_TMP" \
  README.md AGENTS.md requirements-project.txt \
  data dashboard src scripts docs \
  -x '*/__pycache__/*' '*.pyc' \
     'dashboard/_*/*' 'qa/*' 'reports/preview/*' 'reports/assets/*'
mv "$ARCHIVE_TMP" "$ROOT_DIR/code_source.zip"
trap - EXIT
echo "Archive créée : $ROOT_DIR/code_source.zip"
