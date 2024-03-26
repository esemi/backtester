from decimal import Decimal

import pytest

from app.baskets import get_floating_matrix


def test_get_floating_matrix_disabled():
    matrix = get_floating_matrix(Decimal(1))
    same_matrix = get_floating_matrix(Decimal(100500))

    assert matrix == same_matrix
    assert len(matrix.matrix) > 10


@pytest.mark.parametrize('payload, expected_percent, expected_tries', [
    (Decimal(5), Decimal('0.5'), 1),
    (Decimal('10.001'), Decimal('109'), 122),
])
def test_get_hold_position_limit(
    baskets_enabled,
    payload: Decimal,
    expected_percent: Decimal,
    expected_tries: int,
):
    matrix = get_floating_matrix(payload)

    assert matrix.matrix[0].percent == expected_percent
    assert matrix.matrix[0].tries == expected_tries
