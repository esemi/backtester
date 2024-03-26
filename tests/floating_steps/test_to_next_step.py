from decimal import Decimal

from app import baskets
from app.floating_steps import FloatingSteps


def test_to_next_step_happy_path():
    floating_steps = FloatingSteps(baskets.get_floating_matrix(Decimal(0)))
    start_step = floating_steps.current_step

    floating_steps.to_next_step()

    assert floating_steps.current_step > start_step


def test_to_next_step_last_step():
    floating_steps = FloatingSteps(baskets.get_floating_matrix(Decimal(0)))
    floating_steps.current_step = floating_steps._steps[-1]
    floating_steps._tries_left = 100500

    floating_steps.to_next_step()

    assert floating_steps.current_step == floating_steps._steps[-1]
