from decimal import Decimal

import pytest

from app.baskets import _get_basket_number


def test_get_basket_number_not_enabled():
    with pytest.raises(NotImplementedError):
        _get_basket_number(Decimal(1))


@pytest.mark.parametrize('payload, expected', [
    (Decimal(5), 0),
    (Decimal('5.001'), 1),
    (Decimal(10), 1),
    (Decimal('10.001'), 2),
])
def test_get_basket_number(baskets_enabled, payload: Decimal, expected: int):
    result = _get_basket_number(payload)

    assert result == expected
