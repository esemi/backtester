#!/usr/bin/env bash
set -euo pipefail

DB_NAME="thesim"
DB_DEFAULTS_FILE="/root/.my.cnf"
PENDING_DIR="/opt/thesim/backups/tmp"
LOCAL_KEEP_MINUTES=4320

TS="$(date +'%Y-%m-%d_%H-%M-%S')"
WORKDIR="${PENDING_DIR}/${TS}"
SERVER_ID="$(cat /etc/thesim-server-id)"
ARCHIVE="${PENDING_DIR}/${SERVER_ID}_${TS}.tar.gz"

cleanup_current() { rm -rf "${WORKDIR}" 2>/dev/null || true; }
cleanup_old_pending() {
  find "${PENDING_DIR}" -mindepth 1 -maxdepth 1 -type d -mmin +"${LOCAL_KEEP_MINUTES}" -exec rm -rf {} + 2>/dev/null || true
  find "${PENDING_DIR}" -mindepth 1 -maxdepth 1 -type f -name "*.tar.gz" -mmin +"${LOCAL_KEEP_MINUTES}" -delete 2>/dev/null || true
}

send_tg() {
  local text="$1"
  [ -f /etc/thesim/tg.env ] || return 0
  set -a
  # shellcheck disable=SC1091
  source /etc/thesim/tg.env
  set +a
  [ -n "${TG_BOT_TOKEN:-}" ] && [ -n "${TG_CHAT_ID:-}" ] || return 0
  curl -sS -m 15 -X POST "https://api.telegram.org/bot${TG_BOT_TOKEN}/sendMessage" \
    -d "chat_id=${TG_CHAT_ID}" \
    --data-urlencode "text=${text}" >/dev/null 2>&1 || true
}

mkdir -p "${WORKDIR}" "${PENDING_DIR}"
trap cleanup_current EXIT
cleanup_old_pending

mysqldump --defaults-file="${DB_DEFAULTS_FILE}" \
  --single-transaction --quick --no-tablespaces \
  "${DB_NAME}" > "${WORKDIR}/db.sql"

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
  msg="[ТРЕВОГА] ${SERVER_ID}: локальный бэкап не создан, данные trader не найдены"
  send_tg "$msg"
  echo "$msg"
  exit 1
fi

tar -czf "${ARCHIVE}" -C "${WORKDIR}" .
echo "[OK] Local backup created: ${ARCHIVE}"
