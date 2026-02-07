"""Temporary storage place for save open positions between bot restart."""
import json
import logging
import os
import random
import time
from datetime import datetime
from decimal import Decimal

import pymysql
import redis
from pymysql.cursors import DictCursor

from app.settings import app_settings

logger = logging.getLogger(__name__)

connection: redis.Redis = redis.from_url(str(app_settings.redis_dsn))
connection_mysql = pymysql.connect(
    host=app_settings.mysql_host,
    user=app_settings.mysql_user,
    password=app_settings.mysql_password,
    database=app_settings.mysql_db,
    charset='utf8mb4',
    autocommit=True,
    cursorclass=DictCursor,
)

STATS_KEY: str = 'backtester:trader-bot:{0}:stats'
TELEMETRY_BUFFER_KEY: str = 'backtester:trader-bot:{0}:telemetry-buffer'
MYSQL_RETRY_EXC = (pymysql.err.OperationalError, pymysql.err.InterfaceError, pymysql.err.InternalError)


def _normalize_mysql_param(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Decimal) or isinstance(value, float):
        return str(value)
    return value


def _sleep_backoff(attempt: int) -> None:
    base_delay = max(0.0, float(app_settings.mysql_retry_base_delay))
    max_delay = max(base_delay, float(app_settings.mysql_retry_max_delay))
    delay = min(max_delay, base_delay * (2 ** attempt))
    jitter = delay * 0.2 * random.random()
    time.sleep(delay + jitter)


def mysql_execute(query: str, params=None, *, many: bool = False) -> bool:
    attempts = max(1, int(app_settings.mysql_retry_attempts))
    for attempt in range(attempts):
        try:
            connection_mysql.ping(reconnect=True)
            with connection_mysql.cursor() as cursor:
                if many:
                    cursor.executemany(query, params)
                else:
                    cursor.execute(query, params)
            return True
        except MYSQL_RETRY_EXC as exc:
            logger.warning('mysql error: %s (attempt %s/%s)', exc, attempt + 1, attempts)
            if attempt + 1 >= attempts:
                return False
            _sleep_backoff(attempt)
        except Exception as exc:
            logger.exception('mysql unexpected error: %s', exc)
            return False
    return False


def mysql_fetchone(query: str, params=None):
    attempts = max(1, int(app_settings.mysql_retry_attempts))
    for attempt in range(attempts):
        try:
            connection_mysql.ping(reconnect=True)
            with connection_mysql.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchone()
        except MYSQL_RETRY_EXC as exc:
            logger.warning('mysql error: %s (attempt %s/%s)', exc, attempt + 1, attempts)
            if attempt + 1 >= attempts:
                return None
            _sleep_backoff(attempt)
        except Exception as exc:
            logger.exception('mysql unexpected error: %s', exc)
            return None
    return None


def buffer_telemetry(bot_name: str, params: tuple) -> None:
    key = TELEMETRY_BUFFER_KEY.format(bot_name)
    try:
        payload = [_normalize_mysql_param(value) for value in params]
        connection.rpush(key, json.dumps(payload, ensure_ascii=False))
        max_len = int(app_settings.mysql_buffer_max_len)
        if max_len > 0:
            connection.ltrim(key, -max_len, -1)
    except Exception as exc:
        logger.exception('failed to buffer telemetry: %s', exc)


def flush_telemetry(bot_name: str, insert_query: str) -> int:
    key = TELEMETRY_BUFFER_KEY.format(bot_name)
    batch_size = int(app_settings.mysql_buffer_flush_batch)
    if batch_size <= 0:
        return 0
    try:
        items = connection.lrange(key, 0, batch_size - 1)
        if not items:
            return 0
        params_list = []
        for raw in items:
            if isinstance(raw, bytes):
                raw = raw.decode('utf-8')
            params_list.append(tuple(json.loads(raw)))
        if not mysql_execute(insert_query, params_list, many=True):
            return 0
        connection.ltrim(key, len(items), -1)
        return len(items)
    except Exception as exc:
        logger.exception('failed to flush telemetry buffer: %s', exc)
        return 0


def save_stats(bot_name: str, stats: dict) -> None:
    _save_stats_fallback(bot_name, stats)

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
    if not mysql_execute('DELETE FROM `stats` WHERE `bot_name` = %s', (bot_name,)):
        return
    mysql_execute(query, (
        bot_name,
        *values,
    ))


def get_saved_stats(bot_name: str) -> dict | None:
    query = "SELECT * FROM `stats` WHERE `bot_name` = %s ORDER BY created_at DESC LIMIT 1"
    return mysql_fetchone(query, (bot_name,))


def save_state(state: bytes) -> None:
    with open(app_settings.state_filepath, mode='wb') as f:
        f.write(state)


def get_saved_state() -> bytes | None:
    try:
        with open(app_settings.state_filepath, mode='rb') as f:
            return f.read()
    except FileNotFoundError:
        return None


def drop_state() -> None:
    try:
        os.unlink(app_settings.state_filepath)
    except FileNotFoundError:
        pass


def _save_stats_fallback(name: str, stats: dict) -> None:
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
