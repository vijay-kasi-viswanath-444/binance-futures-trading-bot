"""Binance Futures Testnet REST client."""

from __future__ import annotations

import hashlib
import hmac
import logging
import time
from decimal import Decimal
from typing import Any
from urllib.parse import urlencode

import requests

from trading_bot.errors import BinanceAPIError, NetworkError


class BinanceFuturesTestnetClient:
    """Small REST client for Binance USDT-M Futures Testnet."""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str,
        timeout: int = 10,
    ) -> None:
        self.api_key = api_key
        self.api_secret = api_secret.encode("utf-8")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": api_key})

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: Decimal,
        price: Decimal | None = None,
    ) -> dict[str, Any]:
        """Place a market or limit order."""
        payload: dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": self._normalize_decimal(quantity),
            "timestamp": int(time.time() * 1000),
            "recvWindow": 5000,
        }
        if order_type == "LIMIT":
            payload["price"] = self._normalize_decimal(price)
            payload["timeInForce"] = "GTC"

        return self._signed_request("POST", "/fapi/v1/order", payload)

    def _signed_request(
        self,
        method: str,
        path: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret,
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        signed_query = f"{query_string}&signature={signature}"
        url = f"{self.base_url}{path}"

        self.logger.info("Binance request: %s %s payload=%s", method, url, params)
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=signed_query,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            self.logger.exception("Network failure while calling Binance")
            raise NetworkError(f"Network failure while calling Binance: {exc}") from exc

        self.logger.info(
            "Binance response: status=%s body=%s",
            response.status_code,
            response.text,
        )

        try:
            data = response.json()
        except ValueError as exc:
            raise BinanceAPIError(
                "Binance returned a non-JSON response",
                status_code=response.status_code,
                payload=response.text,
            ) from exc

        if not response.ok:
            message = data.get("msg") if isinstance(data, dict) else "Unknown Binance API error"
            raise BinanceAPIError(
                f"Binance API error: {message}",
                status_code=response.status_code,
                payload=data,
            )
        return data

    @staticmethod
    def _normalize_decimal(value: Decimal | None) -> str:
        if value is None:
            return ""
        return format(value.normalize(), "f")

