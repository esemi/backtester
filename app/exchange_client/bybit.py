import logging
from decimal import Decimal
from typing import Generator

from pybit.unified_trading import HTTP  # type: ignore

from app.exchange_client.base import BaseClient, OrderResult
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
                response = self._exchange_session.get_kline(
                    category='spot',
                    symbol=self._symbol,
                    interval='1',
                    limit=1,
                )
                tick_number += 1
                logger.info('next price response {0}'.format(response.get('result')))
                yield Tick(
                    number=tick_number,
                    price=Decimal(response.get('result')['list'][0][4]),
                )
            except Exception as e:
                logger.exception(e)
                yield None

    def buy(self, quantity: Decimal, price: Decimal) -> OrderResult | None:
        try:
            response = self._exchange_session.place_order(
                category='spot',
                symbol=self._symbol,
                side='Buy',
                orderType='Limit',
                qty=str(quantity),
                price=str(price),
                timeInForce='FOK',
            )
            order_response = self._exchange_session.get_order_history(
                category='spot',
                orderId=response.get('result')['orderId'],
            ).get('result')['list']
            logger.info('exchange order result {0}'.format(order_response))
            order_response = order_response[0]

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
        try:
            response = self._exchange_session.place_order(
                category='spot',
                symbol=self._symbol,
                side='Sell',
                orderType='Limit',
                qty=str(quantity),
                price=str(price),
                timeInForce='FOK',
            )
        except Exception as exc:
            logger.exception(exc)
            return None

        try:
            order_response = self._exchange_session.get_order_history(
                category='spot',
                orderId=response.get('result')['orderId'],
            ).get('result')['list'][0]
        except Exception as exc:
            logger.exception(exc)
            return None

        return OrderResult(
            is_filled=order_response.get('orderStatus') == 'Filled',
            qty=Decimal(order_response['cumExecQty']),
            price=Decimal(order_response['avgPrice']),
            raw_response=order_response,
        )

