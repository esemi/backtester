from decimal import Decimal

from app.liquidation import Liquidation
from app.models import Tick


def test_is_active_disabled_by_settings() -> None:
    tick = Tick(
        number=0,
        bid=Decimal(10),
        ask=Decimal(100500),
    )
    instance = Liquidation()

    result = instance.is_active(tick)

    assert result is False


def test_is_active_disabled_by_tick_price(liquidation_enabled) -> None:
    tick = Tick(
        number=0,
        bid=Decimal(11),
        ask=Decimal(100500),
    )
    instance = Liquidation()

    result = instance.is_active(tick)

    assert result is False


def test_is_active_already_activated(liquidation_enabled) -> None:
    tick = Tick(
        number=0,
        bid=Decimal(11),
        ask=Decimal(100500),
    )
    instance = Liquidation()
    instance._is_active = True

    result = instance.is_active(tick)

    assert result is True


def test_is_active_happy_path(liquidation_enabled) -> None:
    tick = Tick(
        number=0,
        bid=Decimal(10),
        ask=Decimal(100500),
    )
    instance = Liquidation()

    result = instance.is_active(tick)

    assert result is True
