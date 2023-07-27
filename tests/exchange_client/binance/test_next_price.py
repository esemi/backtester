from app.exchange_client.binance import Binance


def test_next_price_happy_path():
    client = Binance(symbol='BTCUSDT')
    response = next(client.next_price())

    assert response.number == 0
    assert response.price > 0.0
