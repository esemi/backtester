from datetime import datetime
from decimal import Decimal

from pyxirr import mirr, xirr

from app.models import Position


def calculate_xirr(positions: list[Position], actual_rate: Decimal) -> Decimal:
    if not positions:
        return Decimal(0)

    cash_flow: list[tuple[datetime, Decimal]] = []
    open_position_qty = sum(
        position.amount
        for position in positions
        if not position.is_closed
    )
    if open_position_qty:
        # fake sold by actual price
        cash_flow.append(
            (datetime.utcnow(), open_position_qty * actual_rate * Decimal(-1)),
        )

    for position in positions:
        cash_flow.append(
            (position.open_tick_datetime, position.amount * position.open_rate),
        )
        if position.is_closed:
            cash_flow.append(
                (position.close_tick_datetime, position.amount * position.close_rate * Decimal(-1)),
            )

    cash_flow.sort(key=lambda x: x[0])
    res = xirr(
        dates=[v[0] for v in cash_flow],
        amounts=[v[1] for v in cash_flow],
    )
    del cash_flow
    if res is None:
        return Decimal(0)

    return (Decimal(res) * Decimal(100)).quantize(Decimal('0.0001'))
