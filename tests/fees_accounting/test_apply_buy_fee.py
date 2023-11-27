from decimal import Decimal

from app.exchange_client.base import OrderResult
from app.fees_utils.fees_accounting import FeesAccountingMixin


def test_apply_buy_fee_happy_path():
    raw_order = OrderResult(
        is_filled=True,
        qty=Decimal('13.1'),
        price=Decimal('1.7'),
        fee=Decimal('0.01'),
    )
    strategy = FeesAccountingMixin()

    updated_order = strategy.apply_buy_fee(raw_order, Decimal('0.1'))

    assert strategy._actual_qty_balance == Decimal('0.09')
    assert updated_order.fee == Decimal(0)
    assert updated_order.qty == Decimal('13.0')
    assert updated_order.qty <= raw_order.qty
    assert updated_order.price == Decimal('1.7012987012987012987')  # (13.1 * 1.7) / 13.09


def test_apply_buy_fee_zero_fee():
    raw_order = OrderResult(
        is_filled=True,
        qty=Decimal('13.1'),
        price=Decimal('1.7'),
        fee=Decimal(0),
    )
    strategy = FeesAccountingMixin()

    updated_order = strategy.apply_buy_fee(raw_order, Decimal('0.1'))

    assert updated_order.qty == raw_order.qty
    assert updated_order.price == raw_order.price
    assert updated_order.fee == raw_order.fee
    assert strategy._actual_qty_balance == Decimal(0)


def test_apply_buy_fee_use_account_balance():
    raw_order = OrderResult(
        is_filled=True,
        qty=Decimal('13.1'),
        price=Decimal('1.7'),
        fee=Decimal('0.01'),
    )
    strategy = FeesAccountingMixin()
    strategy._actual_qty_balance = Decimal('0.9999')

    updated_order = strategy.apply_buy_fee(raw_order, Decimal('0.1'))

    assert updated_order.qty == raw_order.qty
    assert updated_order.price == raw_order.price
    assert updated_order.fee == Decimal(0)
    assert strategy._actual_qty_balance == Decimal('0.9899')
