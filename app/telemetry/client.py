from datetime import datetime
from decimal import Decimal

from app.models import Fee, Tick
from app.storage import connection_mysql

_insert_query = """INSERT INTO `telemetry` 
(`bot_name`, `tick_number`, `tick_timestamp`, `bid`, `ask`, `buy_price`, `sell_price`, `buy_fee_qty`, `buy_fee_ticker`, `sell_fee_qty`, `sell_fee_ticker`, `profit_usdt`, `profit_percent`, `bnb_rate`)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
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
        buy_fee: Fee | None = None,
        sell_fee: Fee | None = None,
        profit_usdt: Decimal | None = None,
        profit_percent: Decimal | None = None,
        bnb_rate: Decimal | None = None,
    ):
        if buy_price or sell_price:
            with connection_mysql.cursor() as cursor:
                cursor.execute(_insert_query, (
                    self._bot_name,
                    tick.number,
                    int(datetime.utcnow().timestamp()),
                    tick.bid,
                    tick.ask,
                    buy_price,
                    sell_price,
                    None if not buy_fee else buy_fee.qty,
                    None if not buy_fee else buy_fee.ticker,
                    None if not sell_fee else sell_fee.qty,
                    None if not sell_fee else sell_fee.ticker,
                    profit_usdt,
                    profit_percent,
                    bnb_rate,
                ))

    def cleanup(self) -> None:
        with connection_mysql.cursor() as cursor:
            cursor.execute(_cleanup_query, (self._bot_name,))


class DummyClient(TelemetryClient):
    """Class for fake-save strategy telemetry."""

    def push(self, *args, **kwargs):
        pass

    def cleanup(self, *args, **kwargs) -> None:
        pass
