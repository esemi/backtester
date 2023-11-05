from decimal import Decimal

from app.floating_steps import FloatingSteps
from app.settings import app_settings


def test_init_happy_path():
    floating_steps = FloatingSteps(app_settings.float_steps_path)

    assert len(floating_steps.steps) > 0
    assert floating_steps.current_step > Decimal(0)
    assert floating_steps.tries_left >= 1
