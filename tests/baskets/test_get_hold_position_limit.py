from decimal import Decimal

import pytest

from app.baskets import get_hold_position_limit
from app.settings import app_settings


def test_get_hold_position_limit_not_enabled():
    result = get_hold_position_limit(Decimal(1))

    assert result == app_settings.hold_position_limit


@pytest.mark.parametrize('payload, expected', [
    (Decimal(5), 1),
    (Decimal('5.001'), 2),
    (Decimal(10), 2),
    (Decimal('10.001'), 3),
])
def test_get_hold_position_limit(baskets_enabled, payload: Decimal, expected: Decimal):
    result = get_hold_position_limit(payload)

    assert result == expected
