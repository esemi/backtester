#!/usr/bin/env bash
set -e

# === CONFIG ===
DB_NAME="thesim"
DB_DEFAULTS_FILE="/root/.my.cnf"   # креды (user/pass) для mysqldump
BACKUP_ROOT="/opt/thesim/backups/tmp"

RCLONE_REMOTE="gdrive:thesim_backups"
SERVER_ID="$(cat /etc/thesim-server-id)"

KEEP_MINUTES=2880   # 48 часов

TS="$(date +'%Y-%m-%d_%H-%M-%S')"
WORKDIR="${BACKUP_ROOT}/${TS}"
ARCHIVE="${BACKUP_ROOT}/${SERVER_ID}_${TS}.tar.gz"

mkdir -p "${WORKDIR}"

echo "[+] Dump MySQL"
# Важно: --no-tablespaces чтобы не требовался PROCESS privilege
mysqldump --defaults-file="${DB_DEFAULTS_FILE}" \
  --single-transaction --quick --no-tablespaces \
  "${DB_NAME}" > "${WORKDIR}/db.sql"

echo "[+] Collect trader data (state.pickle + .env)"
FOUND_TRADERS=0

for TRADER_DIR in /home/trader*; do
  [ -d "$TRADER_DIR" ] || continue

  TRADER_NAME="$(basename "$TRADER_DIR")"
  DEST_DIR="${WORKDIR}/${TRADER_NAME}"

  HAS_FILES=0
  mkdir -p "${DEST_DIR}"

  if [ -f "${TRADER_DIR}/state.pickle" ]; then
    cp "${TRADER_DIR}/state.pickle" "${DEST_DIR}/"
    HAS_FILES=1
  fi

  if [ -f "${TRADER_DIR}/.env" ]; then
    cp "${TRADER_DIR}/.env" "${DEST_DIR}/"
    HAS_FILES=1
  fi

  if [ "$HAS_FILES" -eq 1 ]; then
    FOUND_TRADERS=$((FOUND_TRADERS + 1))
  else
    rm -rf "${DEST_DIR}"
  fi
done

if [ "$FOUND_TRADERS" -eq 0 ]; then
  echo "[!] ERROR: No trader data found in /home/trader*"
  exit 1
fi

echo "[i] Traders backed up: ${FOUND_TRADERS}"

echo "[+] Create archive"
tar -czf "${ARCHIVE}" -C "${WORKDIR}" .

echo "[+] Upload to Google Drive"
rclone copy "${ARCHIVE}" "${RCLONE_REMOTE}/${SERVER_ID}/"

echo "[+] Cleanup local tmp"
rm -rf "${WORKDIR}"
rm -f "${ARCHIVE}"

echo "[+] Cleanup old backups on Drive"
# удаляем только архивы .tar.gz старше KEEP_MINUTES в папке конкретного сервера
rclone delete "${RCLONE_REMOTE}/${SERVER_ID}" \
  --min-age "${KEEP_MINUTES}m" \
  --include "*.tar.gz"

echo "[✓] Backup finished: ${TS}"
