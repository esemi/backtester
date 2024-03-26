from decimal import Decimal

from app import baskets
from app.floating_steps import FloatingSteps


def test_get_step_tries_limit_happy_path():
    floating_steps = FloatingSteps(baskets.get_floating_matrix(Decimal(0)))

    assert floating_steps.get_step_tries_limit(floating_steps._steps[0]) > 0
