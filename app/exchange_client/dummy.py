from _decimal import Decimal
from typing import Generator

from app.exchange_client.base import BaseClient, OrderResult, HistoryPrice
from app.models import Tick


class Dummy(BaseClient):
    def buy(self, quantity: Decimal, price: Decimal) -> OrderResult | None:
        raise NotImplementedError

    def sell(self, quantity: Decimal, price: Decimal) -> OrderResult | None:
        raise NotImplementedError

    def get_klines(self, interval: str, start_ms: int, limit: int) -> list[HistoryPrice]:
        raise NotImplementedError

    def next_price(self, start_tick_numeration: int = -1) -> Generator[Tick | None, None, None]:
        raise NotImplementedError
