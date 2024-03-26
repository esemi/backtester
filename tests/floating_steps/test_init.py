from decimal import Decimal

from app import baskets
from app.floating_steps import FloatingSteps


def test_init_happy_path():
    floating_steps = FloatingSteps(baskets.get_floating_matrix(Decimal(0)))

    assert len(floating_steps._steps) > 0
    assert floating_steps.current_step > Decimal(0)
    assert floating_steps._tries_left >= 1
