# TheSIM Backup Setup — инструкция для нового сервера

Эта инструкция описывает, как подключить сервер к общей системе бэкапов TheSIM:
- MySQL база `thesim`
- файлы `state.pickle` и `.env` у пользователей `trader*`
- загрузка архивов в Google Drive
- автозапуск при старте сервера + каждые 10 минут
- хранение бэкапов 2 дня

Инструкция рассчитана на **сервер без GUI**.
---

## 1. Предварительные требования

На сервере должно быть:
- Ubuntu 20.04 / 22.04
- доступ по SSH под `root`
- MySQL
- пользователи:
  - `admin-agent`
  - `trader1 … traderN`
- база данных: `thesim`

## 2. Установка 

```bash
# заходим по ROOT!!!
## На каждом сервере свой
sudo nano /etc/thesim-server-id
	server-bots-27_ip_152.228.135.107 #пишем название сервера, далее на гугле драйв он будет так папку называть
cat /etc/thesim-server-id

apt update
apt install -y rclone
mkdir -p /root/.config/rclone
nano /root/.config/rclone/rclone.conf #код из файла
rclone lsd gdrive:  #Если видны папки — Google Drive подключён.
nano /root/.my.cnf #Создай файл с кредами чтоб не запрашивал пароль
[client]
user=backup
password=yLMReqr7ofPt9E2pgslYXwhchRAKDnvqBddjkua6! #проверить пароль на сервере от мускула

chmod 600 /root/.my.cnf

# Заходими в MySQL под root:
sudo mysql -u root -p
# Пользователь MySQL для бэкапов (запустить в mysql под root) запускаем далее 4 строчки разом
CREATE USER 'backup'@'localhost' IDENTIFIED BY 'yLMReqr7ofPt9E2pgslYXwhchRAKDnvqBddjkua6!'; #проверить пароль на сервере от мускула
GRANT SELECT, LOCK TABLES, SHOW VIEW, TRIGGER ON thesim.* TO 'backup'@'localhost';
GRANT PROCESS ON *.* TO 'backup'@'localhost'; # нужно для tablespaces
FLUSH PRIVILEGES;
exit
#Проверка:
mysqldump --defaults-file=/root/.my.cnf --no-tablespaces thesim > /tmp/test.sql
rm /tmp/test.sql
#Создание директорий бэкапа
mkdir -p /opt/thesim/backups/scripts
mkdir -p /opt/thesim/backups/tmp
#Установка backup.sh
nano /opt/thesim/backups/scripts/backup.sh # код из файла
chmod +x /opt/thesim/backups/scripts/backup.sh
/opt/thesim/backups/scripts/backup.sh #Тестовый запуск
#Systemd service
nano /etc/systemd/system/thesim-backup.service # на 16 и 18 и 21 сервеар с этого места сделать
[Unit]
Description=TheSIM backup to Google Drive
Wants=network-online.target
After=network-online.target mysql.service

[Service]
Type=oneshot
User=root
ExecStartPre=/usr/bin/flock -n /var/lock/thesim-backup.lock -c "true"
ExecStart=/opt/thesim/backups/scripts/backup.sh
TimeoutStartSec=1800
#Systemd timer (каждые 10 минут + старт сервера) 
nano /etc/systemd/system/thesim-backup.timer
[Unit]
Description=Run TheSIM backup every 10 minutes

[Timer]
OnBootSec=2min
OnUnitActiveSec=10min
AccuracySec=30s
Persistent=true

[Install]
WantedBy=timers.target
systemctl daemon-reload
systemctl enable --now thesim-backup.timer
systemctl list-timers --all | grep thesim-backup #Проверка:
#Логи и контроль
journalctl -u thesim-backup.service -n 200 --no-pager

# Если journalctl пустой (после клонирования/смены machine-id) — требуется:
mkdir -p /var/log/journal/$(cat /etc/machine-id)
systemd-tmpfiles --create --prefix /var/log/journal
systemctl restart systemd-journald
systemctl start thesim-backup.service
journalctl -u thesim-backup.service -n 50 --no-pager

#--------------Восстановление-----------------------------
# Предусловия
# Ты под root
# rclone настроен (Google Drive доступен)
# MySQL установлен
# Пользователи trader* существуют
rclone lsl "gdrive:thesim_backups/bots-7/" #Найти нужный бэкап на Google Drive
#Выбери нужный архив, например:
	bots-7_2026-01-22_17-37-56.tar.gz
#Скачать бэкап на сервер
cd /root
rclone copy "gdrive:thesim_backups/ИМЯ_СЕРВЕРА/АРХИВ.tar.gz" .
#rclone copy "gdrive:thesim_backups/bots-7/bots-7_2026-01-22_17-37-56.tar.gz" .
#Распаковать архив
mkdir restore
tar -xzf bots-7_2026-01-22_17-37-56.tar.gz -C restore
cd restore
ls
#Ожидаемо:
db.sql
trader1/
trader2/
...
#Восстановить базу MySQL Осторожно: база будет перезаписана.
#Убедись, что база существует
mysql --defaults-file=/root/.my.cnf -e "CREATE DATABASE IF NOT EXISTS thesim;"
#Восстановление
mysql --defaults-file=/root/.my.cnf thesim < db.sql
# Проверка:
mysql --defaults-file=/root/.my.cnf -e "SHOW TABLES FROM thesim;"
#Восстановить трейдеров (state + env)
for d in trader*; do
  TRADER="/home/$d"
  mkdir -p "$TRADER"
  cp "$d/state.pickle" "$TRADER/" 2>/dev/null || true
  cp "$d/.env" "$TRADER/" 2>/dev/null || true
  chown -R "$d:$d" "$TRADER"
done
#Восстановить одного трейдера (например trader17)
mkdir -p /home/trader17
cp trader17/state.pickle /home/trader17/
cp trader17/.env /home/trader17/
chown -R trader17:trader17 /home/trader17
#Проверка
ls -l /home/trader17
#Ожидаемо:
state.pickle
.env
#Очистка временных файлов (по желанию)
cd /root
rm -rf restore
rm bots-7_2026-01-22_17-37-56.tar.gz
