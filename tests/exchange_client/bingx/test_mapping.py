from decimal import Decimal
from unittest.mock import Mock

from app.exchange_client.bingx import BingX


def test_next_price_happy_path():
    client = BingX(symbol='BTCUSDT')
    client._request = Mock(return_value={  # type: ignore
        'code': 0,
        'data': {
            'bidPrice': '100.1',
            'askPrice': '100.2',
            'bidQty': '1.3',
            'askQty': '1.4',
        },
    })
    client.get_asset_balance = Mock(return_value=Decimal('0.5'))  # type: ignore

    response = next(client.next_price())

    assert response is not None
    assert response.number == 0
    assert response.bid == Decimal('100.1')
    assert response.ask == Decimal('100.2')
    assert response.bid_qty == Decimal('1.3')
    assert response.ask_qty == Decimal('1.4')
    assert response.actual_ticker_balance == Decimal('0.5')


def test_get_klines_happy_path():
    client = BingX(symbol='BTCUSDT')
    client._request = Mock(return_value={  # type: ignore
        'code': 0,
        'data': [
            [1700000000000, '99.1'],
            [1700000060000, '99.2'],
        ],
    })

    response = client.get_klines(interval='1m', start_ms=1700000000000, limit=2)

    assert len(response) == 2
    assert response[0].timestamp == 1700000000000
    assert response[0].price == Decimal('99.1')
    assert response[1].timestamp == 1700000060000
    assert response[1].price == Decimal('99.2')


def test_get_order_happy_path():
    client = BingX(symbol='BTCUSDT')
    client._request = Mock(return_value={  # type: ignore
        'code': 0,
        'data': {
            'orderId': '123',
            'status': 'FILLED',
            'executedQty': '2',
            'origQty': '3',
            'cummulativeQuoteQty': '200',
            'commission': '0.1',
            'commissionAsset': 'USDT',
        },
    })

    response = client.get_order(order_id='123')

    assert response is not None
    assert response.is_filled is True
    assert response.qty == Decimal('2')
    assert response.qty_left == Decimal('1')
    assert response.price == Decimal('100')
    assert response.fee == Decimal('0.1')
    assert response.raw_fees[0].ticker == 'USDT'
