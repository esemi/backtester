from app.exchange_client.binance import Binance


def test_next_price_happy_path():
    client = Binance(symbol='BTCUSDT', test_mode=True)
    response = next(client.next_price())

    assert response.number == 0
    assert response.ask > 0.0
    assert response.ask_qty > 0.0
    assert response.bid > 0.0
    assert response.bid_qty > 0.0
    assert response.bid <= response.ask
