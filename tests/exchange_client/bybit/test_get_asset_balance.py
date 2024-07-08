from app.exchange_client.bybit import ByBit
from app.settings import app_settings


def test_get_asset_balance_happy_path():
    client = ByBit(
        symbol='PLTUSDT',
        api_key=app_settings.bybit_api_key,
        api_secret=app_settings.bybit_api_secret,
    )

    response = client.get_asset_balance()

    assert isinstance(response, dict)
