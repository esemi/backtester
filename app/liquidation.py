import logging
from datetime import datetime
from decimal import Decimal

from app.exchange_client.base import OrderResult
from app.models import Tick
from app.settings import app_settings

logger = logging.getLogger(__file__)


class Liquidation:
    def __init__(self) -> None:
        self._is_active: bool = False
        self.tries: int = 0
        self.order_id: str | None = None
        self.qty_left: Decimal = Decimal(0)
        self.order_created_at: datetime = datetime.utcnow()

    def is_active(self, tick: Tick) -> bool:
        if not app_settings.liquidation_enabled:
            return False

        if self._is_active:
            return True

        if tick.bid > app_settings.liquidation_threshold:
            return False

        self._is_active = True
        return True

    def process_order_cancel(self) -> None:
        self.tries += 1
        self.order_id = None

    def process_order_create(self, order: OrderResult) -> None:
        self.order_id = order.order_id
        self.order_created_at = datetime.utcnow()
