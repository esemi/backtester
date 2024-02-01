from decimal import Decimal

from app.exchange_client.binance import Binance
from app.settings import app_settings
from app.strategy import calculate_ticker_quantity


def test_sell_market_happy_path():
    client = Binance(
        symbol='BTCUSDT',
        test_mode=True,
        api_key=app_settings.binance_api_key,
        api_secret=app_settings.binance_api_secret,
    )
    actual_price = next(client.next_price()).ask + Decimal(5)
    quantity = calculate_ticker_quantity(
        app_settings.continue_buy_amount,
        actual_price,
        Decimal('0.00001'),
    )
    client.buy(quantity=quantity, price=actual_price)
    full_quantity = client.get_asset_balance()

    response = client.sell_market(quantity=full_quantity)

    assert isinstance(response, dict)
    assert response.get('status') == 'FILLED'
