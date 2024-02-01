from decimal import Decimal

import pytest

from app.stoploss import StopLoss


def test_is_stop_loss_shot_threshold() -> None:
    stop_loss_instance = StopLoss()
    stop_loss_instance.update_max_pl(Decimal(9))

    result = stop_loss_instance.is_stop_loss_shot(Decimal(0))

    assert result is False


def test_is_stop_loss_shot_pl_go_upper() -> None:
    stop_loss_instance = StopLoss()
    stop_loss_instance.update_max_pl(Decimal(10))

    result = stop_loss_instance.is_stop_loss_shot(Decimal(11))

    assert result is False


@pytest.mark.parametrize('max_pl, actual_pl, expected', [
    (Decimal(100), Decimal('75.1'), False),
    (Decimal(100), Decimal('75.0'), True),
])
def test_is_stop_loss_shot_happy_path(max_pl: Decimal, actual_pl: Decimal, expected: bool) -> None:
    stop_loss_instance = StopLoss()
    stop_loss_instance.update_max_pl(max_pl)

    result = stop_loss_instance.is_stop_loss_shot(actual_pl)

    assert result is expected
