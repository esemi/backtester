#!/usr/bin/env bash
set -euo pipefail

SERVER_ID="$(cat /etc/thesim-server-id)"
STATE_DIR="/var/lib/thesim-backup"
LAST_UPLOAD_SUCCESS_FILE="${STATE_DIR}/last_upload_success_epoch"
FAIL_COUNT_FILE="${STATE_DIR}/upload_fail_count"
LAST_ALERT_FILE="${STATE_DIR}/last_upload_alert_epoch"
PENDING_DIR="/opt/thesim/backups/tmp"
UPLOADED_DIR="/opt/thesim/backups/uploaded"
MAX_STALE_MINUTES=60
MAX_PENDING_FILES=9
FAIL_ALERT_THRESHOLD=3
ALERT_COOLDOWN_MINUTES=20
CHECK_SLOTS=6

mkdir -p "${STATE_DIR}" "${PENDING_DIR}" "${UPLOADED_DIR}"
now_epoch="$(date +%s)"
msg=""

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

last_success=0
[ -f "${LAST_UPLOAD_SUCCESS_FILE}" ] && last_success="$(cat "${LAST_UPLOAD_SUCCESS_FILE}" 2>/dev/null || echo 0)"
fail_count=0
[ -f "${FAIL_COUNT_FILE}" ] && fail_count="$(cat "${FAIL_COUNT_FILE}" 2>/dev/null || echo 0)"
pending_count="$(find "${PENDING_DIR}" -mindepth 1 -maxdepth 1 -type f -name "*.tar.gz" | wc -l)"

last_slot="$(( (now_epoch / 600) * 600 - 600 ))"
start_slot="$(( last_slot - (CHECK_SLOTS - 1) * 600 ))"

observed_slots="$({
  find "${PENDING_DIR}" "${UPLOADED_DIR}" -mindepth 1 -maxdepth 1 -type f -name "*.tar.gz" -printf "%f\n" 2>/dev/null || true
} | sed -n 's/.*_\([0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}_[0-9]\{2\}-[0-9]\{2\}-[0-9]\{2\}\)\.tar\.gz/\1/p' | while read -r ts; do
  dt="${ts:0:10} ${ts:11:2}:${ts:14:2}:${ts:17:2}"
  ep="$(date -d "$dt" +%s 2>/dev/null || true)"
  [ -n "$ep" ] || continue
  slot="$(( (ep / 600) * 600 ))"
  if [ "$slot" -ge "$start_slot" ] && [ "$slot" -le "$last_slot" ]; then
    echo "$slot"
  fi
done | sort -n | uniq)"

missing=""
slot="$start_slot"
while [ "$slot" -le "$last_slot" ]; do
  if ! grep -Fxq "$slot" <<< "$observed_slots"; then
    t="$(date -u -d "@$slot" +'%H-%M')"
    missing="${missing}${t} "
  fi
  slot=$((slot + 600))
done

if [ -n "$missing" ]; then
  msg="[ТРЕВОГА] ${SERVER_ID}: пропуск локальных архивов по слотам (UTC): ${missing}"
elif [ "$pending_count" -gt "$MAX_PENDING_FILES" ]; then
  msg="[ТРЕВОГА] ${SERVER_ID}: очередь выгрузки растет, pending=${pending_count} (порог ${MAX_PENDING_FILES})"
elif [ "$last_success" -eq 0 ]; then
  msg="[ТРЕВОГА] ${SERVER_ID}: еще нет ни одной успешной выгрузки на Google Drive"
elif [ $((now_epoch - last_success)) -gt $((MAX_STALE_MINUTES * 60)) ]; then
  msg="[ТРЕВОГА] ${SERVER_ID}: нет новой выгрузки на Google Drive более ${MAX_STALE_MINUTES} минут"
elif [ "$fail_count" -ge "$FAIL_ALERT_THRESHOLD" ]; then
  msg="[ТРЕВОГА] ${SERVER_ID}: подряд ошибок выгрузки=${fail_count}"
else
  echo "[monitor] OK pending=${pending_count} fail_count=${fail_count}"
  exit 0
fi

logger -p user.warning -t thesim-backup-monitor "$msg"
last_alert=0
[ -f "${LAST_ALERT_FILE}" ] && last_alert="$(cat "${LAST_ALERT_FILE}" 2>/dev/null || echo 0)"
if [ $((now_epoch - last_alert)) -lt $((ALERT_COOLDOWN_MINUTES * 60)) ]; then
  exit 1
fi

echo "${now_epoch}" > "${LAST_ALERT_FILE}"
send_tg "$msg"
exit 1
