"""Temporary storage place for save open positions between bot restart."""
from datetime import datetime
from decimal import Decimal

import redis

from app.settings import app_settings

connection: redis.Redis = redis.from_url(str(app_settings.redis_dsn))
STATS_KEY: str = 'backtester:trader-bot:{0}:stats'
STATE_KEY: str = 'backtester:trader-bot:{0}'


def save_stats(name: str, stats: dict) -> None:
    prepared_stats = {}
    for key, value in stats.items():
        if value is None:
            value = ''
        if isinstance(value, datetime):
            value = value.isoformat()
        if isinstance(value, Decimal) or isinstance(value, float):
            value = str(value)

        prepared_stats[key] = value

    connection.hset(STATS_KEY.format(name), mapping=prepared_stats)


def get_saved_stats(name: str) -> dict | None:
    return connection.hgetall(STATS_KEY.format(name))


def save_state(name: str, state: bytes) -> None:
    connection.set(STATE_KEY.format(name), state)


def get_saved_state(name: str) -> bytes | None:
    response = connection.get(STATE_KEY.format(name))
    return response


def drop_state(name: str) -> None:
    connection.delete(STATE_KEY.format(name))
