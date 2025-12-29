from datetime import timedelta, datetime, UTC


class SlidingWindowCounter:
    def __init__(self, ttl_threshold: timedelta = timedelta(hours=24)):
        self._ttl_threshold: timedelta = ttl_threshold
        self._counters: list[tuple[int, float]] = []

    def inc(self, count: int = 1, ts: float | None = None) -> None:
        self._counters.append((count, ts or datetime.now(UTC).timestamp()))

    def get_total(self) -> int:
        self._rotate()
        return sum([
            counter
            for counter, _ in self._counters
        ])

    def _rotate(self) -> None:
        time_threshold = (datetime.now(UTC) - self._ttl_threshold).timestamp()
        self._counters = [
            (counter, ttl)
            for counter, ttl in self._counters
            if ttl >= time_threshold
        ]
