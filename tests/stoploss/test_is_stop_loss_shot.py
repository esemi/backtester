from decimal import Decimal

import pytest

from app.stoploss import StopLoss


def test_is_stop_loss_shot_pl_go_upper(stop_loss_enabled) -> None:
    stop_loss_instance = StopLoss()
    stop_loss_instance.update_max_pl(Decimal(10))

    result = stop_loss_instance.is_stop_loss_shot(Decimal(11))

    assert result is False


@pytest.mark.parametrize('max_pl, actual_pl, expected', [
    (Decimal(100), Decimal('74.81'), False),
    (Decimal(100), Decimal('74.80'), True),
    (Decimal(0), Decimal('-24'), False),
    (Decimal(1), Decimal('-24'), True),
])
def test_is_stop_loss_shot_happy_path(max_pl: Decimal, actual_pl: Decimal, expected: bool, stop_loss_enabled) -> None:
    stop_loss_instance = StopLoss()
    stop_loss_instance.update_max_pl(max_pl)

    result = stop_loss_instance.is_stop_loss_shot(actual_pl)

    assert result is expected
