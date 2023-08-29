from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import Generator

from app.models import Tick


@dataclass
class OrderResult:
    is_filled: bool
    qty: Decimal
    price: Decimal
    raw_response: dict | None = None


class BaseClient(ABC):

    def __init__(self, symbol: str):
        self._symbol = symbol

    @abstractmethod
    def next_price(self) -> Generator[Tick | None, None, None]:
        yield None

    @abstractmethod
    def buy(self, quantity: Decimal, price: Decimal) -> OrderResult | None:
        pass

    @abstractmethod
    def sell(self, quantity: Decimal, price: Decimal) -> OrderResult | None:
        pass
