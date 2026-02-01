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

#Чтобы вывести последние 20 строк (однократно):
tail -n 20 /var/log/trader/trader1-log.txt

#А только строки с ошибками:
tail -n 200 /var/log/trader/trader1-log.txt | grep -i error | tail -n 20

#переключение веток
git checkout master     
git checkout deploy-bots
git checkout bybit
git checkout feature-telemetry-profit
git branch --show-current

#Как понять, что нужна правка в коде:
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
  ADD COLUMN `open_price` DECIMAL(40,20) NULL;

sudo supervisorctl restart all

#добавить с проверкой колонки на сервер
mysql -h localhost -u root -p'yLMReqr7ofPt9E2pgslYXwhchRAKDnvqBddjkua6!' thesim -e "
SET @db := DATABASE();

SET @col1 := (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='telemetry' AND COLUMN_NAME='profit_usdt');
SET @col2 := (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='telemetry' AND COLUMN_NAME='profit_percent');
SET @col3 := (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='telemetry' AND COLUMN_NAME='bnb_rate');
SET @col4 := (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='telemetry' AND COLUMN_NAME='open_price');

SET @sql := CONCAT(
  'ALTER TABLE telemetry',
  IF(@col1=0, ' ADD COLUMN profit_usdt DECIMAL(40,20) NULL,', ''),
  IF(@col2=0, ' ADD COLUMN profit_percent DECIMAL(40,20) NULL,', ''),
  IF(@col3=0, ' ADD COLUMN bnb_rate DECIMAL(40,20) NULL,', ''),
  IF(@col4=0, ' ADD COLUMN open_price DECIMAL(40,20) NULL,', ''),
  ' DROP COLUMN __dummy__'
);

SET @sql := REPLACE(@sql, ', DROP COLUMN __dummy__', '');
SET @sql := REPLACE(@sql, 'ALTER TABLE telemetry DROP COLUMN __dummy__', 'SELECT 1');

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
"
# проверка что колонки добавились

mysql -h localhost -u root -p'yLMReqr7ofPt9E2pgslYXwhchRAKDnvqBddjkua6!' thesim -e "DESCRIBE telemetry;"




# смотреть таблицу телеметрии одного бота

mysql -h localhost -u root -p'yLMReqr7ofPt9E2pgslYXwhchRAKDnvqBddjkua6!' thesim \
  -e "SELECT id, bot_name, tick_number, bid, ask, buy_price, sell_price, created_at, bnb_rate,
             ROUND(profit_usdt, 3) AS profit_usdt,
             ROUND(profit_percent, 2) AS profit_percent
      FROM telemetry
      WHERE bot_name='trader3'
      ORDER BY tick_number DESC
      LIMIT 100;" \
  -B | column -t -s $'\t' | less -S

"

# смотреть таблицу телеметрии одного бота

for i in $(seq 1 50); do
  echo "===== trader$i ====="
  mysql -h localhost -u root -p'yLMReqr7ofPt9E2pgslYXwhchRAKDnvqBddjkua6!' thesim \
    -e "SELECT id, bot_name, tick_number, bid, ask, buy_price, sell_price, created_at, bnb_rate,
               ROUND(profit_usdt, 3) AS profit_usdt,
               ROUND(profit_percent, 2) AS profit_percent
        FROM telemetry
        WHERE bot_name='trader$i'
        ORDER BY tick_number DESC
        LIMIT 20;" -B | column -t -s $'\t'
  echo
done

"

```

