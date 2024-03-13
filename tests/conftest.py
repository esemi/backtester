from decimal import Decimal
from unittest.mock import Mock

import pytest

from app.exchange_client.base import OrderResult
from app.settings import app_settings


@pytest.fixture
def exchange_client_pass_mock() -> Mock:
    mock = Mock()
    mock.buy = Mock(return_value=OrderResult(
        is_filled=True,
        qty=Decimal('12.888'),
        price=Decimal('35.4050279'),
        fee=Decimal(0),
    ))
    mock.sell = Mock(return_value=OrderResult(
        is_filled=True,
        qty=Decimal('12.888'),
        price=Decimal('9.5791433891'),
        fee=Decimal(0),
    ))
    yield mock


@pytest.fixture
def strategy_disabled() -> None:
    saved_state = app_settings.enabled
    app_settings.enabled = False
    yield
    app_settings.enabled = saved_state


@pytest.fixture
def stop_loss_enabled() -> None:
    stop_loss_enabled_state = app_settings.stop_loss_enabled
    stop_loss_steps_state = app_settings.stop_loss_steps
    app_settings.stop_loss_enabled = True
    app_settings.stop_loss_steps = '0:25;3:2;6:2;9:5;12:8;15:12;18:14;21:16;24:18;27:20;30:21;33:23;36:24;39:25;42:26;45:27;48:28;51:29;57:30;78:31;84:30;87:29;90:28;93:27;96:26;99:25.2'
    yield
    app_settings.stop_loss_enabled = stop_loss_enabled_state
    app_settings.stop_loss_steps = stop_loss_steps_state


@pytest.fixture
def liquidation_enabled() -> None:
    enabled_state = app_settings.liquidation_enabled
    threshold_state = app_settings.liquidation_threshold
    app_settings.liquidation_enabled = True
    app_settings.liquidation_threshold = Decimal(10)
    yield
    app_settings.liquidation_enabled = enabled_state
    app_settings.liquidation_threshold = threshold_state


@pytest.fixture
def baskets_enabled() -> None:
    enabled_state = app_settings.baskets_enabled
    thresholds_state = app_settings.baskets_thresholds
    buy_amount_state = app_settings.baskets_buy_amount
    app_settings.baskets_enabled = True
    app_settings.baskets_thresholds = '5.0;10.0'
    app_settings.baskets_buy_amount = '10.0;9.5;5.0'
    yield
    app_settings.baskets_enabled = enabled_state
    app_settings.baskets_thresholds = thresholds_state
    app_settings.baskets_buy_amount = buy_amount_state


@pytest.fixture
def hard_stop_loss_enabled() -> Decimal:
    threshold = Decimal(10)
    stop_loss_enabled_state = app_settings.stop_loss_hard_enabled
    stop_loss_threshold_state = app_settings.stop_loss_hard_threshold
    app_settings.stop_loss_hard_enabled = True
    app_settings.stop_loss_hard_threshold = threshold
    yield threshold
    app_settings.stop_loss_hard_enabled = stop_loss_enabled_state
    app_settings.stop_loss_hard_threshold = stop_loss_threshold_state


