from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class Position:
    amount: Decimal
    open_tick_number: int
    open_rate: Decimal
    open_tick_datetime: datetime = datetime.utcnow()
    close_rate: Decimal = Decimal(0)
    close_tick_number: int = -1
    close_tick_datetime: datetime = datetime.utcnow()
    grid_number: str = '0_0'
    basket_number: int = 0

    @property
    def is_closed(self) -> bool:
        return self.close_tick_number >= 0


@dataclass
class OnHoldPositions:
    quantity: Decimal
    buy_amount: Decimal
    tick_number: int
    tick_rate: Decimal


@dataclass
class Tick:
    number: int
    bid: Decimal
    ask: Decimal
    bid_qty: Decimal = Decimal(0)
    ask_qty: Decimal = Decimal(0)
    actual_ticker_balance: Decimal = Decimal(0)

    @property
    def avg_price(self) -> Decimal:
        return (self.ask + self.bid) / Decimal(2)


@dataclass
class FloatingStep:
    percent: Decimal
    tries: int


@dataclass
class FloatingMatrix:
    matrix: list[FloatingStep]
