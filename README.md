Crypto trading robot
---
Trading strategy backtesting utility and trading robot implementation for Binance and ByBit cryptocurrency exchanges.


### Setup on windows
- [install python 3.11](https://www.python.org/downloads/windows/)
- [install git](https://gitforwindows.org/)
- [install redis](https://redis.io/docs/getting-started/installation/install-redis-on-windows/)


### Download code
```bash
git clone https://github.com/esemi/backtester.git
cd backtester
pip install -r requirements.txt
```

Create env file to override default config
```bash
cp .env.example .env
```

### Run rates loader tool
```bash
python -m app.sampler --symbol SOLUSDT --interval 1h --from-date=2023-01-01
python -m app.sampler --symbol SOLUSDT --interval 1h --from-date=2023-01-01 --end-date=2023-01-15
python -m app.sampler --symbol SOLUSDT --interval 1h --from-date=2023-01-01 --end-date=2023-01-15 --exchange=bybit
```

### Run backtesting tool
```bash
python -m app.backtester
```

### Run trading tool
```bash
python -m app.trader
```

### How to
#### Как поменять настройки бота
- идём в [файл настроек](https://github.com/esemi/backtester/blob/trader1/etc/env) нашего бота
- изменяем любые настройки (пример можно [посмотреть тут](https://github.com/esemi/backtester/blob/master/.env.example))
- сохраняем изменения
- в ближайшую минуту новые настройки попадут на сервер, остановят запущенного бота и запустят нового с указанными настройками.


#### Как включить реальную торговлю
- идём в [файл настроек](https://github.com/esemi/backtester/blob/trader1/etc/env) нашего бота
- меняем или добавляем строчку `dry_run=false`
- сохраняем изменения
- в ближайшую минуту новые настройки попадут на сервер и перезапустят бота для реальных торгов


#### Как выключить бота
- идём в [файл настроек](https://github.com/esemi/backtester/blob/trader1/etc/env) нашего бота
- меняем или добавляем строчку `ticks_amount_limit=0`
- сохраняем изменения
- в ближайшую минуту новые настройки попадут на сервер и остановят работающего бота


#### Как переключиться на стратегию с плавающей ставкой
- идём в [файл настроек](https://github.com/esemi/backtester/blob/trader1/etc/env) нашего бота
- меняем или добавляем строчку `strategy_type=floating`
- сохраняем изменения
- в ближайшую минуту новые настройки попадут на сервер


#### Как ограничить количество открытых позиций
- идём в [файл настроек](https://github.com/esemi/backtester/blob/trader1/etc/env) нашего бота
- меняем или добавляем строчку `hold_position_limit=100` (накапливать на руках не больше 100 позиций)
- сохраняем изменения
- в ближайшую минуту новые настройки попадут на сервер


#### Где посмотреть логи и результаты работы
- заходим на сервер по ssh
- `cd /var/log/trader/`
- находим нужный лог или файл с результатами (соответствует имени нашего бота в настройках, например `trader-1-log.txt`)


#### Как работать с не-USDT тикерами
- идём в [файл настроек](https://github.com/esemi/backtester/blob/trader1/etc/env) нашего бота
- устанавливаем тикер `symbol="BARBTC"`
- устанавливаем курс с криптодоллару `symbol_to_usdt_rate="27912.79"`
- сохраняем изменения
- теперь результаты торгов будут автоматически переводиться в USDT по указанному курсу


#### Как переключить трейдера на ByBit биржу
- идём в [файл настроек](https://github.com/esemi/backtester/blob/trader1/etc/env) нашего бота
- устанавливаем тикер `exchange="bybit"`
- сохраняем изменения


### Как добавить нового бота на сервер
- заходим на сервер по ssh из под пользователя root и заводим нового пользователя
- `adduser trader100500`
- `usermod -a -G supervisor trader100500`
- запоминаем пароль нового пользователя (можно взять стандартный пароль для всех ботов, если не слишком беспокоимся за безопасность)
- добавляем автозапуск бота на сервере (просто копируем секцию и меняем порядковый номер в имени бота, секция будет называться примерно `[program:trader100500]`)
- `vi /etc/supervisor/conf.d/traders.conf`
- переключаемся на работу с git репозиторием (в соседнем терминале или прямо на github.com)
- `git checkout master`
- `git checkout -b trader100500`
- `git push -u origin trader100500`
- меняем [настройки бота](https://github.com/esemi/backtester/blob/trader100500/etc/env) в новой ветке
- настраиваем [деплой нового бота на сервер](https://github.com/esemi/backtester/blob/trader100500/.github/workflows/deploy.yml) - заменяем `USER_NAME` на `trader100500`
- оставляем только те ключи и секреты, которые нужны этому инстансу бота (смотри строчки `*_api_key` и `*_api_secret`)
- [создаём PR для новой ветки](https://github.com/esemi/backtester/compare/master...trader100500)
- [ждём пока код бота зальётся на сервер](https://github.com/esemi/backtester/actions/workflows/deploy.yml)
- возвращаемся на сервер и перезапускаем supervisor
- `service supervisor restart`
- проверяем, что все боты стартовали корректно
- `supervisorctl status`


### Как добавить новую пару апи ключей
- добавляем новые доступы в [секреты github](https://github.com/esemi/backtester/settings/secrets/actions) с новыми именами
- прописываем использование созданных переменных в деплой соответствующего бота ([например](https://github.com/esemi/backtester/blob/trader40/.github/workflows/deploy.yml#L45))
