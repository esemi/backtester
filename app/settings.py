"""Application settings."""
import os
from decimal import getcontext, Decimal
from typing import Literal

from pydantic import Field, RedisDsn
from pydantic_settings import BaseSettings

getcontext().prec = 20


class AppSettings(BaseSettings):
    """Application settings class."""

    # common settings
    debug: bool = Field(default=False)
    rates_path: str = os.path.join(os.path.dirname(__file__), '..', 'rates')
    redis_dsn: RedisDsn = Field(default='redis://localhost/4')
    float_steps_path: str = os.path.join(os.path.dirname(__file__), '..', 'etc', 'float_strategy.csv')

    # strategy settings
    strategy_type: Literal['basic', 'floating'] = 'basic'
    step: Decimal = Field(default='0.02', description='шаг в абсолютных значениях для условия на открытие новой позиции')
    fee_percent: Decimal = Field(default='0.1', description='Процент комиссий от суммы сделки')
    avg_rate_sell_limit: Decimal = Field(default='1.05', description='шаг в процентах для условия сделок. 5% = 1.05')
    init_buy_amount: int = Field(default=3, description='сколько позиций открываем в самом начале теста')
    continue_buy_amount: Decimal = Field(
        default='15.0',
        description='Количество денег, на которое открываем новые позиции. Для SOLUSDT измеряется в USDT, для SOLBTC - в BTC.',
    )
    ticker_amount_digits: Decimal = Field(
        default='0.01',
        description='До скольки знаков после запятой округлять количество монет в заявке на покупку. Значение можно узнать тут https://www.binance.com/en/trade-rule',
    )
    global_stop_loss: Decimal = Field(default='0.0', description='цена, при которой продаём всё и заканчиваем работу')
    ticks_amount_limit: int = Field(default=100500, description='максимальное количество тиков для торговой сессии')
    symbol_to_usdt_rate: Decimal = Field(default='1', description='Курс текущего тикера в USDT.')
    hold_position_limit: int = Field(default=0, description='Максимальное количество открытых позиций.')

    # backtester settings
    rates_filename: str = Field(
        default='BINANCE_SOLUSDT, 60.csv',
        description='имя файла с ценой монеты, от старой к новой',
    )

    # trader settings
    throttling_failure_time: int = 10
    throttling_time: int = Field(default=5, description='Минимальная частота тика в секундах')
    show_stats_every_ticks: int = Field(default=1, description='Раз в сколько тиков выводить статистику')
    failure_limit: int = 15
    symbol: str = 'SOLUSDT'
    binance_api_key: str = ''
    binance_api_secret: str = ''
    dry_run: bool = Field(default=True)
    exchange_test_mode: bool = Field(default=False)


app_settings = AppSettings(
    _env_file=os.path.join(os.path.dirname(__file__), '..', '.env'),  # type:ignore
)
