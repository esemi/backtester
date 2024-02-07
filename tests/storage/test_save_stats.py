from decimal import Decimal

from app.floating_steps import FloatingSteps
from app.models import Position, Tick
from app.settings import app_settings
from app.storage import get_saved_stats, save_stats
from app.strategy import BasicStrategy, FloatingStrategy


def test_save_stats_happy_path(exchange_client_pass_mock):
    strategy = BasicStrategy(exchange_client=exchange_client_pass_mock)
    strategy.tick(Tick(number=0, bid=Decimal(9), ask=Decimal(11), bid_qty=Decimal(100500), ask_qty=Decimal(100500)))
    stats = strategy.get_results()

    save_stats('test:key', stats)

    saved_stats = get_saved_stats('test:key')
    assert saved_stats
    assert set(stats.keys()).issubset(set(saved_stats.keys()))


def test_save_stats_floating_stats(exchange_client_pass_mock):
    strategy = FloatingStrategy(
        exchange_client=exchange_client_pass_mock,
        steps_instance=FloatingSteps(app_settings.float_steps_path),
    )
    strategy.tick(Tick(number=0, bid=Decimal(9), ask=Decimal(11), bid_qty=Decimal(100500), ask_qty=Decimal(100500)))
    stats = strategy.get_results()

    save_stats('test:key:floating', stats)

    saved_stats = get_saved_stats('test:key:floating')
    assert saved_stats
    assert set(stats.keys()).issubset(set(saved_stats.keys()))


def test_get_stats_average_open_position_rate(exchange_client_pass_mock):
    strategy = BasicStrategy(exchange_client=exchange_client_pass_mock)
    strategy._push_ticks_history(Tick(
        number=1,
        bid=Decimal('0.0079'),
        ask=Decimal('0.0081'),
        bid_qty=Decimal(100),
        ask_qty=Decimal(500),
    ))
    strategy._open_positions = [
        Position(
            amount=Decimal('4.5'),
            open_rate=Decimal('0.0078'),
            open_tick_number=1,
        ),
        Position(
            amount=Decimal('6.7'),
            open_rate=Decimal('0.0080'),
            open_tick_number=1,
        ),
    ]

    stats = strategy.get_results()

    assert stats['open_position_average_rate'] == Decimal('0.0079196428571428571429')
