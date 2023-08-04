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