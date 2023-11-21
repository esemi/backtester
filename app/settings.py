"""Application settings."""
import getpass
import os
from decimal import getcontext, Decimal
from typing import Literal

from pydantic import Field, RedisDsn
from pydantic_settings import BaseSettings

getcontext().prec = 20

APP_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        '..',
    ),
)


class AppSettings(BaseSettings, extra='ignore'):
    """Application settings class."""

    # common settings
    debug: bool = Field(default=False)

    instance_name: str = Field(default=getpass.getuser(), description='Unique instance name. Username by default.')
    rates_path: str = os.path.join(APP_PATH, 'rates')
    logs_path: str = Field(default='/var/www/kta/storage/trader')
    redis_dsn: RedisDsn = Field(default='redis://localhost/4')
    float_steps_path: str = os.path.join(APP_PATH, 'etc', 'float_strategy.csv')

    # strategy settings
    strategy_type: Literal['basic', 'floating'] = 'basic'
    step: Decimal = Field(default='0.5', description='шаг в процентах для условия на открытие новой позиции. 0.5 = 0.5%')
    fee_percent: Decimal = Field(default='0.1', description='Процент комиссий от суммы сделки')
    avg_rate_sell_limit: Decimal = Field(default='0.5', description='шаг в процентах для условия сделок. 0.5 = 0.5%')
    continue_buy_amount: Decimal = Field(
        default='15.0',
        description='Количество денег, на которое открываем новые позиции. Для SOLUSDT измеряется в USDT, для SOLBTC - в BTC.',
    )
    ticker_amount_digits: Decimal = Field(
        default='0.01',
        description='До скольки знаков после запятой округлять количество монет в заявке на покупку. Значение можно узнать тут https://www.binance.com/en/trade-rule',
    )
    ticker_price_digits: Decimal = Field(
        default='0.01',
        description='До скольки знаков после запятой округлять цену в заявке. Этот параметр также используется для округления цены при проверке на наличие открытой позиции в этом ценовом диапазоне.',
    )
    enabled: bool = Field(default=False, description='вкл/выкл стратегии')
    hold_position_limit: int = Field(default=0, description='Максимальное количество открытых позиций.')
    multiple_sell_on_tick: bool = Field(
        default=True,
        description='Разрешаем множественные продажи на одном тике или нет.',
    )
    use_last_open_position_rate: bool = True
    close_positions_only: bool = False

    # backtester settings
    rates_filename: str = Field(
        default='BINANCE_SOLUSDT, 60.csv',
        description='имя файла с ценой монеты, от старой к новой',
    )

    # trader settings
    exchange: Literal['binance', 'bybit'] = 'binance'
    throttling_failure_time: int = 100
    throttling_time: int = Field(default=5, description='Минимальная частота тика в секундах')
    throttling_time_small_tick: int = 3
    show_stats_every_ticks: int = Field(default=1, description='Раз в сколько тиков выводить статистику')
    failure_limit: int = 15
    symbol: str = 'SOLUSDT'
    binance_api_key: str = ''
    binance_api_secret: str = ''
    bybit_api_key: str = ''
    bybit_api_secret: str = ''
    dry_run: bool = Field(default=True)
    exchange_test_mode: bool = Field(default=False)


app_settings = AppSettings(
    _env_file=os.path.join(APP_PATH, '.env'),  # type:ignore
)
