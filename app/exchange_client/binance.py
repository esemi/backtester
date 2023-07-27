import logging
from decimal import Decimal
from typing import Generator

from binance.spot import Spot  # type: ignore

from app.exchange_client.base import BaseClient
from app.models import Tick

logger = logging.getLogger(__name__)


class Binance(BaseClient):
    def __init__(self, symbol: str, api_key: str = '', api_secret: str = ''):
        super().__init__(symbol)
        self._client = Spot(api_key=api_key or None, api_secret=api_secret or None)

    def next_price(self) -> Generator[Tick | None, None, None]:
        tick_number: int = -1
        while True:
            tick_number += 1
            try:
                response = self._client.ticker_price(
                    symbol=self._symbol,
                )
                yield Tick(number=tick_number, price=Decimal(response.get('price')))
            except Exception as e:
                logger.exception(e)
                yield None

