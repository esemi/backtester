import os
from decimal import Decimal

from app.settings import app_settings


class TelemetryClient:
    """Class for save strategy telemetry for display by google spreadsheets."""
    def __init__(self, filename: str):
        self._filepath = os.path.join(app_settings.telemetry_path, filename)

    def push(
        self,
        tick_number: int,
        tick_price: Decimal,
        buy_price: Decimal | None = None,
        sell_price: Decimal | None = None,
    ):
        self._write_csv_line(
            str(tick_number),
            format_decimal(tick_price),
            format_decimal(buy_price or ''),
            format_decimal(sell_price or ''),
        )

    def _write_csv_line(self, *args) -> None:
        with open(self._filepath, 'a+') as fd:
            line = '\t'.join(args)
            fd.write(f'{line}\n')
            fd.flush()


def format_decimal(source: Decimal | str) -> str:
    return str(source).replace('.', ',')
