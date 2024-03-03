import logging
from datetime import datetime
from decimal import Decimal
from typing import Generator

from binance.spot import Spot  # type: ignore

from app.exchange_client.base import BaseClient, HistoryPrice, OrderResult
from app.models import Tick

logger = logging.getLogger(__name__)


class Binance(BaseClient):
    def __init__(
        self,
        symbol: str,
        api_key: str = '',
        api_secret: str = '',
        test_mode: bool = False,
    ):
        super().__init__(symbol)
        self._client_spot = Spot(
            api_key=api_key or None,
            api_secret=api_secret or None,
            base_url='https://testnet.binance.vision' if test_mode else 'https://api.binance.com',
        )

    def next_price(self, start_tick_numeration: int = -1) -> Generator[Tick | None, None, None]:
        tick_number: int = start_tick_numeration
        while True:
            try:
                response = self._client_spot.book_ticker(
                    symbol=self._symbol,
                )
                tick_number += 1
                yield Tick(
                    number=tick_number,
                    bid=Decimal(response.get('bidPrice')),
                    ask=Decimal(response.get('askPrice')),
                    bid_qty=Decimal(response.get('bidQty')),
                    ask_qty=Decimal(response.get('askQty')),
                    actual_ticker_balance=self.get_asset_balance_cached(),
                )

            except Exception as e:
                logger.exception(e)
                yield None

    def get_klines(self, interval: str, start_ms: int, limit: int) -> list[HistoryPrice]:
        response = self._client_spot.klines(
            symbol=self._symbol,
            interval=interval,
            startTime=start_ms,
            limit=limit,
        )
        return [
            HistoryPrice(
                price=Decimal(line[1]),  # open rate
                timestamp=line[0],       # Kline open time
            )
            for line in response
        ]

    def buy(self, quantity: Decimal, price: Decimal) -> OrderResult | None:
        price_str = '{:f}'.format(price)
        try:
            response = self._client_spot.new_order(
                symbol=self._symbol,
                side='BUY',
                type='LIMIT',
                timeInForce='FOK',
                quantity=quantity,
                price=price_str,
                recvWindow=15000,
                timestamp=int(datetime.utcnow().timestamp() * 1000),
            )
        except Exception as exc:
            logger.exception(exc)
            return None

        fees = self._get_order_fee(response.get('fills', []), skip_bnb=True)
        actual_qty = Decimal(response['executedQty'])
        actual_rate = Decimal(response['cummulativeQuoteQty']) / (actual_qty or 1)
        logger.info(f"buy: {actual_rate=}, {actual_qty=}, {fees=}, {response.get('fills', [])=}")

        return OrderResult(
            is_filled=response.get('status') == 'FILLED',
            qty=actual_qty,
            price=actual_rate,
            fee=fees,
            raw_response=response,
        )

    def sell(self, quantity: Decimal, price: Decimal) -> OrderResult | None:
        price_str = '{:f}'.format(price)
        try:
            response = self._client_spot.new_order(
                symbol=self._symbol,
                side='SELL',
                type='LIMIT',
                timeInForce='FOK',
                quantity=quantity,
                price=price_str,
                recvWindow=15000,
                timestamp=int(datetime.utcnow().timestamp() * 1000),
            )

        except Exception as exc:
            logger.exception(exc)
            return None

        actual_qty = Decimal(response['executedQty'])
        actual_rate = Decimal(response['cummulativeQuoteQty']) / (actual_qty or 1)
        fees = self._get_order_fee(response.get('fills', []), skip_bnb=True)
        logger.info(f"sell: {actual_rate=}, {actual_qty=}, {fees=}, {response.get('fills', [])=}")

        return OrderResult(
            is_filled=response.get('status') == 'FILLED',
            qty=actual_qty,
            price=actual_rate,
            fee=fees,
            raw_response=response,
        )

    def sell_market(self, quantity: Decimal) -> dict | None:
        try:
            response = self._client_spot.new_order(
                symbol=self._symbol,
                side='SELL',
                type='MARKET',
                quantity=quantity,
                recvWindow=15000,
                timestamp=int(datetime.utcnow().timestamp() * 1000),
            )

        except Exception as exc:
            logger.exception(exc)
            return None

        logger.info(f"sell market: {response=}")
        return response

    def get_asset_balance(self) -> Decimal:
        response_balance = self._client_spot.account()
        balance = [
            Decimal(balance.get('free')) + Decimal(balance.get('locked'))
            for balance in response_balance.get('balances', [])
            if self._symbol.startswith(balance.get('asset'))
        ]
        return Decimal(0) if not balance else balance[0]

    @classmethod
    def _get_order_fee(cls, fills: list[dict], skip_bnb: bool = False) -> Decimal:
        return Decimal(sum([
            Decimal(fill.get('commission', 0))
            for fill in fills
            if not skip_bnb or fill.get('commissionAsset') != 'BNB'
        ]))
