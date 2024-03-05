from decimal import Decimal

from app.exchange_client.binance import Binance
from app.settings import app_settings
from app.strategy import calculate_ticker_quantity


def test_cancel_order_happy_path():
    client = Binance(
        symbol='BTCUSDT',
        test_mode=True,
        api_key=app_settings.binance_api_key,
        api_secret=app_settings.binance_api_secret,
    )
    actual_price = next(client.next_price())
    quantity = calculate_ticker_quantity(
        app_settings.continue_buy_amount,
        actual_price.ask,
        Decimal('0.00001'),
    )
    canceled_order = client.buy(
        quantity=quantity,
        price=actual_price.ask - Decimal(10),
        is_gtc=True,
    )

    response = client.cancel_order(
        order_id=canceled_order.order_id,
    )

    assert not canceled_order.is_filled
    assert response
