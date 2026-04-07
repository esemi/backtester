# TheSIM Backup Setup - инструкция для нового сервера

Документ описывает актуальную схему бэкапов:
- локальный бэкап каждые 10 минут,
- выгрузка очереди в Google Drive каждые 30 минут,
- разброс старта выгрузки до 20 минут,
- мониторинг и Telegram-алерты,
- автоматическая очистка локальных и удаленных архивов.

## 1. Что должно быть на сервере
- Ubuntu 20.04/22.04+
- SSH доступ под `root`
- MySQL с базой `thesim`
- пользователи `trader*` с файлами `state.pickle` и `.env`

## 2. Базовая подготовка
```bash
apt update
apt install -y rclone

mkdir -p /opt/thesim/backups/scripts /opt/thesim/backups/tmp /opt/thesim/backups/uploaded
mkdir -p /var/lib/thesim-backup
```

## 3. Идентификатор сервера
```bash
nano /etc/thesim-server-id
# пример:
# server-bots-21_ip_161.97.79.2

cat /etc/thesim-server-id
```

Шаблон: `etc/dop/thesim-server-id.example`

## 4. Настройка rclone (Google Drive)
```bash
mkdir -p /root/.config/rclone
nano /root/.config/rclone/rclone.conf
rclone lsd gdrive:
```

Шаблон: `etc/dop/rclone.conf.example` (или рабочий `etc/dop/rclone.conf`)

## 5. MySQL доступ для бэкапа
```bash
nano /root/.my.cnf
chmod 600 /root/.my.cnf
```

Шаблон: `etc/dop/my.cnf.example`

Если пользователя `backup` нет, создать в MySQL:
```sql
CREATE USER 'backup'@'localhost' IDENTIFIED BY 'replace_me';
GRANT SELECT, LOCK TABLES, SHOW VIEW, TRIGGER ON thesim.* TO 'backup'@'localhost';
GRANT PROCESS ON *.* TO 'backup'@'localhost';
FLUSH PRIVILEGES;
```

Проверка:
```bash
mysqldump --defaults-file=/root/.my.cnf --no-tablespaces thesim > /tmp/test.sql
rm /tmp/test.sql
```

## 6. Telegram для алертов
```bash
nano /etc/thesim/tg.env
chmod 600 /etc/thesim/tg.env
```

Шаблон: `etc/dop/tg.env.example`

## 7. Установка скриптов бэкапа
Скопировать на сервер файлы из `etc/dop`:
- `backup_local.sh`
- `upload_missing_backups.sh`
- `drive_cleanup.sh`
- `check_gdrive_freshness.sh`

И положить в `/opt/thesim/backups/scripts/`, затем:
```bash
chmod +x /opt/thesim/backups/scripts/backup_local.sh
chmod +x /opt/thesim/backups/scripts/upload_missing_backups.sh
chmod +x /opt/thesim/backups/scripts/drive_cleanup.sh
chmod +x /opt/thesim/backups/scripts/check_gdrive_freshness.sh
```

## 8. Установка systemd unit/timer
Скопировать на сервер файлы из `etc/dop` в `/etc/systemd/system/`:
- `thesim-backup.service`
- `thesim-backup.timer`
- `thesim-upload.service`
- `thesim-upload.timer`
- `thesim-drive-cleanup.service`
- `thesim-drive-cleanup.timer`
- `thesim-backup-monitor.service`
- `thesim-backup-monitor.timer`

Применение:
```bash
systemctl daemon-reload
systemctl enable --now thesim-backup.timer
systemctl enable --now thesim-upload.timer
systemctl enable --now thesim-drive-cleanup.timer
systemctl enable --now thesim-backup-monitor.timer
```

## 9. Что делает каждый процесс
- `thesim-backup.timer` (`*:0/10`): создает локальный архив в `tmp`.
- `thesim-upload.timer` (`*:0/30`, `RandomizedDelaySec=1200`): выгружает очередь на Drive.
- `thesim-drive-cleanup.timer` (раз в 6 часов): удаляет старые архивы на Drive.
- `thesim-backup-monitor.timer` (`*:0/10`): контроль пайплайна и алерты.

## 10. Актуальные параметры (важно)
В текущих шаблонах:
- локальное хранение: `LOCAL_KEEP_MINUTES=4320` (3 дня),
- выгрузка за цикл: `MAX_FILES_PER_RUN=3`,
- джиттер внутри upload-скрипта: до 20 минут,
- удаленное хранение: `REMOTE_KEEP_MINUTES=240` (4 часа),
- алерт по очереди: `MAX_PENDING_FILES=9`,
- алерт по отсутствию выгрузки: `MAX_STALE_MINUTES=60`.

## 11. Проверка после установки
```bash
systemctl list-timers --all | grep thesim-

journalctl -u thesim-backup.service -n 50 --no-pager
journalctl -u thesim-upload.service -n 50 --no-pager
journalctl -u thesim-backup-monitor.service -n 50 --no-pager
```

Проверить наличие локальных архивов:
```bash
ls -lah /opt/thesim/backups/tmp
```

## 12. Диагностика
- Ошибки квот Google Drive ищи в:
```bash
journalctl -u thesim-upload.service --since "2 hours ago" --no-pager
```

- Если монитор показывает пропуски по слотам, сверяй имена файлов `*.tar.gz` в `tmp` и `uploaded`.

## 13. Восстановление из бэкапа
1. Найти архив на Drive:
```bash
rclone lsl "gdrive:thesim_backups/<SERVER_ID>/"
```
2. Скачать архив:
```bash
cd /root
rclone copy "gdrive:thesim_backups/<SERVER_ID>/<ARCHIVE>.tar.gz" .
```
3. Распаковать:
```bash
mkdir -p /root/restore
tar -xzf <ARCHIVE>.tar.gz -C /root/restore
```
4. Восстановить БД:
```bash
mysql --defaults-file=/root/.my.cnf -e "CREATE DATABASE IF NOT EXISTS thesim;"
mysql --defaults-file=/root/.my.cnf thesim < /root/restore/db.sql
```
5. Восстановить файлы trader:
```bash
cd /root/restore
for d in trader*; do
  TRADER="/home/$d"
  mkdir -p "$TRADER"
  cp "$d/state.pickle" "$TRADER/" 2>/dev/null || true
  cp "$d/.env" "$TRADER/" 2>/dev/null || true
  chown -R "$d:$d" "$TRADER"
done
```

## 14. Быстрый запуск за 5 минут
```bash
# 1) Базовые пакеты и папки
apt update && apt install -y rclone
mkdir -p /opt/thesim/backups/scripts /opt/thesim/backups/tmp /opt/thesim/backups/uploaded
mkdir -p /var/lib/thesim-backup /root/.config/rclone

# 2) Обязательные конфиги
nano /etc/thesim-server-id
nano /root/.config/rclone/rclone.conf
nano /root/.my.cnf && chmod 600 /root/.my.cnf
nano /etc/thesim/tg.env && chmod 600 /etc/thesim/tg.env

# 3) Скопировать скрипты в /opt/thesim/backups/scripts/
# backup_local.sh upload_missing_backups.sh drive_cleanup.sh check_gdrive_freshness.sh
chmod +x /opt/thesim/backups/scripts/*.sh

# 4) Скопировать systemd файлы в /etc/systemd/system/
# thesim-backup.service thesim-backup.timer
# thesim-upload.service thesim-upload.timer
# thesim-drive-cleanup.service thesim-drive-cleanup.timer
# thesim-backup-monitor.service thesim-backup-monitor.timer

# 5) Включить таймеры
systemctl daemon-reload
systemctl enable --now thesim-backup.timer
systemctl enable --now thesim-upload.timer
systemctl enable --now thesim-drive-cleanup.timer
systemctl enable --now thesim-backup-monitor.timer

# 6) Быстрая проверка
systemctl list-timers --all | grep thesim-
journalctl -u thesim-backup.service -n 30 --no-pager
journalctl -u thesim-upload.service -n 30 --no-pager
journalctl -u thesim-backup-monitor.service -n 30 --no-pager
```
