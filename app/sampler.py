import argparse
import logging
import os
from datetime import datetime

from app.exchange_client.binance import Binance
from app.settings import app_settings


logger = logging.getLogger(__name__)


def main(symbol: str, start_date: datetime, interval: str = '5m') -> int:
    logger.info('load sample for {0}-{1} from {2}'.format(symbol, interval, start_date))
    binance_client = Binance(symbol=symbol, test_mode=False)
    limit: int = 1000
    counter: int = 0
    filepath = os.path.join(
        app_settings.rates_path,
        f'BINANCE_{symbol}_{interval}_{start_date.date().isoformat()}.csv',
    )
    with open(filepath, 'w') as output_fd:
        output_fd.write('time,open\n')
        start_ms: int = int(start_date.timestamp() * 1000)

        while True:
            rates = binance_client.get_klines(interval, start_ms, limit)
            counter += len(rates)
            for tick_time, tick_rate in rates:
                tick_date = datetime.utcfromtimestamp(tick_time / 1000)
                output_fd.write('{0},{1}\n'.format(tick_date.isoformat(), tick_rate))

            if len(rates) < limit:
                break

            start_ms = rates[-1][0]+1

    logger.info('saved {0} rows'.format(counter))
    return counter


def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        msg = "not a valid date: {0!r}".format(s)
        raise argparse.ArgumentTypeError(msg)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG if app_settings.debug else logging.INFO,
        format='%(asctime)s %(levelname)-8s %(message)s',
    )
    parser = argparse.ArgumentParser()
    parser.add_argument('--symbol', required=True, help='Symbol code')
    parser.add_argument('--from-date', required=True, help='History from date to now (eg. 2023-01-25)', type=valid_date)
    parser.add_argument(
        '--interval',
        choices=['1m', '3m', '5m', '15m', '30m', '1h'],
        help='Candle interval',
        default='5m',
    )
    args = parser.parse_args()

    main(args.symbol, args.from_date, args.interval)
