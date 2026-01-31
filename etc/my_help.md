```shell

# команды для supervisor
# Статус всех программ
sudo supervisorctl status

# Перезапустить supervisor (сервис)
sudo systemctl restart supervisor

# Подтянуть изменения в конфиге
sudo supervisorctl reread
sudo supervisorctl update

# Запуск / остановка / рестарт одной программы
sudo supervisorctl start trader1
sudo supervisorctl stop trader1
sudo supervisorctl restart trader1

# Запустить/остановить все программы
sudo supervisorctl start all
sudo supervisorctl stop all
sudo supervisorctl restart all

# Перезапустить все программы из конфигов
sudo supervisorctl restart all

# Запустить серию трейдеров 1..50
for i in $(seq 1 50); do sudo supervisorctl start trader$i; done

# Статус только трейдеров
sudo supervisorctl status | grep trader

# Автозапуск ботов после обновления/ребута
# (включить autostart/autorestart для всех trader*)
sudo sed -i 's/^autostart=false/autostart=true/g; s/^autorestart=false/autorestart=true/g' /etc/supervisor/conf.d/traders.conf
sudo supervisorctl reread
sudo supervisorctl update

#Сводка по ключевым строкам:
tail -n 200 /var/log/trader/trader1-log.txt | egrep "tick |skip buy|invest body|debug:|state saved|ERROR|Traceback"

#Показать только позиции и вытащить “цена/цель/Check/Percent”:
tail -n 200 /var/log/trader/trader1-log.txt \
  | awk -F'Current price | Open rate \\+N% | Check | Percent ' '/Position: /{printf "price=%s target=%s check=%s pct=%s\n",$2,$3,$4,$5}'

#Увидеть только новые “тики”:
tail -f /var/log/trader/trader1-log.txt | egrep "tick |skip buy|ERROR|Traceback"

#В реальном времени — только ключевые события:
tail -f /var/log/trader/trader1-log.txt \
  | egrep "tick |skip buy|invest body|debug:|state saved|ERROR|Traceback"

# В реальном времени — только позиции, в компактном виде:
tail -f /var/log/trader/trader1-log.txt \
  | awk -F'Current price | Open rate \\+N% | Check | Percent ' \
    '/Position: /{printf "price=%s target=%s check=%s pct=%s\n",$2,$3,$4,$5}'

#Реалтайм + показать последние 20 строк и дальше смотреть:
tail -n 20 -f /var/log/trader/trader1-log.txt


Как понять, что нужна правка в коде:

# В логах появляются ошибки при создании ордера, типа “price limit / price out of range / exceeds price limit”.
# Ордеры не создаются, хотя сигнал на покупку/продажу есть.
# Проверка логов:

rg -n "price limit|out of range|exceeds" /var/log/trader/trader1-log.txt

#добавить в БД на сервер 3 колонки
mysql -uroot -p
USE thesim;
ALTER TABLE telemetry
  ADD COLUMN profit_usdt DECIMAL(40,20) NULL,
  ADD COLUMN profit_percent DECIMAL(40,20) NULL,
  ADD COLUMN bnb_rate DECIMAL(40,20) NULL;

sudo supervisorctl restart all
```

