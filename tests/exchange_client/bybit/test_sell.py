from decimal import Decimal

from app.exchange_client.bybit import ByBit
from app.settings import app_settings
from app.strategy import calculate_ticker_quantity


def test_sell_happy_path():
    client = ByBit(
        symbol='BTCUSDT',
        api_key=app_settings.bybit_api_key,
        api_secret=app_settings.bybit_api_secret,
        test_mode=True,
    )
    actual_price = next(client.next_price()).price - Decimal(200)
    quantity = calculate_ticker_quantity(
        app_settings.continue_buy_amount,
        actual_price,
        Decimal('0.00001'),
    )

    response = client.sell(
        quantity=quantity,
        price=actual_price,
    )

    assert response.is_filled
    assert response.price >= actual_price
    assert response.qty == quantity


def test_sell_canceled():
    client = ByBit(
        symbol='BTCUSDT',
        api_key=app_settings.bybit_api_key,
        api_secret=app_settings.bybit_api_secret,
        test_mode=True,
    )
    actual_price = next(client.next_price())
    quantity = calculate_ticker_quantity(
        app_settings.continue_buy_amount,
        actual_price.price,
        Decimal('0.00001'),
    )

    response = client.sell(
        quantity=quantity,
        price=actual_price.price + Decimal(20),
    )

    assert not response.is_filled
    assert response.qty == Decimal(0)
    assert response.price == Decimal(0)
