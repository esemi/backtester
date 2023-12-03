from decimal import Decimal

from app.models import Tick
from app.storage import save_stats, get_saved_stats
from app.strategy import BasicStrategy


def test_save_stats_happy_path(exchange_client_pass_mock):
    strategy = BasicStrategy(exchange_client=exchange_client_pass_mock)
    strategy.tick(Tick(number=0, bid=Decimal(9), ask=Decimal(11), bid_qty=Decimal(100500), ask_qty=Decimal(100500)))
    stats = strategy.get_results()

    save_stats('test:key', stats)

    saved_stats = get_saved_stats('test:key')
    assert saved_stats
    assert set(stats.keys()) == {key.decode('utf-8') for key in saved_stats.keys()}
