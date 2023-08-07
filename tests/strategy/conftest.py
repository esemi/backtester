from unittest.mock import Mock

import pytest


@pytest.fixture
def exchange_client_pass_mock() -> Mock:
    mock = Mock()
    mock.buy = Mock(return_value={
        'executedQty': '12.888',
        'cummulativeQuoteQty': '456.3',
        'status': 'FILLED',
    })
    mock.sell = Mock(return_value={
        'executedQty': '12.888',
        'cummulativeQuoteQty': '123.456',
        'status': 'FILLED',
    })
    yield mock
