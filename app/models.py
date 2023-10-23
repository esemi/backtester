from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Position:
    amount: Decimal
    open_tick_number: int
    open_rate: Decimal
    close_rate: Decimal = Decimal(0)
    close_tick_number: int = -1


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
    bid_qty: Decimal = 0
    ask_qty: Decimal = 0

    @property
    def avg_price(self) -> Decimal:
        return (self.ask + self.bid) / Decimal(2)
