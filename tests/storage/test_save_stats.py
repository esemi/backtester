from decimal import Decimal

from app.floating_steps import FloatingSteps
from app.models import Tick
from app.settings import app_settings
from app.storage import save_stats, get_saved_stats
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
