from typing import Generator

from app.models import Tick


class BaseClient:

    def __init__(self, symbol: str):
        self._symbol = symbol

    def next_price(self) -> Generator[Tick | None, None, None]:
        # todo abstract
        yield None
