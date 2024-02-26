import logging
from decimal import Decimal

from app.settings import app_settings

logger = logging.getLogger(__file__)


class StopLoss:
    def __init__(self) -> None:
        self._max_pl: Decimal = Decimal(0)

        self._steps: list[tuple[Decimal, Decimal]] = [
            (
                Decimal(step.split(':')[0]),
                Decimal(step.split(':')[1]),
            )
            for step in app_settings.stop_loss_steps.split(';')
        ]
        self._steps.sort(key=lambda x: x[0], reverse=True)

        if not self._steps:
            raise RuntimeError('Stop loss steps not found!')

    def update_max_pl(self, current_pl: Decimal) -> None:
        self._max_pl = max(self._max_pl, current_pl)

    def is_stop_loss_shot(self, current_pl: Decimal) -> bool:
        if current_pl >= self._max_pl:
            return False

        threshold = self._get_threshold()
        diff = self._max_pl - current_pl
        logger.info('StopLoss: threshold ${0}, diff ${1}, max PL ${2}, current PL ${3}'.format(
            threshold,
            diff,
            self._max_pl,
            current_pl,
        ))
        return diff >= threshold

    def _get_threshold(self) -> Decimal:
        for step in self._steps:
            if self._max_pl >= step[0]:
                return step[1]

        return self._steps[-1][1]
