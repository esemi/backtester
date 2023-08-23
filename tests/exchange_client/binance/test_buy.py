from decimal import Decimal

from app.exchange_client.binance import Binance
from app.settings import app_settings
from app.strategy import calculate_ticker_quantity


def test_buy_happy_path():
    client = Binance(
        symbol='BTCUSDT',
        test_mode=True,
        api_key=app_settings.binance_api_key,
        api_secret=app_settings.binance_api_secret,
    )
    actual_price = next(client.next_price()).price + Decimal(1)
    quantity = calculate_ticker_quantity(
        app_settings.continue_buy_amount,
        actual_price,
        Decimal('0.00001'),
    )

    response = client.buy(
        quantity=quantity,
        price=actual_price,
    )

    assert response['status'] == 'FILLED'
    assert Decimal(response['cummulativeQuoteQty']) <= actual_price
    assert Decimal(response['executedQty']) == quantity


def test_buy_canceled():
    client = Binance(
        symbol='BTCUSDT',
        test_mode=True,
        api_key=app_settings.binance_api_key,
        api_secret=app_settings.binance_api_secret,
    )
    actual_price = next(client.next_price())
    quantity = calculate_ticker_quantity(
        app_settings.continue_buy_amount,
        actual_price.price,
        Decimal('0.00001'),
    )

    response = client.buy(
        quantity=quantity,
        price=actual_price.price - Decimal(10),
    )

    assert response['status'] == 'EXPIRED'
    assert Decimal(response['executedQty']) == Decimal(0)
    assert Decimal(response['cummulativeQuoteQty']) == Decimal(0)
