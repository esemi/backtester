import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Generator

from app.models import Fee, Tick


@dataclass
class OrderResult:
    is_filled: bool
    qty: Decimal
    price: Decimal
    fee: Decimal
    raw_fees: list[Fee] = field(default_factory=list)
    order_id: str | int = ''
    qty_left: Decimal = Decimal(0)
    raw_response: dict | None = None


@dataclass
class HistoryPrice:
    price: Decimal
    timestamp: int


class BaseClient(ABC):

    def __init__(self, symbol: str, cache_time: int = 60):
        self.symbol: str = symbol
        self._cache_time: int = cache_time
        self._last_asset_amount: Decimal = Decimal(0)
        self._last_asset_amount_ttl: int = 0

    @abstractmethod
    def next_price(self, start_tick_numeration: int = -1) -> Generator[Tick | None, None, None]:
        yield None

    @abstractmethod
    def get_klines(self, interval: str, start_ms: int, limit: int) -> list[HistoryPrice]:
        raise NotImplementedError

    @abstractmethod
    def buy(self, quantity: Decimal, price: Decimal) -> OrderResult | None:
        pass

    @abstractmethod
    def sell(self, quantity: Decimal, price: Decimal, is_gtc: bool = False) -> OrderResult | None:
        pass

    def get_asset_balance_cached(self) -> Decimal:
        if self._last_asset_amount_ttl <= time.time():
            self._last_asset_amount = self.get_asset_balance()
            self._last_asset_amount_ttl = int(time.time()) + self._cache_time

        return self._last_asset_amount

    @abstractmethod
    def get_asset_balance(self) -> Decimal:
        pass

    @abstractmethod
    def sell_market(self, quantity: Decimal) -> dict | None:
        pass

    @abstractmethod
    def get_order(self, order_id: str | int) -> OrderResult | None:
        pass

    @abstractmethod
    def cancel_order(self, order_id: str | int) -> dict | None:
        pass
