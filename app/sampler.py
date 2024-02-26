import argparse
import logging
import os
from datetime import datetime, time, timezone

from app.exchange_client.binance import Binance
from app.exchange_client.bybit import ByBit
from app.settings import app_settings

logger = logging.getLogger(__name__)


def main(
    symbol: str,
    start_date: datetime,
    end_date: datetime,
    interval: str = '5m',
    exchange: str = 'binance',
) -> int:
    logger.info('Loading data for {0}-{1} from {2} to {3}'.format(symbol, interval, start_date, end_date))

    exchange_client = {
        'binance': Binance(
            symbol=symbol,
            test_mode=False,
        ),
        'bybit': ByBit(
            symbol=symbol,
            test_mode=False,
        ),
    }[exchange]

    limit: int = 1000
    counter: int = 0

    filepath = os.path.join(
        app_settings.rates_path,
        f'{exchange}_{symbol}_{interval}_{start_date.strftime("%Y-%m-%d_%H-%M-%S")}_{end_date.strftime("%Y-%m-%d_%H-%M-%S")}.csv',
    )

    with open(filepath, 'w') as output_fd:
        output_fd.write('time,open\n')
        start_ms: int = int(start_date.timestamp() * 1000)
        end_ms: int = int(end_date.timestamp() * 1000)

        while start_ms <= end_ms:
            rates = exchange_client.get_klines(interval, start_ms, limit)
            counter += len(rates)
            for rate in rates:
                tick_date = datetime.utcfromtimestamp(rate.timestamp / 1000).replace(tzinfo=timezone.utc)
                if start_date <= tick_date <= end_date:
                    formatted_time = tick_date.strftime('%Y-%m-%dT%H:%M:%S')
                    output_fd.write('{0},{1}\n'.format(formatted_time, rate.price))

            if not rates:
                break

            start_ms = rates[-1].timestamp + 1

    logger.info('Saved {0} rows'.format(counter))
    return counter


def valid_date(s: str) -> datetime:
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        msg = "Not a valid date: {0!r}".format(s)
        raise argparse.ArgumentTypeError(msg)


def valid_time(s: str) -> time:
    try:
        return datetime.strptime(s, "%H:%M:%S").time()
    except ValueError:
        msg = "Not a valid time: {0!r}".format(s)
        raise argparse.ArgumentTypeError(msg)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG if app_settings.debug else logging.INFO,
        format='%(asctime)s %(levelname)-8s %(message)s',
    )
    parser = argparse.ArgumentParser()
    parser.add_argument('--symbol', required=True, help='Symbol code')
    parser.add_argument('--from-date', required=True, help='History from date (eg. 2023-01-01)', type=valid_date)
    parser.add_argument('--from-time', required=True, help='History from time (eg. 00:00:00)', type=valid_time)
    parser.add_argument('--end-date', required=True, help='History to date (eg. 2023-01-25)', type=valid_date)
    parser.add_argument('--end-time', required=True, help='History to time (eg. 23:59:59)', type=valid_time)
    parser.add_argument(
        '--interval',
        choices=['1s', '1m', '3m', '5m', '15m', '30m', '1h'],
        help='Candle interval',
        default='5m',
    )
    parser.add_argument(
        '--exchange',
        choices=['binance', 'bybit'],
        help='Exchange name',
        default='binance',
    )
    args = parser.parse_args()

    start_date = datetime.combine(args.from_date, args.from_time).replace(tzinfo=timezone.utc)
    end_date = datetime.combine(args.end_date, args.end_time).replace(tzinfo=timezone.utc)

    main(args.symbol, start_date, end_date, args.interval, args.exchange)
