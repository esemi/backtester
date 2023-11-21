from decimal import Decimal

from app.models import Tick, Position
from app.settings import app_settings
from app.strategy import BasicStrategy


def test_init_buy(exchange_client_pass_mock):
    strategy = BasicStrategy(exchange_client=exchange_client_pass_mock)

    response = strategy.tick(Tick(number=0, bid=Decimal(9), ask=Decimal(11), bid_qty=Decimal(100500), ask_qty=Decimal(100500)))

    assert response is True
    assert len(strategy._open_positions) == 1
    assert not strategy._closed_positions


def test_break_by_enable_flag(exchange_client_pass_mock, strategy_disabled):
    strategy = BasicStrategy(exchange_client=exchange_client_pass_mock)

    response = strategy.tick(Tick(number=0, bid=Decimal(8), ask=Decimal(10), bid_qty=Decimal(100500), ask_qty=Decimal(100500)))

    assert response is False


def test_buy_something(exchange_client_pass_mock):
    strategy = BasicStrategy(exchange_client=exchange_client_pass_mock)

    strategy.tick(Tick(number=0, bid=Decimal(10), ask=Decimal(11), bid_qty=Decimal(100500), ask_qty=Decimal(100500)))
    response = strategy.tick(Tick(number=1, bid=Decimal(10), ask=Decimal(10), bid_qty=Decimal(100500), ask_qty=Decimal(100500)))

    assert response is True
    assert len(strategy._open_positions) == 2


def test_buy_something_decline_by_duplicate(exchange_client_pass_mock):
    strategy = BasicStrategy(exchange_client=exchange_client_pass_mock)

    strategy.tick(Tick(number=0, bid=Decimal(10), ask=Decimal('35.4050279'), bid_qty=Decimal(100500), ask_qty=Decimal(100500)))
    response = strategy.tick(Tick(number=1, bid=Decimal(10), ask=Decimal('35.4050279'), bid_qty=Decimal(100501), ask_qty=Decimal(100501)))

    assert response is True
    assert len(strategy._open_positions) == 1


def test_buy_something_decline_by_qty(exchange_client_pass_mock):
    strategy = BasicStrategy(exchange_client=exchange_client_pass_mock)

    strategy.tick(Tick(number=0, bid=Decimal(10), ask=Decimal(11), bid_qty=Decimal(100500), ask_qty=Decimal(100500)))
    response = strategy.tick(Tick(number=1, bid=Decimal(10), ask=Decimal(12), bid_qty=Decimal(100500), ask_qty=Decimal('0.9')))

    assert response is True
    assert len(strategy._open_positions) == 1


def test_sell_something(exchange_client_pass_mock):
    strategy = BasicStrategy(exchange_client=exchange_client_pass_mock)
    buy_price = Decimal('10.0')
    hold_price = Decimal('11.0')
    minimal_sell_price = buy_price + buy_price * app_settings.avg_rate_sell_limit / Decimal(100)
    strategy._open_positions.append(Position(amount=Decimal(1), open_tick_number=0, open_rate=buy_price))
    strategy._open_positions.append(Position(amount=Decimal(1), open_tick_number=0, open_rate=buy_price))
    strategy._open_positions.append(Position(amount=Decimal(1), open_tick_number=0, open_rate=buy_price))
    strategy._open_positions.append(Position(amount=Decimal(1), open_tick_number=2, open_rate=hold_price))
    strategy._push_ticks_history(Tick(1, bid=Decimal(1), ask=buy_price, bid_qty=Decimal(100500), ask_qty=Decimal(100500)))
    strategy._push_ticks_history(Tick(2, bid=Decimal(1), ask=hold_price, bid_qty=Decimal(100500), ask_qty=Decimal(100500)))

    response = strategy.tick(Tick(number=3, bid=Decimal(minimal_sell_price), ask=Decimal(100500), bid_qty=Decimal(100500), ask_qty=Decimal(100500)))

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


def test_sell_something_decline_by_ask_qty(exchange_client_pass_mock):
    strategy = BasicStrategy(exchange_client=exchange_client_pass_mock)
    buy_price = Decimal('10.0')
    minimal_sell_price = buy_price + buy_price * app_settings.avg_rate_sell_limit / Decimal(100)
    strategy._open_positions.append(Position(amount=Decimal(1), open_tick_number=0, open_rate=buy_price))
    strategy._open_positions.append(Position(amount=Decimal(1), open_tick_number=0, open_rate=buy_price))
    strategy._push_ticks_history(Tick(0, bid=Decimal(1), ask=buy_price, bid_qty=Decimal(100500), ask_qty=Decimal(100500)))
    strategy._push_ticks_history(Tick(0, bid=Decimal(1), ask=buy_price, bid_qty=Decimal(100500), ask_qty=Decimal(100500)))

    response = strategy.tick(Tick(number=2, bid=Decimal(minimal_sell_price), ask=Decimal(100500), bid_qty=Decimal('1.9'), ask_qty=Decimal(100500)))

    assert response is True
    assert len(strategy._open_positions) == 1
    assert len(strategy._closed_positions) == 1
