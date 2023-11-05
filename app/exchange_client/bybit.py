import logging
import time
from decimal import Decimal
from typing import Generator

from pybit.unified_trading import HTTP  # type: ignore

from app.exchange_client.base import BaseClient, OrderResult, HistoryPrice
from app.models import Tick

logger = logging.getLogger(__name__)


class ByBit(BaseClient):
    def __init__(
        self,
        symbol: str,
        api_key: str = '',
        api_secret: str = '',
        test_mode: bool = False,
    ):
        super().__init__(symbol)

        self._exchange_session = HTTP(
            testnet=test_mode,
            api_key=api_key or None,
            api_secret=api_secret or None,
        )

    def next_price(self, start_tick_numeration: int = -1) -> Generator[Tick | None, None, None]:
        tick_number: int = start_tick_numeration
        while True:
            try:
                response = self._exchange_session.get_tickers(
                    category='spot',
                    symbol=self._symbol,
                )
                tick_number += 1
                logger.info('next price response {0}'.format(response.get('result')))
                yield Tick(
                    number=tick_number,
                    bid=Decimal(response.get('result')['list'][0]['bid1Price']),
                    bid_qty=Decimal(response.get('result')['list'][0]['bid1Size']),
                    ask=Decimal(response.get('result')['list'][0]['ask1Price']),
                    ask_qty=Decimal(response.get('result')['list'][0]['ask1Size']),
                )
            except Exception as e:
                logger.exception(e)
                yield None

    def get_klines(self, interval: str, start_ms: int, limit: int) -> list[HistoryPrice]:
        interval_adopted = {
            '1m': 1,
            '3m': 3,
            '5m': 5,
            '15m': 15,
            '30m': 30,
            '1h': 60,
        }[interval]

        response = self._exchange_session.get_kline(
            category='spot',
            symbol=self._symbol,
            interval=interval_adopted,
            start=start_ms,
            limit=limit,
        )
        return [
            HistoryPrice(
                price=Decimal(line[1]),  # open rate
                timestamp=int(line[0]),  # Kline open time
            )
            for line in reversed(response.get('result')['list'])
        ]

    def buy(self, quantity: Decimal, price: Decimal) -> OrderResult | None:
        price_str = '{:f}'.format(price)
        try:
            response = self._exchange_session.place_order(
                category='spot',
                symbol=self._symbol,
                side='Buy',
                orderType='Limit',
                qty=str(quantity),
                price=price_str,
                timeInForce='FOK',
            )
            time.sleep(2)
            order_response = self._exchange_session.get_order_history(
                category='spot',
                orderId=response.get('result')['orderId'],
            )
            logger.info('exchange order result {0} {1}'.format(response, order_response))
            order_response = order_response.get('result')['list'][0]

        except Exception as exc:
            logger.exception(exc)
            return None

        return OrderResult(
            is_filled=order_response.get('orderStatus') == 'Filled',
            qty=Decimal(order_response['cumExecQty'] or 0),
            price=Decimal(order_response['avgPrice'] or 0),
            raw_response=order_response,
        )

    def sell(self, quantity: Decimal, price: Decimal) -> OrderResult | None:
        price_str = '{:f}'.format(price)
        try:
            response = self._exchange_session.place_order(
                category='spot',
                symbol=self._symbol,
                side='Sell',
                orderType='Limit',
                qty=str(quantity),
                price=price_str,
                timeInForce='FOK',
            )
            time.sleep(2)
            order_response = self._exchange_session.get_order_history(
                category='spot',
                orderId=response.get('result')['orderId'],
            )
            logger.info('exchange order result {0} {1}'.format(response, order_response))
            order_response = order_response.get('result')['list'][0]

        except Exception as exc:
            logger.exception(exc)
            return None

        return OrderResult(
            is_filled=order_response.get('orderStatus') == 'Filled',
            qty=Decimal(order_response['cumExecQty'] or 0),
            price=Decimal(order_response['avgPrice'] or 0),
            raw_response=order_response,
        )

