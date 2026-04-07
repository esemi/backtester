#!/usr/bin/env bash
set -euo pipefail

PENDING_DIR="/opt/thesim/backups/tmp"
UPLOADED_DIR="/opt/thesim/backups/uploaded"
RCLONE_REMOTE="gdrive:thesim_backups"
SERVER_ID="$(cat /etc/thesim-server-id)"
STATE_DIR="/var/lib/thesim-backup"
LAST_UPLOAD_SUCCESS_FILE="${STATE_DIR}/last_upload_success_epoch"
FAIL_COUNT_FILE="${STATE_DIR}/upload_fail_count"
LOCAL_KEEP_MINUTES=4320
MAX_FILES_PER_RUN=3

mkdir -p "${PENDING_DIR}" "${UPLOADED_DIR}" "${STATE_DIR}"

# Spread upload starts across servers to reduce API spikes.
sleep "$((RANDOM % 1201))"

mapfile -t CANDIDATES < <(find "${PENDING_DIR}" -mindepth 1 -maxdepth 1 -type f -name "*.tar.gz" -mmin +2 -printf "%p\n" | sort | head -n "${MAX_FILES_PER_RUN}")

if [ "${#CANDIDATES[@]}" -eq 0 ]; then
  echo "[upload] queue empty"
  exit 0
fi

for file in "${CANDIDATES[@]}"; do
  [ -f "$file" ] || continue
  base="$(basename "$file")"
  done_mark="${UPLOADED_DIR}/${base}.done"

  if [ -f "${done_mark}" ]; then
    rm -f "$file" 2>/dev/null || true
    continue
  fi

  remote_path="${RCLONE_REMOTE}/${SERVER_ID}/${base}"
  echo "[upload] start ${base}"

  success=0
  for attempt in 1 2 3 4 5; do
    out="$(rclone copyto "$file" "$remote_path" \
      --retries 1 \
      --low-level-retries 1 \
      --timeout 30m \
      --contimeout 30s 2>&1)" && rc=0 || rc=$?

    if [ "$rc" -eq 0 ]; then
      success=1
      break
    fi

    retry_after="$(printf '%s' "$out" | sed -n 's/.*retry after \([0-9][0-9]*\).*/\1/p' | head -n1)"
    if [ -n "$retry_after" ]; then
      sleep_s="$retry_after"
    else
      case "$attempt" in
        1) sleep_s=5 ;;
        2) sleep_s=15 ;;
        3) sleep_s=30 ;;
        4) sleep_s=60 ;;
        *) sleep_s=90 ;;
      esac
    fi

    echo "[upload] fail attempt ${attempt}, sleep ${sleep_s}s: ${out}"
    sleep "$sleep_s"
  done

  if [ "$success" -eq 1 ]; then
    touch "$done_mark"
    mv -f "$file" "${UPLOADED_DIR}/${base}" 2>/dev/null || rm -f "$file"
    date +%s > "${LAST_UPLOAD_SUCCESS_FILE}"
    echo 0 > "${FAIL_COUNT_FILE}"
    echo "[upload] success ${base}"
  else
    cur=0
    [ -f "${FAIL_COUNT_FILE}" ] && cur="$(cat "${FAIL_COUNT_FILE}" 2>/dev/null || echo 0)"
    cur=$((cur + 1))
    echo "$cur" > "${FAIL_COUNT_FILE}"
    echo "[upload] failed ${base}, consecutive_failures=${cur}"
  fi
done

find "${UPLOADED_DIR}" -mindepth 1 -maxdepth 1 -type f -name "*.tar.gz" -mmin +"${LOCAL_KEEP_MINUTES}" -delete 2>/dev/null || true
find "${UPLOADED_DIR}" -mindepth 1 -maxdepth 1 -type f -name "*.done" -mmin +"${LOCAL_KEEP_MINUTES}" -delete 2>/dev/null || true

echo "[upload] cycle done"
