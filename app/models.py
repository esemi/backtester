from dataclasses import dataclass


@dataclass
class Position:
    amount: float
    open_tick_number: int
    open_rate: float
    close_rate: float = 0.0
    close_tick_number: int = -1


@dataclass
class OnHoldPositions:
    amount: float
    tick_number: int
    rate: float
