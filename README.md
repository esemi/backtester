# WIP


### Setup on windows
- [install python 3.11](https://www.python.org/downloads/windows/)
- [install git](https://gitforwindows.org/)


### Download code
```bash
git clone https://github.com/esemi/backtester.git
cd backtester
pip install -U pip poetry setuptools
poetry install
```

Create env file to override default config
```bash
cat > .env << EOF
EOF
```

### Run backtesting tool
```bash
python -m app.backtester
```