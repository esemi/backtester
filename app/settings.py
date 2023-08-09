"""Application settings."""
import os

from pydantic import Field
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    """Application settings class."""

    # common settings
    debug: bool = Field(default=False)
    rates_path: str = os.path.join(os.path.dirname(__file__), '..', 'rates')

    # strategy settings
    step: float = Field(default=0.02, description='шаг в абсолютных значениях для условия на открытие новой позиции')
    avg_rate_sell_limit: float = Field(default=1.05, description='шаг в процентах для условия сделок. 5% = 1.05')
    init_buy_amount: int = Field(default=3, description='сколько позиций открываем в самом начале теста')
    continue_buy_amount: float = Field(default=1.0, description='сколько монет в одной позиции')
    global_stop_loss: float = Field(default=0.0, description='цена, при которой продаём всё и заканчиваем работу')
    ticks_amount_limit: int = Field(default=100500, description='максимальное количество тиков для торговой сессии')

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
