import logging
from decimal import Decimal

from app.models import FloatingMatrix

logger = logging.getLogger(__name__)


class FloatingSteps:
    current_step: Decimal
    _step_tries: dict[Decimal, int]
    _steps: list[Decimal]
    _tries_left: int

    def __init__(self, matrix: FloatingMatrix) -> None:
        self._step_tries: dict[Decimal, int] = {}
        self._steps: list[Decimal] = []

        for matrix_step in matrix.matrix:
            self._step_tries[matrix_step.percent] = matrix_step.tries
            self._steps.append(matrix_step.percent)

        if not self._steps:
            raise RuntimeError('Invalid floating steps config!')

        self.current_step = self._steps[0]
        self._tries_left = self.get_step_tries_limit(self.current_step)

    def get_step_tries_limit(self, step: Decimal) -> int:
        return self._step_tries[step]

    def to_prev_step(self) -> None:
        logger.debug(f'to_prev_step start {self.current_step=} {self._tries_left}')
        current_step_index = self._steps.index(self.current_step)
        self._tries_left -= 1

        if self._tries_left < 0 and current_step_index:
            self.current_step = self._steps[current_step_index - 1]
            self._tries_left = self.get_step_tries_limit(self.current_step)
        logger.debug(f'to_prev_step end {self.current_step=} {self._tries_left}')

    def to_next_step(self) -> None:
        logger.debug(f'to_next_step start {self.current_step=} {self._tries_left}')
        current_step_index = self._steps.index(self.current_step)
        if current_step_index + 1 < len(self._steps):
            self.current_step = self._steps[current_step_index + 1]

        self._tries_left = self.get_step_tries_limit(self.current_step)
        logger.debug(f'to_next_step end {self.current_step=} {self._tries_left}')




