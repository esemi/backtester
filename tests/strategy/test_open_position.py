from unittest.mock import Mock

from app.strategy import Strategy


def test_open_position_exception():
    mock = Mock()
    mock.buy = Mock(return_value=None)

    strategy = Strategy(exchange_client=mock)

    response = strategy._open_position(quantity=1.1, price=123.1, tick_number=0)

    assert response is False
    assert len(strategy._open_positions) == 0


def test_open_position_expired():
    mock = Mock()
    mock.buy = Mock(return_value={
        'executedQty': '0',
        'cummulativeQuoteQty': '0',
        'status': 'EXPIRED',
    })

    strategy = Strategy(exchange_client=mock)

    response = strategy._open_position(quantity=1.1, price=123.1, tick_number=0)

    assert response is False
    assert len(strategy._open_positions) == 0


def test_open_position_filled(exchange_client_pass_mock):
    strategy = Strategy(exchange_client=exchange_client_pass_mock)

    response = strategy._open_position(quantity=1.1, price=123.1, tick_number=0)

    assert response is True
    assert len(strategy._open_positions) == 1
    assert strategy._open_positions[0].amount == 12.888
    assert strategy._open_positions[0].open_rate == 456.3 / 12.888
    assert strategy._open_positions[0].open_tick_number == 0
