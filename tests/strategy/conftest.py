from decimal import Decimal
from unittest.mock import Mock

import pytest

from app.exchange_client.base import OrderResult


@pytest.fixture
def exchange_client_pass_mock() -> Mock:
    mock = Mock()
    mock.buy = Mock(return_value=OrderResult(
        is_filled=True,
        qty=Decimal('12.888'),
        price=Decimal('35.4050279'),
    ))
    mock.sell = Mock(return_value=OrderResult(
        is_filled=True,
        qty=Decimal('12.888'),
        price=Decimal('9.5791433891'),
    ))
    yield mock
