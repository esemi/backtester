from decimal import Decimal

from app.models import Position
from app.strategy import BasicStrategy


def test_close_all_positions_happy_path(exchange_client_pass_mock):
    position1 = Position(
        amount=Decimal('1.1'),
        open_tick_number=0,
        open_rate=Decimal('123.1')
    )
    position2 = Position(
        amount=Decimal('1.2'),
        open_tick_number=0,
        open_rate=Decimal('125.98')
    )
    strategy = BasicStrategy(exchange_client=exchange_client_pass_mock)
    strategy._open_positions.append(position1)
    strategy._open_positions.append(position2)

    response = strategy._close_all_positions(price=Decimal('123.1'), tick_number=999)

    assert response is True
    assert len(strategy._open_positions) == 0
    assert len(strategy._closed_positions) == 3
    assert strategy._closed_positions[0].amount == Decimal('1.1')
    assert strategy._closed_positions[0].close_rate == Decimal(0)
    assert strategy._closed_positions[0].close_tick_number == 999
    assert strategy._closed_positions[1].amount == Decimal('1.2')
    assert strategy._closed_positions[1].close_rate == Decimal(0)
    assert strategy._closed_positions[1].close_tick_number == 999
    assert strategy._closed_positions[2].amount == Decimal('2.3')
    assert strategy._closed_positions[2].close_rate == Decimal('9.5791433891')
    assert strategy._closed_positions[2].close_tick_number == 999


def test_close_all_positions_not_found_positions(exchange_client_pass_mock):
    strategy = BasicStrategy(exchange_client=exchange_client_pass_mock)

    response = strategy._close_all_positions(price=Decimal('123.1'), tick_number=999)

    assert response is True
    assert len(strategy._open_positions) == 0
    assert len(strategy._closed_positions) == 0
