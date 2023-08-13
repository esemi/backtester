from unittest.mock import Mock

from app.models import Position
from app.strategy import BasicStrategy


def test_get_open_positions_for_sell_happy_path():
    strategy = BasicStrategy(exchange_client=Mock())
    strategy._open_positions.append(Position(amount=1, open_tick_number=0, open_rate=10))
    strategy._open_positions.append(Position(amount=1, open_tick_number=0, open_rate=9))
    strategy._open_positions.append(Position(amount=1, open_tick_number=0, open_rate=11))
    strategy._open_positions.append(Position(amount=1, open_tick_number=0, open_rate=8))

    response = strategy._get_open_positions_for_sell()

    assert id(response) != id(strategy._open_positions)
    assert response[0].open_rate == 8
    assert response[1].open_rate == 9
