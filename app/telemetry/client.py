from datetime import datetime
from decimal import Decimal

from app.models import Tick
from app.storage import connection_mysql

_insert_query = """INSERT INTO `telemetry` 
(`bot_name`, `tick_number`, `tick_timestamp`, `bid`, `ask`, `buy_price`, `sell_price`)
VALUES (%s, %s, %s, %s, %s, %s, %s)"""
_cleanup_query = 'DELETE FROM `telemetry` WHERE `bot_name` = %s'


class TelemetryClient:
    """Class for save strategy telemetry for display by google spreadsheets."""
    def __init__(self, bot_name: str):
        self._bot_name = bot_name

    def push(
        self,
        tick: Tick,
        buy_price: Decimal | None = None,
        sell_price: Decimal | None = None,
    ):
        with connection_mysql.cursor() as cursor:
            cursor.execute(_insert_query, (
                self._bot_name,
                tick.number,
                int(datetime.utcnow().timestamp()),
                tick.bid,
                tick.ask,
                buy_price,
                sell_price,
            ))

    def cleanup(self) -> None:
        with connection_mysql.cursor() as cursor:
            cursor.execute(_cleanup_query, (self._bot_name,))
