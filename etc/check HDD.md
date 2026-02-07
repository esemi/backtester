# HDD Guard (Telegram + supervisor stop)

Цель: если диск `/` (root filesystem) заполняется до **90%+**, сервер:

- отправляет уведомление в Telegram
- выполняет `sudo supervisorctl stop all`
- не спамит: шлет 1 alert при достижении порога и 1 "recovery" когда место снова стало < порога

## 0) Что нужно заранее

- Telegram bot token (через BotFather)
- `chat_id` (куда слать: личка/группа/канал)
- На сервере должны быть: `curl`, `systemd`, `supervisorctl`

Проверка:

```bash
command -v curl systemctl supervisorctl
```

Если `curl` нет:

```bash
apt update && apt install -y curl
```

## 1) Секреты Telegram

Создаем файл с токеном и chat_id:

```bash
sudo mkdir -p /etc/thesim
sudo nano /etc/thesim/tg.env
```

Содержимое (замени значения):

```bash
TG_BOT_TOKEN="8147056290:AAHKZ5rgFkU-2tPUWnXc7TmQsnt67O92HT8"
TG_CHAT_ID="-1002917122599"
```

Права:

```bash
sudo chmod 600 /etc/thesim/tg.env
```

## 2) Скрипт проверки диска

```bash
sudo nano /usr/local/bin/disk_guard.sh
```

Содержимое:

```bash
#!/usr/bin/env bash
set -euo pipefail

THRESHOLD=90
MOUNT="/"
STATE="/var/tmp/disk_guard.triggered"
SERVER_ID="$(cat /etc/thesim-server-id 2>/dev/null || hostname)"

# Load Telegram secrets
set -a
source /etc/thesim/tg.env
set +a

use_pct="$(df -P "$MOUNT" | awk 'NR==2{gsub("%","",$5); print $5}')"

send() {
  local msg="$1"
  curl -fsS -X POST "https://api.telegram.org/bot${TG_BOT_TOKEN}/sendMessage" \
    -d "chat_id=${TG_CHAT_ID}" \
    --data-urlencode "text=${msg}" >/dev/null
}

if [ "$use_pct" -ge "$THRESHOLD" ]; then
  if [ ! -f "$STATE" ]; then
    touch "$STATE"
    send "HDD usage ${use_pct}% on ${SERVER_ID} ($(hostname), ${MOUNT}) >= ${THRESHOLD}%. Running: supervisorctl stop all"
    sudo supervisorctl stop all || true
  fi
else
  # Send recovery once, then reset latch
  if [ -f "$STATE" ]; then
    send "HDD usage recovered: ${use_pct}% on ${SERVER_ID} ($(hostname), ${MOUNT}) < ${THRESHOLD}%."
    rm -f "$STATE"
  fi
fi
```

Права:

```bash
sudo chmod 0755 /usr/local/bin/disk_guard.sh
```

Важно: `sudo supervisorctl stop all` должен работать без запроса пароля.
Если у тебя `root` запускает скрипт, обычно это уже ок.

## 3) systemd service + timer (раз в минуту)

Service:

```bash
sudo nano /etc/systemd/system/disk-guard.service
```

```ini
[Unit]
Description=Disk usage guard (Telegram + stop supervisor)

[Service]
Type=oneshot
ExecStart=/usr/local/bin/disk_guard.sh
```

Timer:

```bash
sudo nano /etc/systemd/system/disk-guard.timer
```

```ini
[Unit]
Description=Run disk guard every minute

[Timer]
OnBootSec=1min
OnUnitActiveSec=5min
AccuracySec=10s
Persistent=true

[Install]
WantedBy=timers.target
```

Включить:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now disk-guard.timer
sudo systemctl list-timers | grep disk-guard
```

## 4) Проверка

Запуск вручную:

```bash
sudo /usr/local/bin/disk_guard.sh
```

Логи systemd:

```bash
journalctl -u disk-guard.service -n 50 --no-pager
```

## 5) Замечания по безопасности

- Не пиши токен/чат в публичные логи.
- `TG_CHAT_ID` для группы обычно отрицательный.
