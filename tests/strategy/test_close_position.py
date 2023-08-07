from unittest.mock import Mock

from app.models import Position
from app.strategy import Strategy


def test_close_position_exception():
    mock = Mock()
    mock.sell = Mock(return_value=None)
    position = Position(
        amount=1.1,
        open_tick_number=0,
        open_rate=123.1
    )
    strategy = Strategy(exchange_client=mock)
    strategy._open_positions.append(position)

    response = strategy._close_position(position, price=123.1111, tick_number=1)

    assert response is False
    assert len(strategy._open_positions) == 1
    assert len(strategy._closed_positions) == 0


def test_close_position_expired():
    mock = Mock()
    mock.sell = Mock(return_value={
        'executedQty': '0',
        'cummulativeQuoteQty': '0',
        'status': 'EXPIRED',
    })
    position = Position(
        amount=1.1,
        open_tick_number=0,
        open_rate=123.1
    )
    strategy = Strategy(exchange_client=mock)
    strategy._open_positions.append(position)

    response = strategy._close_position(position, price=123.1, tick_number=1)

    assert response is False
    assert len(strategy._open_positions) == 1
    assert len(strategy._closed_positions) == 0


def test_open_position_filled(exchange_client_pass_mock):
    position = Position(
        amount=1.1,
        open_tick_number=0,
        open_rate=123.1
    )
    strategy = Strategy(exchange_client=exchange_client_pass_mock)
    strategy._open_positions.append(position)

    response = strategy._close_position(position, price=123.1, tick_number=999)

    assert response is True
    assert len(strategy._open_positions) == 0
    assert len(strategy._closed_positions) == 1
    assert strategy._closed_positions[0].amount == 1.1
    assert strategy._closed_positions[0].close_rate == 123.456 / 12.888
    assert strategy._closed_positions[0].close_tick_number == 999
