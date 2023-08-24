import logging
import os
from decimal import Decimal

from app.exchange_client.dummy import Dummy
from app.floating_steps import FloatingSteps
from app.models import Tick
from app.settings import app_settings
from app.strategy import BasicStrategy, FloatingStrategy

logger = logging.getLogger(__name__)


def main() -> None:
    exchange_client = Dummy(symbol='dummy')

    if app_settings.strategy_type == 'basic':
        strategy = BasicStrategy(exchange_client=exchange_client, dry_run=True)

    elif app_settings.strategy_type == 'floating':
        strategy = FloatingStrategy(
            exchange_client=exchange_client,
            steps_instance=FloatingSteps(app_settings.float_steps_path),
            dry_run=True,
        )

    else:
        raise RuntimeError('Unknown strategy type!')

    for tick in get_rates(app_settings.rates_filename):
        logger.info('tick {0}'.format(tick))

        go_to_next_step = strategy.tick(tick=tick)
        if not go_to_next_step:
            logger.info('end trading')
            break

    strategy.show_results()


def get_rates(filename: str) -> list[Tick]:
    filepath = os.path.abspath(os.path.join(
        app_settings.rates_path,
        filename,
    ))

    output: list[Tick] = []
    with open(filepath) as fd:
        tick_number = 0
        for num, line in enumerate(fd):
            if not num or not line:
                continue

            output.append(Tick(
                number=tick_number,
                price=Decimal(line.split(',')[1]),
            ))
            tick_number += 1
    return output


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG if app_settings.debug else logging.WARNING,
        format='%(asctime)s %(levelname)-8s %(message)s',
    )
    main()
