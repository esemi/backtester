"""Temporary storage place for save open positions between bot restart."""
from datetime import datetime
from decimal import Decimal

import pymysql
import redis
from pymysql.cursors import DictCursor

from app.settings import app_settings

STATS_KEY: str = 'backtester:trader-bot:{0}:stats'
STATE_KEY: str = 'backtester:trader-bot:{0}'

connection: redis.Redis = redis.from_url(str(app_settings.redis_dsn))
_connection: pymysql.Connection = None  # type: ignore


def get_mysql_connection() -> pymysql.Connection:
    global _connection
    if _connection is None:
        _connection = pymysql.connect(
            host=app_settings.mysql_host,
            user=app_settings.mysql_user,
            password=app_settings.mysql_password,
            database=app_settings.mysql_db,
            charset='utf8mb4',
            autocommit=True,
            cursorclass=DictCursor,
        )
    return _connection


def save_stats_fallback(name: str, stats: dict) -> None:
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


def save_stats(bot_name: str, stats: dict) -> None:
    save_stats_fallback(bot_name, stats)

    columns = [
        column_name
        for column_name in stats.keys()
    ]

    values = [
        stats.get(column_name)
        for column_name in columns
    ]

    query = f"""INSERT INTO `stats` 
        (`bot_name`, {', '.join(columns)})
        VALUES (%s, {', '.join(['%s'] * len(columns))})"""
    with get_mysql_connection().cursor() as cursor:
        cursor.execute('DELETE FROM `stats` WHERE `bot_name` = %s', (
            bot_name,
        ))
        cursor.execute(query, (
            bot_name,
            *values,
        ))


def get_saved_stats(bot_name: str) -> dict | None:
    with get_mysql_connection().cursor() as cursor:
        query = "SELECT * FROM `stats` WHERE `bot_name` = %s ORDER BY created_at DESC LIMIT 1"
        cursor.execute(query, (bot_name,))
        return cursor.fetchone()


def save_state(name: str, state: bytes) -> None:
    connection.set(STATE_KEY.format(name), state)


def get_saved_state(name: str) -> bytes | None:
    response = connection.get(STATE_KEY.format(name))
    return response


def drop_state(name: str) -> None:
    connection.delete(STATE_KEY.format(name))
