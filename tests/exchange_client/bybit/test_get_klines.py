from datetime import datetime, timedelta
from decimal import Decimal

from app.exchange_client.bybit import ByBit


def test_get_klines_happy_path():
    client = ByBit(symbol='BTCUSDT', test_mode=True)
    start_ms = round((datetime.utcnow() - timedelta(days=1)).timestamp() * 1000)

    response = client.get_klines(
        interval='1m',
        start_ms=int(start_ms),
        limit=100,
    )

    assert len(response) == 100
    assert response[0].timestamp > 0
    assert response[0].price > Decimal(0)
