from decimal import Decimal

from app.floating_steps import FloatingSteps
from app.settings import app_settings


def test_to_next_step_happy_path():
    floating_steps = FloatingSteps(app_settings.float_steps_path)

    floating_steps.to_next_step()

    assert floating_steps.current_step == Decimal('0.4')
    assert floating_steps.tries_left == 4


def test_to_next_step_last_step():
    floating_steps = FloatingSteps(app_settings.float_steps_path)
    floating_steps.current_step = Decimal(10)
    floating_steps.tries_left = 100500

    floating_steps.to_next_step()

    assert floating_steps.current_step == Decimal(10)
    assert floating_steps.tries_left == 1
