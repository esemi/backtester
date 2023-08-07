from decimal import Decimal
from unittest.mock import Mock

from app.models import Tick, Position
from app.settings import app_settings
from app.strategy import Strategy


def test_init_buy(exchange_client_pass_mock):
    strategy = Strategy(exchange_client=exchange_client_pass_mock)

    response = strategy.tick(Tick(number=0, price=Decimal(10)))

    assert response is True
    assert len(strategy._open_positions) == 3
    assert not strategy._closed_positions


def test_skip_first_tick(exchange_client_pass_mock):
    strategy = Strategy(exchange_client=exchange_client_pass_mock)

    strategy.tick(Tick(number=0, price=Decimal(10)))
    response = strategy.tick(Tick(number=1, price=Decimal(9)))

    assert response is True
    assert len(strategy._open_positions) == 3
    assert not strategy._closed_positions


def test_break_by_tick_limit(exchange_client_pass_mock):
    strategy = Strategy(exchange_client=exchange_client_pass_mock)

    response = strategy.tick(Tick(number=app_settings.ticks_amount_limit, price=Decimal(9)))

    assert response is False


def test_break_by_global_stop_loss(exchange_client_pass_mock):
    strategy = Strategy(exchange_client=exchange_client_pass_mock)

    strategy.tick(Tick(number=0, price=Decimal(10)))
    response = strategy.tick(Tick(number=2, price=Decimal(app_settings.global_stop_loss)))

    assert response is False
    assert len(strategy._open_positions) == 0
    assert len(strategy._closed_positions) == 3


def test_buy_something(exchange_client_pass_mock):
    strategy = Strategy(exchange_client=exchange_client_pass_mock)

    strategy.tick(Tick(number=0, price=Decimal(10)))
    strategy.tick(Tick(number=1, price=Decimal(9)))
    response = strategy.tick(Tick(number=2, price=Decimal(8)))

    assert response is True
    assert len(strategy._open_positions) == 4


def test_sell_something(exchange_client_pass_mock):
    strategy = Strategy(exchange_client=exchange_client_pass_mock)
    buy_price = 10.0
    hold_price = 11.0
    minimal_sell_price = buy_price * app_settings.avg_rate_sell_limit
    strategy._open_positions.append(Position(amount=1, open_tick_number=0, open_rate=buy_price))
    strategy._open_positions.append(Position(amount=1, open_tick_number=0, open_rate=buy_price))
    strategy._open_positions.append(Position(amount=1, open_tick_number=0, open_rate=buy_price))
    strategy._open_positions.append(Position(amount=1, open_tick_number=2, open_rate=hold_price))

    response = strategy.tick(Tick(number=3, price=Decimal(minimal_sell_price)))

    assert response is True
    assert len(strategy._open_positions) == 1
    assert strategy._open_positions[0].open_rate == hold_price
    assert strategy._open_positions[0].open_tick_number == 2
    assert len(strategy._closed_positions) == 3
    for position in strategy._closed_positions:
        assert position.open_rate == buy_price
        assert position.open_tick_number == 0
        assert position.close_rate > 0.0
        assert position.close_tick_number == 3
