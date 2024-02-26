from decimal import Decimal

import pytest

from app.stoploss import StopLoss


@pytest.mark.parametrize("max_pl, expected_threshold", [
    (Decimal(100500), Decimal('25.2')),
    (Decimal(99), Decimal('25.2')),
    (Decimal(98), Decimal(26)),
    (Decimal(96), Decimal(26)),
    (Decimal(4), Decimal(2)),
    (Decimal(3), Decimal(2)),
    (Decimal(2), Decimal(25)),
    (Decimal(0), Decimal(25)),
    (Decimal(-100), Decimal(25)),
    (Decimal(-100500), Decimal(25)),
])
def test_get_threshold(max_pl: Decimal, expected_threshold: Decimal, stop_loss_enabled) -> None:
    stop_loss_instance = StopLoss()
    stop_loss_instance.update_max_pl(max_pl)

    result = stop_loss_instance._get_threshold()

    assert result == expected_threshold


def test_get_threshold_negative_pl(stop_loss_enabled) -> None:
    stop_loss_instance = StopLoss()
    stop_loss_instance._max_pl = Decimal(-100)

    result = stop_loss_instance._get_threshold()

    assert result == Decimal(25)

