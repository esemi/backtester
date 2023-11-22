import math
from decimal import Decimal

from app.settings import app_settings


def get_grid_num_by_price(price: Decimal) -> int:
    return math.floor(price / app_settings.grid_step)
