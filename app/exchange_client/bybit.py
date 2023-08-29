import logging
from decimal import Decimal
from typing import Generator

from pybit.unified_trading import HTTP  # type: ignore

from app.exchange_client.base import BaseClient, OrderResult
from app.models import Tick

logger = logging.getLogger(__name__)


class ByBit(BaseClient):
    def __init__(
        self,
        symbol: str,
        api_key: str = '',
        api_secret: str = '',
        test_mode: bool = False,
    ):
        super().__init__(symbol)

        self._exchange_session = HTTP(
            testnet=test_mode,
            api_key=api_key or None,
            api_secret=api_secret or None,
        )

    def next_price(self, start_tick_numeration: int = -1) -> Generator[Tick | None, None, None]:
        tick_number: int = start_tick_numeration
        while True:
            try:
                response = self._exchange_session.get_kline(
                    category='spot',
                    symbol=self._symbol,
                    interval='1',
                    limit=1,
                )
                tick_number += 1
                yield Tick(
                    number=tick_number,
                    price=Decimal(response.get('result')['list'][0][4]),
                )
            except Exception as e:
                logger.exception(e)
                yield None

    def buy(self, quantity: Decimal, price: Decimal) -> OrderResult | None:
        # todo impl
        # todo test
        pass

    def sell(self, quantity: Decimal, price: Decimal) -> OrderResult | None:
        # todo impl
        # todo test
        pass
