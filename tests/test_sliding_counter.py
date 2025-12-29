import time
from datetime import timedelta

from app.state_utils.sliding_counter import SlidingWindowCounter


def test_sliding_counter_happy_path():
    slider = SlidingWindowCounter()
    slider.inc(7)
    slider.inc()

    assert slider.get_total() == 8


def test_sliding_counter_rotation():
    slider = SlidingWindowCounter(ttl_threshold=timedelta(seconds=5))
    slider.inc()
    time.sleep(3)
    slider.inc()
    slider.inc()
    time.sleep(2)

    assert slider.get_total() == 2

    time.sleep(4)
    assert slider.get_total() == 0
