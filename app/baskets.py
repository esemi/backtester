"""Three baskets configuratuion."""
from decimal import Decimal

from app.settings import app_settings

_thresholds: list[Decimal] = []
_buy_amounts: list[Decimal] = []
_hold_limits: list[int] = []
_grid_steps: list[Decimal] = []


def get_continue_buy_amount(tick_price: Decimal) -> Decimal:
    global _buy_amounts
    if not app_settings.baskets_enabled:
        return app_settings.continue_buy_amount

    if not _buy_amounts:
        _buy_amounts = [
            Decimal(value)
            for value in app_settings.baskets_buy_amount.split(';')
        ]

    basket_num = get_basket_number(tick_price)
    return _buy_amounts[basket_num]


def get_grid_step(tick_price: Decimal) -> Decimal:
    global _grid_steps
    if not app_settings.baskets_enabled:
        return app_settings.grid_step

    if not _grid_steps:
        _grid_steps = [
            Decimal(value)
            for value in app_settings.baskets_grid_step.split(';')
        ]

    basket_num = get_basket_number(tick_price)
    return _grid_steps[basket_num]


def get_hold_position_limit(tick_price: Decimal) -> int:
    global _hold_limits
    if not app_settings.baskets_enabled:
        return app_settings.hold_position_limit

    if not _hold_limits:
        _hold_limits = [
            int(value)
            for value in app_settings.baskets_hold_position_limit.split(';')
        ]

    basket_num = get_basket_number(tick_price)
    return _hold_limits[basket_num]


def get_basket_number(tick_price: Decimal) -> int:
    global _thresholds
    if not app_settings.baskets_enabled:
        return 0

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
