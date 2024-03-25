import math
from decimal import Decimal

from app import baskets


def get_grid_num_by_price(price: Decimal) -> str:
    grid_step = baskets.get_grid_step(price)
    basket_number = baskets.get_basket_number(price)
    result = '{0}_{1}'.format(
        basket_number,
        math.floor(price / grid_step),
    )

    return result
