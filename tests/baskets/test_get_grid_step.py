from decimal import Decimal

import pytest

from app.baskets import get_grid_step
from app.settings import app_settings


def test_get_grid_step_not_enabled():
    result = get_grid_step(Decimal(1))

    assert result == app_settings.grid_step


@pytest.mark.parametrize('payload, expected', [
    (Decimal(5), 1),
    (Decimal('5.001'), 2),
    (Decimal(10), 2),
    (Decimal('10.001'), 3),
])
def test_get_grid_step(baskets_enabled, payload: Decimal, expected: Decimal):
    result = get_grid_step(payload)

    assert result == expected
