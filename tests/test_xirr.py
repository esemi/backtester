from datetime import datetime, timedelta
from decimal import Decimal

from app.models import Position
from app.xirr import calculate_xirr


def test_calculate_xirr_empty():
    res = calculate_xirr([], Decimal(1))

    assert res == Decimal(0)


def test_calculate_xirr_open_positions_only():
    start_date = datetime.utcnow() - timedelta(days=365)
    positions = [
        Position(
            amount=Decimal('83.3'),
            open_rate=Decimal('1.2'),
            open_tick_number=1,
            open_tick_datetime=start_date,
        ),
    ]

    res = calculate_xirr(positions, Decimal('1.32'))

    assert res == Decimal(10)


def test_calculate_xirr_happy_path():
    positions = [
        Position(
            amount=Decimal('83.3'),
            open_rate=Decimal('1.2'),
            open_tick_number=1,
            open_tick_datetime=datetime.utcnow() - timedelta(days=365),
            close_rate=Decimal('1.32'),
            close_tick_number=2,
            close_tick_datetime=datetime.utcnow(),
        ),
        Position(
            amount=Decimal(1),
            open_rate=Decimal(6),
            open_tick_number=1,
            open_tick_datetime=datetime(2023, 1, 1),
            close_rate=Decimal(5),
            close_tick_number=2,
            close_tick_datetime=datetime(2023, 1, 2),
        ),
    ]
    res = calculate_xirr(positions, Decimal('100500'))

    assert res == Decimal('8.8950')


def test_calculate_xirr_too_short_period():
    positions = [
        Position(
            amount=Decimal(1),
            open_rate=Decimal('5.0'),
            open_tick_number=1,
            open_tick_datetime=datetime(2023, 1, 1, hour=0),
            close_rate=Decimal('5.001'),
            close_tick_number=2,
            close_tick_datetime=datetime(2023, 1, 1, hour=20),
        ),
    ]
    res = calculate_xirr(positions, Decimal('100500'))

    assert res == Decimal('0')

