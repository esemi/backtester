Crypto Trader
---
Trading strategy backtesting utility and trading robot implementation for Binance and ByBit cryptocurrency exchanges


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
- идём [на сервер](http://139.59.115.56/)
- находим нужный лог или файл с результатами (соответствует имени нашего бота в настройках)
- открываем и обновляем страницу в браузере (для появления новых значений)


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

