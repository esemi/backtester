"""Application settings."""
import os

from pydantic import Field
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    """Application settings class."""

    step: float = Field(default=0.02, description='шаг в абсолютных значениях для условия сделок')
    avg_rate_sell_limit: float = Field(default=1.05, description='шаг в процентах для условия сделок. 5% = 1.05')
    init_buy_amount: int = Field(default=3, description='сколько позиций открываем в самом начале теста')
    continue_buy_amount: float = Field(default=1.0, description='сколько монет в одной позиции')
    rates_filename: str = Field(
        default='BINANCE_SOLUSDT, 60.csv',
        description='имя файла с ценой монеты, от старой к новой',
    )


app_settings = AppSettings(
    _env_file=os.path.join(os.path.dirname(__file__), '..', '.env'),  # type:ignore
)
