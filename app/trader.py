
import logging
import time

from app.exchange_client.binance import Binance
from app.settings import app_settings
from app.strategy import Strategy

logger = logging.getLogger(__name__)


def main() -> None:
    exchange_client = Binance(symbol=app_settings.symbol)
    failure_counter: int = 0
    strategy = Strategy()

    for tick in exchange_client.next_price():
        logger.info('tick {0}'.format(tick))
        if failure_counter >= app_settings.failure_limit:
            logger.warning('end trading by failure limit')
            break

        if not tick:
            logging.warning('skip tick by failure')
            time.sleep(app_settings.throttling_time)
            failure_counter += 1
            continue

        go_to_next_step = strategy.tick(tick=tick)
        if not go_to_next_step:
            logger.info('end trading by strategy reason')
            break

        if tick.number % app_settings.show_stats_every_ticks == 0:
            strategy.show_results()

    strategy.show_results()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG if app_settings.debug else logging.INFO,
        format='%(asctime)s %(levelname)-8s %(message)s',
    )
    main()
