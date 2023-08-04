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
        self._client_spot = Spot(api_key=api_key or None, api_secret=api_secret or None)

    def next_price(self) -> Generator[Tick | None, None, None]:
        tick_number: int = -1
        while True:
            try:
                response = self._client_spot.ticker_price(
                    symbol=self._symbol,
                )
                tick_number += 1
                yield Tick(number=tick_number, price=Decimal(response.get('price')))
            except Exception as e:
                logger.exception(e)
                yield None

    def get_klines(self, interval: str, start_ms: int, limit: int) -> list[tuple[int, str]]:
        response = self._client_spot.klines(
            symbol=self._symbol,
            interval=interval,
            startTime=start_ms,
            limit=limit,
        )
        return [
            (
                line[0],  # Kline open time
                line[1],  # open rate
            )
            for line in response
        ]
