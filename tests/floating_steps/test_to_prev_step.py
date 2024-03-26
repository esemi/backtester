from decimal import Decimal

from app.floating_steps import FloatingSteps
from app.settings import app_settings


def test_to_prev_step_happy_path():
    floating_steps = FloatingSteps(app_settings.float_steps_path)
    floating_steps.current_step = Decimal(10)
    floating_steps._tries_left = 0

    floating_steps.to_prev_step()

    assert floating_steps.current_step != Decimal(10)
    assert floating_steps._tries_left > 0


def test_to_prev_step_has_tries():
    floating_steps = FloatingSteps(app_settings.float_steps_path)
    floating_steps.current_step = Decimal(10)
    floating_steps._tries_left = 1

    floating_steps.to_prev_step()

    assert floating_steps.current_step == Decimal(10)
    assert floating_steps._tries_left == 0


def test_to_prev_step_first_step():
    floating_steps = FloatingSteps(app_settings.float_steps_path)
    first_step = floating_steps._steps[0]

    floating_steps.to_prev_step()

    assert floating_steps.current_step == first_step


def test_to_prev_step_negative_tries_count():
    floating_steps = FloatingSteps(app_settings.float_steps_path)
    floating_steps._tries_left = 0

    floating_steps.to_prev_step()

    assert floating_steps._tries_left == -1
