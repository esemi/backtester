from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Generator

from app.models import Tick


class BaseClient(ABC):

    def __init__(self, symbol: str):
        self._symbol = symbol

    @abstractmethod
    def next_price(self) -> Generator[Tick | None, None, None]:
        yield None

    @abstractmethod
    def get_klines(self, interval: str, start_ms: int, limit: int) -> list[tuple[int, str]]:
        pass

    @abstractmethod
    def buy(self, quantity: Decimal, price: Decimal) -> dict | None:
        pass

    @abstractmethod
    def sell(self, quantity: Decimal, price: Decimal) -> dict | None:
        pass
