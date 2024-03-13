"""Three baskets configuratuion."""
from decimal import Decimal

from app.settings import app_settings

_thresholds: list[Decimal] = []
_buy_amounts: list[Decimal] = []


def get_continue_buy_amount(tick_price: Decimal) -> Decimal:
    global _buy_amounts
    if not app_settings.baskets_enabled:
        return app_settings.continue_buy_amount

    if not _buy_amounts:
        _buy_amounts = [
            Decimal(value)
            for value in app_settings.baskets_buy_amount.split(';')
        ]

    basket_num = _get_basket_number(tick_price)
    return _buy_amounts[basket_num]


def _get_basket_number(tick_price: Decimal) -> int:
    global _thresholds
    if not app_settings.baskets_enabled:
        raise NotImplementedError

    if not _thresholds:
        _thresholds = [
            Decimal(value)
            for value in app_settings.baskets_thresholds.split(';')
        ]

    basket_num = 0
    for threshold in _thresholds:
        if tick_price <= threshold:
            break
        basket_num += 1
    return basket_num
