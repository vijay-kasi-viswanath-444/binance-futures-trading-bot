"""Order placement and output formatting helpers."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from trading_bot.bot.client import BinanceFuturesTestnetClient
from trading_bot.bot.validators import OrderRequest


def submit_order(
    client: BinanceFuturesTestnetClient,
    order: OrderRequest,
) -> dict:
    """Submit an order through the Binance client."""
    return client.place_order(
        symbol=order.symbol,
        side=order.side,
        order_type=order.order_type,
        quantity=order.quantity,
        price=order.price,
    )


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

