from decimal import Decimal

import pytest

from app.baskets import get_continue_buy_amount
from app.settings import app_settings


def test_get_continue_buy_amount_not_enabled():
    result = get_continue_buy_amount(Decimal(1))

    assert result == app_settings.continue_buy_amount


@pytest.mark.parametrize('payload, expected', [
    (Decimal(5), Decimal(10)),
    (Decimal('5.001'), Decimal('9.5')),
    (Decimal(10), Decimal('9.5')),
    (Decimal('10.001'), Decimal(5)),
])
def test_get_continue_buy_amount(baskets_enabled, payload: Decimal, expected: Decimal):
    result = get_continue_buy_amount(payload)

    assert result == expected
