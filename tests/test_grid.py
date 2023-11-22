from decimal import Decimal

import pytest

from app.grid import get_grid_num_by_price


@pytest.mark.parametrize('payload, expected', [
    (Decimal('0'), 0),
    (Decimal('0.11'), 0),
    (Decimal('1.9999'), 1),
    (Decimal('100500'), 100500),
    (Decimal('-100500.0789'), -100501),
    (Decimal('-0.01'), -1),
])
def test_get_grid_num_by_price(payload: Decimal, expected: int):
    response = get_grid_num_by_price(payload)

    assert response == expected
