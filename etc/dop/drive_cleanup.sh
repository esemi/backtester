#!/usr/bin/env bash
set -euo pipefail

RCLONE_REMOTE="gdrive:thesim_backups"
SERVER_ID="$(cat /etc/thesim-server-id)"
REMOTE_KEEP_MINUTES=240

sleep "$((RANDOM % 181))"

rclone delete "${RCLONE_REMOTE}/${SERVER_ID}" \
  --min-age "${REMOTE_KEEP_MINUTES}m" \
  --include "*.tar.gz" \
  --drive-use-trash=false \
  --retries 3 \
  --low-level-retries 3

echo "[cleanup] remote cleanup done (keep ${REMOTE_KEEP_MINUTES} minutes)"
