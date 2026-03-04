import hashlib
import hmac
import json
import logging
import time
from datetime import datetime
from decimal import Decimal
from typing import Any, Generator
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.exchange_client.base import BaseClient, HistoryPrice, OrderResult
from app.models import Fee, Tick

logger = logging.getLogger(__name__)


class BingX(BaseClient):
    def __init__(
        self,
        symbol: str,
        api_key: str = '',
        api_secret: str = '',
        test_mode: bool = False,
    ):
        super().__init__(symbol)
        self._api_key = api_key
        self._api_secret = api_secret
        self._base_url = 'https://open-api.bingx.com'
        if test_mode:
            logger.warning('BingX test mode flag is set, public endpoint is used: %s', self._base_url)

    def next_price(self, start_tick_numeration: int = -1) -> Generator[Tick | None, None, None]:
        tick_number: int = start_tick_numeration
        while True:
            try:
                response = self._public_request(
                    method='GET',
                    path='/openApi/spot/v1/ticker/bookTicker',
                    params={'symbol': self.symbol},
                )
                payload = self._extract_data(response)
                tick_number += 1
                yield Tick(
                    number=tick_number,
                    bid=Decimal(str(payload.get('bidPrice', '0'))),
                    ask=Decimal(str(payload.get('askPrice', '0'))),
                    bid_qty=Decimal(str(payload.get('bidQty', '0'))),
                    ask_qty=Decimal(str(payload.get('askQty', '0'))),
                    actual_ticker_balance=self.get_asset_balance_cached(),
                )
            except Exception as exc:
                logger.exception(exc)
                yield None

    def get_klines(self, interval: str, start_ms: int, limit: int) -> list[HistoryPrice]:
        response = self._public_request(
            method='GET',
            path='/openApi/spot/v1/market/kline',
            params={
                'symbol': self.symbol,
                'interval': interval,
                'startTime': start_ms,
                'limit': limit,
            },
        )
        payload = self._extract_data(response)
        return [
            HistoryPrice(
                price=Decimal(str(line[1])),
                timestamp=int(line[0]),
            )
            for line in payload
        ]

    def buy(self, quantity: Decimal, price: Decimal, is_gtc: bool = False) -> OrderResult | None:
        return self._place_order(
            side='BUY',
            quantity=quantity,
            price=price,
            is_gtc=is_gtc,
        )

    def sell(self, quantity: Decimal, price: Decimal, is_gtc: bool = False) -> OrderResult | None:
        return self._place_order(
            side='SELL',
            quantity=quantity,
            price=price,
            is_gtc=is_gtc,
        )

    def sell_market(self, quantity: Decimal) -> dict | None:
        try:
            response = self._signed_request(
                method='POST',
                path='/openApi/spot/v1/trade/order',
                params={
                    'symbol': self.symbol,
                    'side': 'SELL',
                    'type': 'MARKET',
                    'quantity': str(quantity),
                },
            )
            payload = self._extract_data(response)
            order_id = payload.get('orderId') or payload.get('id')
            if not order_id:
                return payload
            order_result = self.get_order(order_id=order_id)
            return order_result.raw_response if order_result else payload
        except Exception as exc:
            logger.exception(exc)
            return None

    def get_asset_balance(self) -> Decimal:
        response = self._signed_request(
            method='GET',
            path='/openApi/spot/v1/account/balance',
        )
        payload = self._extract_data(response)
        raw_symbol = self._get_raw_symbol()
        for row in payload.get('balances', payload if isinstance(payload, list) else []):
            asset = row.get('asset') or row.get('coin') or row.get('currency')
            if asset != raw_symbol:
                continue
            free_balance = Decimal(str(row.get('free', row.get('freeAmount', 0)) or 0))
            locked_balance = Decimal(str(row.get('locked', row.get('freezeAmount', 0)) or 0))
            return free_balance + locked_balance
        return Decimal(0)

    def get_order(self, order_id: str | int) -> OrderResult | None:
        try:
            response = self._signed_request(
                method='GET',
                path='/openApi/spot/v1/trade/order',
                params={
                    'symbol': self.symbol,
                    'orderId': order_id,
                },
            )
            payload = self._extract_data(response)
            return self._build_order_result(payload)
        except Exception as exc:
            logger.exception(exc)
            return None

    def cancel_order(self, order_id: str | int) -> dict | None:
        try:
            response = self._signed_request(
                method='DELETE',
                path='/openApi/spot/v1/trade/order',
                params={
                    'symbol': self.symbol,
                    'orderId': order_id,
                },
            )
            return self._extract_data(response)
        except Exception as exc:
            logger.exception(exc)
            return None

    def get_bnb_rate(self) -> Decimal | None:
        return None

    def _place_order(self, side: str, quantity: Decimal, price: Decimal, is_gtc: bool) -> OrderResult | None:
        try:
            response = self._signed_request(
                method='POST',
                path='/openApi/spot/v1/trade/order',
                params={
                    'symbol': self.symbol,
                    'side': side,
                    'type': 'LIMIT',
                    'quantity': str(quantity),
                    'price': '{:f}'.format(price),
                    'timeInForce': 'GTC' if is_gtc else 'FOK',
                },
            )
            payload = self._extract_data(response)
            order_id = payload.get('orderId') or payload.get('id')
            if not order_id:
                return self._build_order_result(payload)
            time.sleep(1)
            return self.get_order(order_id=order_id)
        except Exception as exc:
            logger.exception(exc)
            return None

    def _build_order_result(self, payload: dict[str, Any]) -> OrderResult:
        executed_qty = Decimal(str(payload.get('executedQty', payload.get('executedQuantity', 0)) or 0))
        orig_qty = Decimal(str(payload.get('origQty', payload.get('quantity', executed_qty)) or 0))
        quote_qty = Decimal(str(payload.get('cummulativeQuoteQty', payload.get('executedAmount', 0)) or 0))
        avg_price = Decimal(str(payload.get('price', payload.get('avgPrice', 0)) or 0))
        actual_rate = avg_price if avg_price > 0 else (quote_qty / (executed_qty or 1))
        fee = Decimal(str(payload.get('commission', payload.get('executedCommission', payload.get('fee', 0))) or 0))
        fee_asset = payload.get('commissionAsset') or payload.get('feeAsset') or payload.get('feeCurrency')
        status = str(payload.get('status', payload.get('orderStatus', ''))).upper()

        raw_fees: list[Fee] = []
        if fee > 0 and fee_asset:
            raw_fees.append(Fee(qty=fee, ticker=str(fee_asset)))

        return OrderResult(
            is_filled=status == 'FILLED',
            qty=executed_qty,
            qty_left=orig_qty - executed_qty,
            price=actual_rate,
            fee=fee,
            raw_fees=raw_fees,
            order_id=payload.get('orderId', payload.get('id', '')),
            raw_response=payload,
        )

    def _public_request(self, method: str, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._request(method=method, path=path, params=params or {}, is_signed=False)

    def _signed_request(self, method: str, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = params.copy() if params else {}
        payload['timestamp'] = int(datetime.utcnow().timestamp() * 1000)
        payload['recvWindow'] = 15000
        query = self._build_query(payload)
        signature = hmac.new(
            self._api_secret.encode('utf-8'),
            query.encode('utf-8'),
            hashlib.sha256,
        ).hexdigest()
        payload['signature'] = signature
        return self._request(method=method, path=path, params=payload, is_signed=True)

    @classmethod
    def _build_query(cls, params: dict[str, Any]) -> str:
        return urlencode(sorted((key, value) for key, value in params.items() if value is not None))

    def _request(self, method: str, path: str, params: dict[str, Any], is_signed: bool) -> dict[str, Any]:
        query = self._build_query(params)
        url = '{0}{1}'.format(self._base_url, path)
        if query:
            url = '{0}?{1}'.format(url, query)
        headers = {'Content-Type': 'application/json'}
        if is_signed and self._api_key:
            headers['X-BX-APIKEY'] = self._api_key

        request = Request(
            url=url,
            headers=headers,
            method=method,
        )
        with urlopen(request, timeout=30) as response:
            body = response.read().decode('utf-8')
        decoded = json.loads(body)
        if str(decoded.get('code', '0')) not in {'0', ''}:
            raise ValueError('bingx api error: {0}'.format(decoded))
        return decoded

    @classmethod
    def _extract_data(cls, response: dict[str, Any]) -> Any:
        data = response.get('data')
        if isinstance(data, dict) and 'data' in data:
            return data.get('data')
        return data if data is not None else response
