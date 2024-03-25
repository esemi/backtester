from decimal import Decimal

import pytest

from app.grid import get_grid_num_by_price


@pytest.mark.parametrize('payload, expected', [
    (Decimal('0'), '0_0'),
    (Decimal('0.11'), '0_0'),
    (Decimal('1.9999'), '0_1'),
    (Decimal('100500'), '0_100500'),
    (Decimal('-100500.0789'), '0_-100501'),
    (Decimal('-0.01'), '0_-1'),
])
def test_get_grid_num_by_price(payload: Decimal, expected: str):
    response = get_grid_num_by_price(payload)

    assert response == expected


@pytest.mark.parametrize('payload, expected', [
    (Decimal('0'), '0_0'),
    (Decimal('0.11'), '0_0'),
    (Decimal('1.9999'), '0_1'),
    (Decimal('5.001'), '1_2'),
    (Decimal('100500'), '2_33500'),
    (Decimal('-100500.0789'), '0_-100501'),
    (Decimal('-0.01'), '0_-1'),
])
def test_get_grid_num_by_price_baskets(baskets_enabled, payload: Decimal, expected: int):
    response = get_grid_num_by_price(payload)

    assert response == expected
