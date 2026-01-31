import logging
from datetime import datetime
from decimal import Decimal
from itertools import groupby
from typing import Generator
from uuid import uuid4

from binance.spot import Spot  # type: ignore

from app.exchange_client.base import BaseClient, HistoryPrice, OrderResult
from app.models import Fee, Tick

logger = logging.getLogger(__name__)


class Binance(BaseClient):
    def __init__(
        self,
        symbol: str,
        api_key: str = '',
        api_secret: str = '',
        test_mode: bool = False,
        rebate_code: str = '',
    ):
        super().__init__(symbol)
        self._client_spot = Spot(
            api_key=api_key or None,
            api_secret=api_secret or None,
            base_url='https://testnet.binance.vision' if test_mode else 'https://api.binance.com',
        )
        self._rebate_code = rebate_code
        self._bnb_rate_cache_ttl: int = 0
        self._bnb_rate_cache_value: Decimal | None = None

    def next_price(self, start_tick_numeration: int = -1) -> Generator[Tick | None, None, None]:
        tick_number: int = start_tick_numeration
        while True:
            try:
                response = self._client_spot.book_ticker(
                    symbol=self.symbol,
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
            symbol=self.symbol,
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

    def buy(self, quantity: Decimal, price: Decimal, is_gtc: bool = False) -> OrderResult | None:
        price_str = '{:f}'.format(price)
        try:
            response = self._client_spot.new_order(
                symbol=self.symbol,
                side='BUY',
                type='LIMIT',
                timeInForce='GTC' if is_gtc else 'FOK',
                quantity=quantity,
                price=price_str,
                recvWindow=15000,
                timestamp=int(datetime.utcnow().timestamp() * 1000),
                newClientOrderId=self._get_client_order_id(),
            )
        except Exception as exc:
            logger.exception(exc)
            return None

        fees = self._get_order_fee(response.get('fills', []), skip_bnb=True)
        raw_fees = self._get_raw_fees(response.get('fills', []))
        actual_qty = Decimal(response['executedQty'])
        actual_rate = Decimal(response['cummulativeQuoteQty']) / (actual_qty or 1)
        logger.info(f"buy: {actual_rate=}, {actual_qty=}, {fees=}, {response.get('fills', [])=}")

        return OrderResult(
            is_filled=response.get('status') == 'FILLED',
            qty=actual_qty,
            qty_left=Decimal(response['origQty']) - actual_qty,
            price=actual_rate,
            fee=fees,
            raw_fees=raw_fees,
            order_id=response['orderId'],
            raw_response=response,
        )

    def sell(self, quantity: Decimal, price: Decimal, is_gtc: bool = False) -> OrderResult | None:
        price_str = '{:f}'.format(price)
        try:
            response = self._client_spot.new_order(
                symbol=self.symbol,
                side='SELL',
                type='LIMIT',
                timeInForce='GTC' if is_gtc else 'FOK',
                quantity=quantity,
                price=price_str,
                recvWindow=15000,
                timestamp=int(datetime.utcnow().timestamp() * 1000),
                newClientOrderId=self._get_client_order_id(),
            )

        except Exception as exc:
            logger.exception(exc)
            return None

        actual_qty = Decimal(response['executedQty'])
        actual_rate = Decimal(response['cummulativeQuoteQty']) / (actual_qty or 1)
        fees = self._get_order_fee(response.get('fills', []), skip_bnb=True)
        raw_fees = self._get_raw_fees(response.get('fills', []))
        logger.info(f"sell: {actual_rate=}, {actual_qty=}, {fees=}, {response.get('fills', [])=}")

        return OrderResult(
            is_filled=response.get('status') == 'FILLED',
            qty=actual_qty,
            qty_left=Decimal(response['origQty']) - actual_qty,
            price=actual_rate,
            fee=fees,
            raw_fees=raw_fees,
            order_id=response['orderId'],
            raw_response=response,
        )

    def sell_market(self, quantity: Decimal) -> dict | None:
        try:
            response = self._client_spot.new_order(
                symbol=self.symbol,
                side='SELL',
                type='MARKET',
                quantity=quantity,
                recvWindow=15000,
                timestamp=int(datetime.utcnow().timestamp() * 1000),
                newClientOrderId=self._get_client_order_id(),
            )

        except Exception as exc:
            logger.exception(exc)
            return None

        logger.info(f"sell market: {response=}")
        return response

    def get_asset_balance(self) -> Decimal:
        response_balance = self._client_spot.account()
        logger.info('response_balance={0}'.format(response_balance))
        raw_symbol = self._get_raw_symbol()
        balance = [
            Decimal(balance.get('free')) + Decimal(balance.get('locked'))
            for balance in response_balance.get('balances', [])
            if raw_symbol == balance.get('asset')
        ]
        return Decimal(0) if not balance else balance[0]

    def get_order(self, order_id: str | int) -> OrderResult | None:
        try:
            response = self._client_spot.get_order(
                symbol=self.symbol,
                orderId=order_id,
                timestamp=int(datetime.utcnow().timestamp() * 1000),
            )
        except Exception as exc:
            logger.exception(exc)
            return None

        actual_qty = Decimal(response['executedQty'])
        actual_rate = Decimal(response['cummulativeQuoteQty']) / (actual_qty or 1)
        fees = self._get_order_fee(response.get('fills', []), skip_bnb=True)
        raw_fees = self._get_raw_fees(response.get('fills', []))
        logger.info(f"get order: {actual_rate=}, {actual_qty=}, {fees=}, {response.get('fills', [])=}")

        return OrderResult(
            is_filled=response.get('status') == 'FILLED',
            qty=actual_qty,
            qty_left=Decimal(response['origQty']) - actual_qty,
            price=actual_rate,
            fee=fees,
            raw_fees=raw_fees,
            order_id=response['orderId'],
            raw_response=response,
        )

    def cancel_order(self, order_id: str | int) -> dict | None:
        try:
            response = self._client_spot.cancel_order(
                symbol=self.symbol,
                orderId=order_id,
                timestamp=int(datetime.utcnow().timestamp() * 1000),
            )
        except Exception as exc:
            logger.exception(exc)
            return None

        logger.info(f"cancel order: {response}")
        return response

    def get_bnb_rate(self) -> Decimal | None:
        now = int(datetime.utcnow().timestamp())
        if self._bnb_rate_cache_ttl > now and self._bnb_rate_cache_value is not None:
            return self._bnb_rate_cache_value

        try:
            response = self._client_spot.book_ticker(
                symbol='BNBUSDT',
            )
            price = Decimal(response.get('askPrice'))
        except Exception as exc:
            logger.exception(exc)
            return None

        self._bnb_rate_cache_value = price
        self._bnb_rate_cache_ttl = now + 30
        return price

    def _get_client_order_id(self) -> str:
        uid = uuid4().hex
        return 'x-{0}-{1}-{2}'.format(
            self._rebate_code,
            uid,
            int(datetime.utcnow().timestamp() * 1000),
        )[:36]

    @classmethod
    def _get_order_fee(cls, fills: list[dict], skip_bnb: bool = False) -> Decimal:
        return Decimal(sum([
            Decimal(fill.get('commission', 0))
            for fill in fills
            if not skip_bnb or fill.get('commissionAsset') != 'BNB'
        ]))

    @classmethod
    def _get_raw_fees(cls, fills: list[dict]) -> list[Fee]:
        groups = groupby(
            iterable=fills,
            key=lambda x: x.get('commissionAsset'),
        )

        fees_by_asset: list[Fee] = []
        for asset_name, fees in groups:
            qty = Decimal(sum([
                Decimal(fee.get('commission', 0))
                for fee in fees
            ]))
            if qty > 0:
                fees_by_asset.append(
                    Fee(qty=qty, ticker=asset_name),  # type: ignore
                )
        return fees_by_asset
