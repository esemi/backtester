from decimal import Decimal
from unittest.mock import Mock

from app.models import Position, Tick
from app.strategy import BasicStrategy


def test_get_invest_body_happy_path(baskets_disabled):
    strategy = BasicStrategy(exchange_client=Mock())

    response = strategy._get_invest_body()

    assert response == Decimal(15 * 99)


def test_get_invest_body_open_positions(baskets_disabled):
    last_tick = Tick(
        number=0,
        bid=Decimal('120.9'),
        ask=Decimal(100500),
    )
    strategy = BasicStrategy(exchange_client=Mock())
    strategy._push_ticks_history(last_tick)
    strategy._open_positions.append(
        Position(
            amount=Decimal('1.1'),
            open_tick_number=0,
            open_rate=Decimal('123.1')
        )
    )

    response = strategy._get_invest_body()

    expected_response = Decimal(15 * 99) - Decimal('1.1') * Decimal('123.1') + Decimal('1.1') * Decimal('120.9')
    assert response == expected_response


def test_get_invest_body_baskets_simple(baskets_enabled):
    strategy = BasicStrategy(exchange_client=Mock())

    response = strategy._get_invest_body()

    assert response == Decimal(10 * 1 + 9.5 * 2 + 5 * 3)


def test_get_invest_body_baskets_and_positions(baskets_enabled):
    last_tick = Tick(
        number=0,
        bid=Decimal('120.9'),
        ask=Decimal(100500),
    )
    strategy = BasicStrategy(exchange_client=Mock())
    strategy._push_ticks_history(last_tick)
    strategy._open_positions.append(
        Position(
            amount=Decimal('1.1'),
            open_tick_number=0,
            open_rate=Decimal('123.1')
        )
    )

    response = strategy._get_invest_body()

    expected_response = Decimal(10 * 1 + 9.5 * 2 + 5 * 3) - Decimal('1.1') * Decimal('123.1') + Decimal('1.1') * Decimal('120.9')
    assert response == expected_response
