from _decimal import Decimal
from typing import Generator

from app.exchange_client.base import BaseClient
from app.models import Tick


class Dummy(BaseClient):
    def buy(self, quantity: Decimal, price: Decimal) -> dict | None:
        raise NotImplementedError

    def sell(self, quantity: Decimal, price: Decimal) -> dict | None:
        raise NotImplementedError

    def get_klines(self, interval: str, start_ms: int, limit: int) -> list[tuple[int, str]]:
        raise NotImplementedError

    def next_price(self) -> Generator[Tick | None, None, None]:
        raise NotImplementedError
