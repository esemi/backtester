from typing import Generator

from app.exchange_client.base import BaseClient
from app.models import Tick


class Binance(BaseClient):
    def next_price(self) -> Generator[Tick | None, None, None]:
        # todo impl
        while True:
            yield None
