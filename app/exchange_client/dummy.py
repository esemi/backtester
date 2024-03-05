from typing import Generator

from _decimal import Decimal

from app.exchange_client.base import BaseClient, HistoryPrice, OrderResult
from app.models import Tick


class Dummy(BaseClient):
    def sell_market(self, quantity: Decimal) -> dict | None:
        raise NotImplementedError

    def buy(self, quantity: Decimal, price: Decimal) -> OrderResult | None:
        raise NotImplementedError

    def sell(self, quantity: Decimal, price: Decimal, is_gtc: bool = False) -> OrderResult | None:
        raise NotImplementedError

    def get_klines(self, interval: str, start_ms: int, limit: int) -> list[HistoryPrice]:
        raise NotImplementedError

    def next_price(self, start_tick_numeration: int = -1) -> Generator[Tick | None, None, None]:
        raise NotImplementedError

    def get_asset_balance(self) -> Decimal:
        return Decimal(0)

    def get_order(self, order_id: str | int) -> OrderResult | None:
        raise NotImplementedError

    def cancel_order(self, order_id: str | int) -> dict | None:
        raise NotImplementedError
