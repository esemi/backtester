from decimal import Decimal

import pytest

from app.stoploss import get_diff_percent


@pytest.mark.parametrize('prev_pl, actual_pl, expected_percent', [
    (Decimal(0), Decimal(0), Decimal(0)),
    (Decimal(0), Decimal(-10), Decimal(1000)),
    (Decimal(100), Decimal(90), Decimal(10)),
    (Decimal(77), Decimal('63.294'), Decimal('17.8')),
    (Decimal(777), Decimal('-388.5'), Decimal('150')),
    (Decimal(77), Decimal('154'), Decimal('-100')),
])
def test_get_diff_percent(prev_pl: Decimal, actual_pl: Decimal, expected_percent: Decimal) -> None:
    result = get_diff_percent(prev_pl, actual_pl)

    assert result == expected_percent
