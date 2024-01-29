import copy
from decimal import ROUND_DOWN, Decimal

from app.exchange_client.base import OrderResult


class FeesAccountingMixin:
    def __init__(self, *args, **kwargs):
        self._actual_qty_balance = Decimal(0)

    def apply_buy_fee(self, order: OrderResult, digits_round: Decimal) -> OrderResult:
        updated_order = copy.deepcopy(order)
        if not updated_order.fee:
            return updated_order

        updated_order.fee = Decimal(0)

        if self._actual_qty_balance >= order.fee:
            self._actual_qty_balance -= order.fee
            return updated_order

        executed_qty = Decimal(order.qty - order.fee)
        executed_qty_rounded = executed_qty.quantize(digits_round, rounding=ROUND_DOWN)

        updated_order.qty = executed_qty_rounded
        self._actual_qty_balance += (executed_qty - executed_qty_rounded)

        updated_order.price = (order.price * order.qty) / executed_qty
        return updated_order

    def apply_sell_fee(self, order: OrderResult) -> OrderResult:
        updated_order = copy.deepcopy(order)
        if not updated_order.fee:
            return updated_order

        updated_order.fee = Decimal(0)
        updated_order.price = ((order.qty * order.price) - order.fee) / order.qty
        return updated_order

