from dataclasses import dataclass


@dataclass
class Position:
    amount: int
    open_tick_number: int
    open_rate: float
    close_rate: float | None = None
    close_tick_number: int | None = None
