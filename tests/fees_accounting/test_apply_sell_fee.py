from decimal import Decimal

from app.exchange_client.base import OrderResult
from app.fees_utils.fees_accounting import FeesAccountingMixin


def test_apply_sell_fee_happy_path():
    raw_order = OrderResult(
        is_filled=True,
        qty=Decimal('13.1'),
        price=Decimal('1.7'),
        fee=Decimal('0.01'),
    )

    updated_order = FeesAccountingMixin().apply_sell_fee(raw_order)

    assert updated_order.qty == raw_order.qty
    assert updated_order.price == Decimal('1.6992366412213740458')  # ((13.1 * 1.7) - 0.01) / 13.1)
    assert updated_order.price <= raw_order.price
    assert updated_order.fee == Decimal(0)


def test_apply_sell_fee_zero_fee():
    raw_order = OrderResult(
        is_filled=True,
        qty=Decimal('13.1'),
        price=Decimal('1.7'),
        fee=Decimal(0),
    )

    updated_order = FeesAccountingMixin().apply_sell_fee(raw_order)

    assert updated_order.qty == raw_order.qty
    assert updated_order.price == raw_order.price
    assert updated_order.fee == raw_order.fee
