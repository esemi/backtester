from decimal import Decimal

import pytest

from app.stoploss import StopLoss


@pytest.mark.parametrize('max_pl, expected_percent', [
    (Decimal(100500), Decimal(25)),
    (Decimal(51), Decimal(25)),
    (Decimal(50), Decimal(50)),
    (Decimal(30), Decimal(50)),
    (Decimal(10), Decimal(80)),
    (Decimal(9), Decimal(80)),
    (Decimal(0), Decimal(80)),
])
def test_get_diff_percent(max_pl: Decimal, expected_percent: Decimal) -> None:
    stop_loss_instance = StopLoss()
    stop_loss_instance.update_max_pl(max_pl)

    result = stop_loss_instance._get_percent_threshold()

    assert result == expected_percent
