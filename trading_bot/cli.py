"""CLI entrypoint for placing Binance Futures Testnet orders."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Sequence

from trading_bot.client import BinanceFuturesTestnetClient
from trading_bot.config import BASE_URL, get_api_credentials, setup_logging
from trading_bot.errors import BinanceAPIError, NetworkError, TradingBotError, ValidationError


VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}


@dataclass
class OrderRequest:
    symbol: str
    side: str
    order_type: str
    quantity: Decimal
    price: Decimal | None = None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Place a Binance Futures Testnet order (USDT-M)."
    )
    parser.add_argument("--symbol", required=True, help="Trading pair, e.g. BTCUSDT")
    parser.add_argument("--side", required=True, help="BUY or SELL")
    parser.add_argument("--order-type", required=True, help="MARKET or LIMIT")
    parser.add_argument("--quantity", required=True, help="Order quantity")
    parser.add_argument("--price", help="Order price, required for LIMIT orders")
    return parser


def parse_order(args: Sequence[str]) -> OrderRequest:
    parser = build_parser()
    namespace = parser.parse_args(args)

    symbol = namespace.symbol.strip().upper()
    side = namespace.side.strip().upper()
    order_type = namespace.order_type.strip().upper()

    if not symbol:
        raise ValidationError("symbol is required")
    if side not in VALID_SIDES:
        raise ValidationError("side must be BUY or SELL")
    if order_type not in VALID_ORDER_TYPES:
        raise ValidationError("order type must be MARKET or LIMIT")

    quantity = _parse_positive_decimal(namespace.quantity, "quantity")
    price = None

    if order_type == "LIMIT":
        if namespace.price is None:
            raise ValidationError("price is required for LIMIT orders")
        price = _parse_positive_decimal(namespace.price, "price")
    elif namespace.price is not None:
        raise ValidationError("price should only be provided for LIMIT orders")

    return OrderRequest(
        symbol=symbol,
        side=side,
        order_type=order_type,
        quantity=quantity,
        price=price,
    )


def _parse_positive_decimal(raw_value: str, field_name: str) -> Decimal:
    try:
        value = Decimal(raw_value)
    except InvalidOperation as exc:
        raise ValidationError(f"{field_name} must be a valid number") from exc
    if value <= 0:
        raise ValidationError(f"{field_name} must be greater than 0")
    return value


def format_avg_price(response: dict) -> str:
    avg_price = response.get("avgPrice")
    if avg_price not in (None, "", "0.00000"):
        return str(avg_price)

    executed_qty = response.get("executedQty")
    cum_quote = response.get("cumQuote")
    if executed_qty and cum_quote:
        try:
            executed = Decimal(str(executed_qty))
            quote = Decimal(str(cum_quote))
            if executed > 0:
                return format((quote / executed).normalize(), "f")
        except InvalidOperation:
            return "N/A"
    return "N/A"


def print_request_summary(order: OrderRequest) -> None:
    print("Order Request Summary")
    print(f"  Symbol: {order.symbol}")
    print(f"  Side: {order.side}")
    print(f"  Type: {order.order_type}")
    print(f"  Quantity: {order.quantity}")
    print(f"  Price: {order.price if order.price is not None else 'N/A'}")


def print_response_summary(response: dict) -> None:
    print("Order Response Details")
    print(f"  Order ID: {response.get('orderId', 'N/A')}")
    print(f"  Status: {response.get('status', 'N/A')}")
    print(f"  Executed Quantity: {response.get('executedQty', 'N/A')}")
    print(f"  Average Price: {format_avg_price(response)}")


def main(args: Sequence[str] | None = None) -> int:
    setup_logging()
    try:
        order = parse_order(args if args is not None else sys.argv[1:])
        api_key, api_secret = get_api_credentials()
        if not api_key or not api_secret:
            raise ValidationError(
                "BINANCE_API_KEY and BINANCE_API_SECRET must be set in the environment"
            )

        print_request_summary(order)
        client = BinanceFuturesTestnetClient(
            api_key=api_key,
            api_secret=api_secret,
            base_url=BASE_URL,
        )
        response = client.place_order(
            symbol=order.symbol,
            side=order.side,
            order_type=order.order_type,
            quantity=order.quantity,
            price=order.price,
        )
        print_response_summary(response)
        print("Result: Order placed successfully.")
        return 0
    except ValidationError as exc:
        print(f"Result: Validation failed. {exc}", file=sys.stderr)
        return 2
    except BinanceAPIError as exc:
        print(f"Result: Binance API request failed. {exc}", file=sys.stderr)
        return 3
    except NetworkError as exc:
        print(f"Result: Network failure. {exc}", file=sys.stderr)
        return 4
    except TradingBotError as exc:
        print(f"Result: Application error. {exc}", file=sys.stderr)
        return 5
    except Exception as exc:  # pragma: no cover - defensive fallback
        print(f"Result: Unexpected error. {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

