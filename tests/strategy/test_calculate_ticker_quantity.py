from decimal import Decimal

from app.strategy import calculate_ticker_quantity


def test_calculate_ticker_quantity_happy_path():
    response = calculate_ticker_quantity(
        Decimal('15'),
        Decimal('25869.58'),
        Decimal('0.00001'),
    )

    assert isinstance(response, Decimal)
    assert response == Decimal('0.00058')
