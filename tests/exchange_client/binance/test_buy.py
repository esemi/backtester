from decimal import Decimal

from app.exchange_client.binance import Binance
from app.settings import app_settings


def test_buy_happy_path():
    client = Binance(
        symbol='BTCUSDT',
        test_mode=True,
        api_key=app_settings.binance_api_key,
        api_secret=app_settings.binance_api_secret,
    )
    actual_price = next(client.next_price()).price + Decimal(1)

    response = client.buy(
        quantity=Decimal('0.00035'),  # ~$10
        price=actual_price,
    )

    assert response['status'] == 'FILLED'
    assert response['price'] == str(actual_price)
    assert response['price'] == str(actual_price)

    assert len(response) == 100
    assert response[0][0] > 0
    assert response[0][1]


def test_buy_canceled():
    client = Binance(
        symbol='BTCUSDT',
        test_mode=True,
        api_key=app_settings.binance_api_key,
        api_secret=app_settings.binance_api_secret,
    )
    actual_price = next(client.next_price())

    response = client.buy(
        quantity=Decimal('0.00035'),  # ~$10
        price=actual_price.price - Decimal(10),
    )

    assert len(response) == 100
    assert response[0][0] > 0
    assert response[0][1]
