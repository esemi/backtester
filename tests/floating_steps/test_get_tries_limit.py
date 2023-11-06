from app.floating_steps import FloatingSteps
from app.settings import app_settings


def test_get_step_tries_limit_happy_path():
    floating_steps = FloatingSteps(app_settings.float_steps_path)

    assert floating_steps.get_step_tries_limit(floating_steps.steps[0]) > 0
