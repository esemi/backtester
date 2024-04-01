"""Three baskets configuratuion."""
import json
from decimal import Decimal

from app.models import FloatingMatrix, FloatingStep
from app.settings import app_settings

_thresholds: list[Decimal] = []
_buy_amounts: list[Decimal] = []
_hold_limits: list[int] = []
_grid_steps: list[Decimal] = []
_floating_matrix: list[FloatingMatrix] = []


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


def get_total_deposit() -> Decimal:
    if not app_settings.baskets_enabled:
        return Decimal(app_settings.hold_position_limit * app_settings.continue_buy_amount)

    get_hold_position_limit(Decimal(0))
    get_continue_buy_amount(Decimal(0))

    summary = Decimal(0)
    for i in range(len(_buy_amounts)):
        summary += Decimal(_buy_amounts[i]) * Decimal(_hold_limits[i])
    return summary


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


def get_floating_matrix(tick_price: Decimal) -> FloatingMatrix:
    global _floating_matrix

    if not app_settings.baskets_enabled:
        with open(app_settings.float_steps_path, 'r') as fd:
            return FloatingMatrix(
                matrix=[
                    FloatingStep(
                        percent=Decimal(line.split(',')[0]),
                        tries=int(line.split(',')[1]),
                    )
                    for index, line in enumerate(fd.readlines())
                    if index and line
                ],
            )

    if not _floating_matrix:
        matrix_baskets = json.loads(app_settings.baskets_floating_matrix)
        for basket_index, raw_matrix in enumerate(matrix_baskets):
            parsed_matrix: list[FloatingStep] = [
                FloatingStep(
                    percent=Decimal(value[0]),
                    tries=int(value[1]),
                )
                for value in raw_matrix
            ]
            _floating_matrix.append(
                FloatingMatrix(matrix=parsed_matrix),
            )

    basket_num = get_basket_number(tick_price)
    return _floating_matrix[basket_num]


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

