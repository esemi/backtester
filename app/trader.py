
import logging
import signal
import time

from app.exchange_client.binance import Binance
from app.floating_steps import FloatingSteps
from app.settings import app_settings
from app.strategy import BasicStrategy, FloatingStrategy

logger = logging.getLogger(__name__)
_has_stop_request: bool = False


def force_exit_request(*args, **kwargs) -> None:  # type: ignore
    """Stop worker by signal."""
    global _has_stop_request  # noqa: WPS420, WPS442
    _has_stop_request = True  # noqa: WPS122, WPS442
    logger.info('force exit')


def main() -> None:
    exchange_client = Binance(
        symbol=app_settings.symbol,
        api_key=app_settings.binance_api_key,
        api_secret=app_settings.binance_api_secret,
        test_mode=app_settings.exchange_test_mode,
    )
    failure_counter: int = 0

    if app_settings.strategy_type == 'basic':
        strategy = BasicStrategy(exchange_client=exchange_client, dry_run=app_settings.dry_run)

    elif app_settings.strategy_type == 'floating':
        strategy = FloatingStrategy(
            exchange_client=exchange_client,
            steps_instance=FloatingSteps(app_settings.float_steps_path),
            dry_run=app_settings.dry_run,
        )

    else:
        raise RuntimeError('Unknown strategy type!')

    for tick in exchange_client.next_price():
        logger.info('tick {0}'.format(tick))
        if _has_stop_request:
            logger.warning('end trading by signal')
            break

        if failure_counter >= app_settings.failure_limit:
            logger.warning('end trading by failure limit')
            break

        if not tick:
            logging.warning('skip tick by failure')
            time.sleep(app_settings.throttling_failure_time)
            failure_counter += 1
            continue

        failure_counter = 0

        go_to_next_step = strategy.tick(tick=tick)
        if not go_to_next_step:
            logger.info('end trading by strategy reason')
            break

        if tick.number and tick.number % app_settings.show_stats_every_ticks == 0:
            strategy.show_results()

        time.sleep(app_settings.throttling_time)

    strategy.show_results()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG if app_settings.debug else logging.INFO,
        format='%(asctime)s %(levelname)-8s %(message)s',
    )

    signal.signal(signal.SIGINT, force_exit_request)
    main()
