from decimal import Decimal

from app.exchange_client.bybit import ByBit
from app.settings import app_settings
from app.strategy import calculate_ticker_quantity


def test_get_order():
    client = ByBit(
        symbol='BTCUSDT',
        api_key=app_settings.bybit_api_key,
        api_secret=app_settings.bybit_api_secret,
        test_mode=True,
    )
    actual_price = next(client.next_price())
    quantity = calculate_ticker_quantity(
        app_settings.continue_buy_amount,
        actual_price.ask,
        Decimal('0.00001'),
    )
    buy_order = client.buy(
        quantity=quantity,
        price=actual_price.ask - Decimal(10),
        is_gtc=True,
    )

    response = client.get_order(buy_order.order_id)

    assert not response.is_filled
    assert response.order_id == buy_order.order_id
    assert response.qty_left > 0
