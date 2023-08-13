from decimal import Decimal


class FloatingSteps:
    step_tries: dict[Decimal, int]
    steps: list[Decimal]
    current_step: Decimal
    tries_left: int

    def __init__(self, filepath: str) -> None:
        self.step_tries: dict[Decimal, int] = {}
        self.steps: list[Decimal] = []

        with open(filepath, 'r') as fd:
            for index, line in enumerate(fd.readlines()):
                if not index or not line:
                    continue

                step = Decimal(line.split(',')[0])
                tries_limit = int(line.split(',')[1])
                self.step_tries[step] = tries_limit
                self.steps.append(step)

        if not self.steps:
            raise RuntimeError('Invalid floating steps config!')

        self.current_step = self.steps[0]
        self.tries_left = self.get_step_tries_limit(self.current_step)

    def get_step_tries_limit(self, step: Decimal) -> int:
        return self.step_tries[step]

    def to_prev_step(self) -> None:
        current_step_index = self.steps.index(self.current_step)
        self.tries_left -= 1

        if self.tries_left < 0 and current_step_index:
            self.current_step = self.steps[current_step_index - 1]
            self.tries_left = self.get_step_tries_limit(self.current_step)

    def to_next_step(self) -> None:
        current_step_index = self.steps.index(self.current_step)
        if current_step_index + 1 < len(self.steps):
            self.current_step = self.steps[current_step_index + 1]

        self.tries_left = self.get_step_tries_limit(self.current_step)




