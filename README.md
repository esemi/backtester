# WIP


### Setup on windows
- [install python 3.11](https://www.python.org/downloads/windows/)
- [install git](https://gitforwindows.org/)


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
- идём в [файл настроек](https://github.com/esemi/backtester/tree/master/instances) нашего бота
- изменяем любые настройки (пример можно [посмотреть тут](https://github.com/esemi/backtester/blob/master/.env.example))
- сохраняем изменения
- в ближайшую минуту новые настройки попадут на сервер, остановят запущенного бота и запустят нового с указанными настройками.


#### Как включить реальную торговлю в боте
- идём в [файл настроек](https://github.com/esemi/backtester/tree/master/instances) нашего бота
- меняем или добавляем строчку `dry_run=false`
- сохраняем изменения
- в ближайшую минуту новые настройки попадут на сервер и перезапустят бота для реальных торгов


#### Как выключить бота
- идём в [файл настроек](https://github.com/esemi/backtester/tree/master/instances) нашего бота
- меняем или добавляем строчку `ticks_amount_limit=0`
- сохраняем изменения
- в ближайшую минуту новые настройки попадут на сервер и остановят работающего бота


#### Где посмотреть логи и результаты работы
- идём [на сервер](http://139.59.115.56/)
- находим нужный лог или файл с результатами (соответствует имени нашего бота в настройках)
- открываем и обновляем страницу в браузере (для появления новых значений)
