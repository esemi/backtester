"""Temporary storage place for save open positions between bot restart."""
from datetime import timedelta

import redis

from app.settings import app_settings

connection: redis.Redis = redis.from_url(str(app_settings.redis_dsn))
STORAGE_PREFIX: str = 'backtester:trader-bot:{0}'


def save_state(name: str, state: bytes) -> None:
    connection.set(STORAGE_PREFIX.format(name), state)
    connection.expire(STORAGE_PREFIX.format(name), time=timedelta(hours=3))


def get_saved_state(name: str) -> bytes | None:
    response = connection.get(STORAGE_PREFIX.format(name))
    return response


def drop_state(name: str) -> None:
    connection.delete(STORAGE_PREFIX.format(name))
