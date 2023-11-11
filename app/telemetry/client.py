import os
from datetime import datetime
from decimal import Decimal

from app.models import Tick


class TelemetryClient:
    """Class for save strategy telemetry for display by google spreadsheets."""
    def __init__(self, filepath: str):
        os.makedirs(filepath, exist_ok=True)
        self._filepath = os.path.join(filepath, 'telemetry.tsv')

    def push(
        self,
        tick: Tick,
        buy_price: Decimal | None = None,
        sell_price: Decimal | None = None,
    ):
        self._write_csv_line(
            str(tick.number),
            str(int(datetime.utcnow().timestamp())),
            format_decimal(tick.bid),
            format_decimal(tick.ask),
            format_decimal(buy_price or ''),
            format_decimal(sell_price or ''),
        )

    def cleanup(self) -> None:
        if os.path.exists(self._filepath):
            os.remove(self._filepath)

    def _write_csv_line(self, *args) -> None:
        with open(self._filepath, 'a+') as fd:
            line = '\t'.join(args)
            fd.write(f'{line}\n')
            fd.flush()


def format_decimal(source: Decimal | str) -> str:
    return str(source).replace('.', ',')
