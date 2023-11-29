from decimal import Decimal

from app.exchange_client.binance import Binance
from app.settings import app_settings
from app.strategy import calculate_ticker_quantity


def test_sell_happy_path():
    client = Binance(
        symbol='BTCUSDT',
        test_mode=True,
        api_key=app_settings.binance_api_key,
        api_secret=app_settings.binance_api_secret,
    )
    actual_price = next(client.next_price()).bid - Decimal(10)
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
    assert response.fee == Decimal(0)


def test_sell_canceled():
    client = Binance(
        symbol='BTCUSDT',
        test_mode=True,
        api_key=app_settings.binance_api_key,
        api_secret=app_settings.binance_api_secret,
    )
    actual_price = next(client.next_price())
    quantity = calculate_ticker_quantity(
        app_settings.continue_buy_amount,
        actual_price.bid,
        Decimal('0.00001'),
    )

    response = client.sell(
        quantity=quantity,
        price=actual_price.bid + Decimal(10),
    )

    assert not response.is_filled
    assert response.qty == Decimal(0)
    assert response.price == Decimal(0)
