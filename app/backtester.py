import argparse
import logging
import os
from datetime import datetime, timezone
from decimal import Decimal

from app.exchange_client.dummy import Dummy
from app.models import Tick
from app.settings import APP_PATH, app_settings
from app.strategy import get_strategy_instance

logger = logging.getLogger(__name__)


BACKTESTER_TICK_QTY = Decimal(999999999999)


def main(
    use_every_n_tick: int = 1,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> None:
    strategy = get_strategy_instance(
        strategy_type=app_settings.strategy_type,
        exchange_client=Dummy(symbol='dummy'),
        dry_run=True,
    )

    for tick in get_rates(
        app_settings.rates_filename,
        use_every_n_tick,
        start_date,
        end_date,
    ):
        logger.info('tick {0}'.format(tick))

        go_to_next_step = strategy.tick(tick=tick)
        if not go_to_next_step:
            logger.info('end trading')
            break

    strategy.show_results()


def get_rates(
    filename: str,
    use_every_n_tick: int = 1,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> list[Tick]:
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

            if num % use_every_n_tick:
                continue

            if start_date and end_date:
                tick_date = datetime.fromisoformat(line.split(',')[0]).replace(tzinfo=timezone.utc)
                if tick_date < start_date or tick_date > end_date:
                    continue

            price = Decimal(line.split(',')[1])
            output.append(Tick(
                number=tick_number,
                bid=price,
                ask=price,
                bid_qty=BACKTESTER_TICK_QTY,
                ask_qty=BACKTESTER_TICK_QTY,
            ))
            tick_number += 1
    return output


def valid_datetime(s: str) -> datetime:
    try:
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    except ValueError:
        msg = "Not a valid date: {0!r}".format(s)
        raise argparse.ArgumentTypeError(msg)


if __name__ == '__main__':
    logging.basicConfig(
        filename=os.path.join(APP_PATH, 'backtest.log'),
        filemode='w',
        level=logging.DEBUG if app_settings.debug else logging.INFO,
        format='%(asctime)s %(levelname)-8s %(message)s',
    )

    parser = argparse.ArgumentParser()
    parser.add_argument('--from-date', default=None, help='Use ticks from datetime (eg. 2023-01-01 00:00:00)', type=valid_datetime)
    parser.add_argument('--to-date', default=None, help='Use ticks to datetime (eg. 2023-02-02 23:59:59)', type=valid_datetime)
    parser.add_argument('--used-ticks', default=1, help='Use every N tick', type=int)
    args = parser.parse_args()

    main(
        use_every_n_tick=args.used_ticks,
        start_date=args.from_date,
        end_date=args.to_date,
    )
