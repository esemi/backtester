from datetime import datetime, timedelta

from app.exchange_client.binance import Binance


def test_get_klines_happy_path():
    client = Binance(symbol='SOLUSDT')
    start_ms = round((datetime.utcnow() - timedelta(days=1)).timestamp() * 1000)

    response = client.get_klines(
        interval='1m',
        start_ms=int(start_ms),
        limit=100,
    )

    assert len(response) == 100
    assert response[0][0] > 0
    assert response[0][1]
