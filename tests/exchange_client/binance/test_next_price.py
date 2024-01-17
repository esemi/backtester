from app.exchange_client.binance import Binance
from app.settings import app_settings


def test_next_price_happy_path():
    client = Binance(
        symbol='BTCUSDT',
        test_mode=True,
        api_key=app_settings.binance_api_key,
        api_secret=app_settings.binance_api_secret,
    )
    response = next(client.next_price())

    assert response.number == 0
    assert response.ask > 0.0
    assert response.ask_qty > 0.0
    assert response.bid > 0.0
    assert response.bid_qty > 0.0
    assert response.bid <= response.ask
    assert response.actual_ticker_balance > 0.0
