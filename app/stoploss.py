import logging
from decimal import Decimal
from typing import Self

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
        if not self._steps:
            raise RuntimeError('Stop loss steps not found!')

    def update_max_pl(self, current_pl: Decimal) -> None:
        self._max_pl = max(self._max_pl, current_pl)

    def is_stop_loss_shot(self, current_pl: Decimal) -> bool:
        if self._max_pl < app_settings.stop_loss_pl_threshold:
            return False

        if current_pl >= self._max_pl:
            return False

        percent_threshold = self._get_percent_threshold()
        diff_percent = get_diff_percent(self._max_pl, current_pl)
        logger.info('StopLoss: {0}% threshold, {1}% diff, {2} max PL, {3} current PL'.format(
            percent_threshold,
            diff_percent,
            self._max_pl,
            current_pl,
        ))
        return diff_percent >= percent_threshold

    def _get_percent_threshold(self) -> Decimal:
        percent_threshold = self._steps[0][1]
        for step in self._steps:
            if self._max_pl > step[0]:
                break
            percent_threshold = step[1]

        return percent_threshold


def get_diff_percent(value_prev: Decimal, value_new: Decimal) -> Decimal:
    diff_nominal = value_prev - value_new
    if not diff_nominal:
        return Decimal(0)
    one_percent = (value_prev or Decimal(1)) / Decimal(100)
    return diff_nominal / one_percent
