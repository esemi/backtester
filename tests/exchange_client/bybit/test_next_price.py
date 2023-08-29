from app.exchange_client.bybit import ByBit


def test_next_price_happy_path():
    client = ByBit(symbol='BTCUSDT', test_mode=True)
    response = next(client.next_price())

    assert response.number == 0
    assert response.price > 0.0
