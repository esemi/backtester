
import logging
import pickle
import signal
import time
from datetime import datetime

from app import storage
from app.exchange_client.base import BaseClient
from app.exchange_client.binance import Binance
from app.exchange_client.bybit import ByBit
from app.settings import app_settings
from app.storage import drop_state, connection_mysql
from app.strategy import BasicStrategy, get_strategy_instance

logger = logging.getLogger(__name__)
_has_stop_request: bool = False


def force_exit_request(*args, **kwargs) -> None:  # type: ignore
    """Stop worker by signal."""
    global _has_stop_request  # noqa: WPS420, WPS442
    _has_stop_request = True  # noqa: WPS122, WPS442
    logger.info('force exit')


def main() -> None:
    exchange_client = _get_exchange_client(app_settings.exchange)
    failure_counter: int = 0

    strategy = get_strategy_instance(
        strategy_type=app_settings.strategy_type,
        exchange_client=exchange_client,
        dry_run=app_settings.dry_run,
    )

    _restore_strategy_state(app_settings.instance_name, strategy)
    start_tick_numeration = strategy.get_last_tick().number if strategy.has_tick_history() else -1

    for tick in exchange_client.next_price(start_tick_numeration):
        logger.info('tick {0}'.format(tick))
        if _has_stop_request:
            logger.warning('end trading by signal')
            break

        if failure_counter >= app_settings.failure_limit:
            logger.warning('end trading by failure limit')
            break

        if not tick:
            logger.warning('skip tick by failure')
            time.sleep(app_settings.throttling_failure_time)
            failure_counter += 1
            continue

        failure_counter = 0

        go_to_next_step = strategy.tick(tick=tick)
        if not go_to_next_step:
            logger.info('end trading by strategy reason')
            drop_state(app_settings.instance_name)
            break

        _save_strategy_state(app_settings.instance_name, strategy)

        if tick.number and tick.number % app_settings.show_stats_every_ticks == 0:
            strategy.save_results()

        _continue_or_break()

    strategy.save_results()


def _get_exchange_client(name: str) -> BaseClient:
    return {
        'binance': Binance(
            symbol=app_settings.symbol,
            api_key=app_settings.binance_api_key,
            api_secret=app_settings.binance_api_secret,
            test_mode=app_settings.exchange_test_mode,
        ),
        'bybit': ByBit(
            symbol=app_settings.symbol,
            api_key=app_settings.bybit_api_key,
            api_secret=app_settings.bybit_api_secret,
            test_mode=app_settings.exchange_test_mode,
        ),
    }[name]


def _save_strategy_state(unique_instance_name: str, strategy_instance: BasicStrategy) -> None:
    serialized_state = pickle.dumps(strategy_instance.get_state_for_save())
    storage.save_state(unique_instance_name, serialized_state)
    logger.info('state saved to redis')


def _restore_strategy_state(unique_instance_name: str, strategy_instance: BasicStrategy) -> None:
    saved_state = storage.get_saved_state(unique_instance_name)
    if not saved_state:
        return

    logger.info('previous state restored by redis')
    deserialized_state = pickle.loads(saved_state)
    strategy_instance.restore_state_from(deserialized_state)


def _continue_or_break() -> None:
    throttling_tick_time = min(app_settings.throttling_time_small_tick, app_settings.throttling_time)
    sleep_end_timestamp: float = datetime.utcnow().timestamp() + float(app_settings.throttling_time)

    while datetime.utcnow().timestamp() < sleep_end_timestamp:
        if _has_stop_request:
            return
        time.sleep(throttling_tick_time)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG if app_settings.debug else logging.INFO,
        format='%(asctime)s %(levelname)-8s %(message)s',
    )

    signal.signal(signal.SIGINT, force_exit_request)
    main()

    try:
        connection_mysql.close()
    except Exception as exc:
        logger.exception(exc)
