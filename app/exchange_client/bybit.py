import logging
import time
from dataclasses import asdict
from decimal import Decimal
from typing import Generator

from pybit.unified_trading import HTTP  # type: ignore

from app.exchange_client.base import BaseClient, HistoryPrice, OrderResult
from app.models import Fee, Tick

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
            timeout=30,
            max_retries=20,
            retry_delay=5,
        )
        self._exchange_session.retry_codes.add(10000)

    def next_price(self, start_tick_numeration: int = -1) -> Generator[Tick | None, None, None]:
        tick_number: int = start_tick_numeration
        while True:
            try:
                response = self._exchange_session.get_tickers(
                    category='spot',
                    symbol=self.symbol,
                )
                tick_number += 1
                logger.info('next price response {0}'.format(response.get('result')))
                yield Tick(
                    number=tick_number,
                    bid=Decimal(response.get('result')['list'][0]['bid1Price']),
                    bid_qty=Decimal(response.get('result')['list'][0]['bid1Size']),
                    ask=Decimal(response.get('result')['list'][0]['ask1Price']),
                    ask_qty=Decimal(response.get('result')['list'][0]['ask1Size']),
                    actual_ticker_balance=self.get_asset_balance_cached(),
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
            symbol=self.symbol,
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

    def buy(self, quantity: Decimal, price: Decimal, is_gtc: bool = False) -> OrderResult | None:
        price_str = '{:f}'.format(price)
        try:
            response = self._exchange_session.place_order(
                category='spot',
                symbol=self.symbol,
                side='Buy',
                orderType='Limit',
                qty=str(quantity),
                price=price_str,
                timeInForce='GTC' if is_gtc else 'FOK',
            )
            time.sleep(2)

        except Exception as exc:
            logger.exception(exc)
            return None

        return self.get_order(
            order_id=response.get('result')['orderId'],
        )

    def sell(self, quantity: Decimal, price: Decimal, is_gtc: bool = False) -> OrderResult | None:
        price_str = '{:f}'.format(price)
        try:
            response = self._exchange_session.place_order(
                category='spot',
                symbol=self.symbol,
                side='Sell',
                orderType='Limit',
                qty=str(quantity),
                price=price_str,
                timeInForce='GTC' if is_gtc else 'FOK',
            )
            time.sleep(2)

        except Exception as exc:
            logger.exception(exc)
            return None

        return self.get_order(
            order_id=response.get('result')['orderId'],
        )

    def sell_market(self, quantity: Decimal) -> dict | None:
        try:
            response = self._exchange_session.place_order(
                category='spot',
                symbol=self.symbol,
                side='Sell',
                orderType='Market',
                qty=str(quantity),
                timeInForce='GTC',
            )
            time.sleep(5)
        except Exception as exc:
            logger.exception(exc)
            return None

        order_response = self.get_order(
            order_id=response.get('result')['orderId'],
        )
        logger.info(f"sell market: {order_response=}")

        if order_response:
            return asdict(order_response)
        return None

    def get_asset_balance(self) -> Decimal:
        response_balance = self._exchange_session.get_wallet_balance(
            accountType='UNIFIED',
        )
        balance = sum(
            Decimal(coin.get('walletBalance', 0))
            for coin in response_balance.get('result')['list'][0]['coin']
            if self.symbol.startswith(coin.get('coin'))
        )
        return Decimal(balance)

    def get_order(self, order_id: str | int) -> OrderResult | None:
        try:
            order_response = self._exchange_session.get_order_history(
                category='spot',
                orderId=order_id,
            )
            logger.info('exchange order result {0}'.format(order_response))
            order_response = order_response.get('result')['list'][0]

        except Exception as exc:
            logger.exception(exc)
            return None

        actual_qty = Decimal(order_response['cumExecQty'] or 0)
        total_qty = Decimal(order_response['qty'] or 0)
        actual_rate = Decimal(order_response['avgPrice'] or 0)
        fee = Decimal(order_response.get('cumExecFee') or 0)
        fee_ticker = order_response.get('feeCurrency')
        logger.info(f"get order: {actual_rate=}, {actual_qty=}, {fee=} {fee_ticker=}")

        response = OrderResult(
            is_filled=order_response.get('orderStatus') == 'Filled',
            qty=actual_qty,
            price=actual_rate,
            fee=fee,
            raw_fees=[Fee(qty=fee, ticker=fee_ticker)] if fee and fee_ticker else [],
            qty_left=total_qty - actual_qty,
            order_id=order_response['orderId'] or '',
            raw_response=order_response,
        )
        return response

    def cancel_order(self, order_id: str | int) -> dict | None:
        try:
            cancel_response = self._exchange_session.cancel_order(
                category='spot',
                symbol=self.symbol,
                orderId=order_id,
            )

        except Exception as exc:
            logger.exception(exc)
            return None

        logger.info(f"cancel order: {cancel_response}")
        return cancel_response
