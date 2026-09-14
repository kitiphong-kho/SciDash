#!/usr/bin/env bash
# Installs (or updates) the SciDash sync cron job: runs on the 1st and 15th
# of every month at 03:00. Safe to re-run -- replaces any previous
# scidash-sync line instead of duplicating it.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="$(command -v python3)"
MARKER="# scidash-sync"
CRON_LINE="0 3 1,15 * * cd \"$ROOT_DIR\" && mkdir -p logs && \"$PYTHON_BIN\" scripts/sync_scopus.py >> logs/sync.log 2>&1 $MARKER"

TMP_CRON="$(mktemp)"
crontab -l 2>/dev/null | grep -v "$MARKER" > "$TMP_CRON" || true
echo "$CRON_LINE" >> "$TMP_CRON"
crontab "$TMP_CRON"
rm -f "$TMP_CRON"

echo "Installed cron job:"
echo "  $CRON_LINE"
echo
echo "Current crontab:"
crontab -l
