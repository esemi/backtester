from decimal import Decimal

from app.exchange_client.binance import Binance
from app.settings import app_settings


def test_sell_happy_path():
    client = Binance(
        symbol='BTCUSDT',
        test_mode=True,
        api_key=app_settings.binance_api_key,
        api_secret=app_settings.binance_api_secret,
    )
    actual_price = next(client.next_price()).price - Decimal(10)
    qty = Decimal('0.00035')  # ~$10

    response = client.sell(
        quantity=qty,
        price=actual_price,
    )

    assert response['status'] == 'FILLED'
    assert Decimal(response['cummulativeQuoteQty']) <= actual_price
    assert Decimal(response['executedQty']) == qty


def test_sell_canceled():
    client = Binance(
        symbol='BTCUSDT',
        test_mode=True,
        api_key=app_settings.binance_api_key,
        api_secret=app_settings.binance_api_secret,
    )
    actual_price = next(client.next_price())

    response = client.sell(
        quantity=Decimal('0.00035'),  # ~$10
        price=actual_price.price + Decimal(10),
    )

    assert response['status'] == 'EXPIRED'
    assert Decimal(response['executedQty']) == Decimal(0)
    assert Decimal(response['cummulativeQuoteQty']) == Decimal(0)
