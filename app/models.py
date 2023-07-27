from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Position:
    amount: float
    open_tick_number: int
    open_rate: float
    close_rate: float = 0.0
    close_tick_number: int = -1


@dataclass
class OnHoldPositions:
    quantity: float
    buy_amount: float
    tick_number: int
    tick_rate: float


@dataclass
class Tick:
    number: int
    price: Decimal
