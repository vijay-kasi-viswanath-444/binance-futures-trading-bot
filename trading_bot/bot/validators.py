"""Validation helpers for CLI order input."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from trading_bot.errors import ValidationError


VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}


@dataclass
class OrderRequest:
    symbol: str
    side: str
    order_type: str
    quantity: Decimal
    price: Decimal | None = None


def validate_order_input(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: str | None = None,
) -> OrderRequest:
    normalized_symbol = symbol.strip().upper()
    normalized_side = side.strip().upper()
    normalized_order_type = order_type.strip().upper()

    if not normalized_symbol:
        raise ValidationError("symbol is required")
    if normalized_side not in VALID_SIDES:
        raise ValidationError("side must be BUY or SELL")
    if normalized_order_type not in VALID_ORDER_TYPES:
        raise ValidationError("order type must be MARKET or LIMIT")

    parsed_quantity = parse_positive_decimal(quantity, "quantity")
    parsed_price = None

    if normalized_order_type == "LIMIT":
        if price is None:
            raise ValidationError("price is required for LIMIT orders")
        parsed_price = parse_positive_decimal(price, "price")
    elif price is not None:
        raise ValidationError("price should only be provided for LIMIT orders")

    return OrderRequest(
        symbol=normalized_symbol,
        side=normalized_side,
        order_type=normalized_order_type,
        quantity=parsed_quantity,
        price=parsed_price,
    )


def parse_positive_decimal(raw_value: str, field_name: str) -> Decimal:
    try:
        value = Decimal(raw_value)
    except InvalidOperation as exc:
        raise ValidationError(f"{field_name} must be a valid number") from exc
    if value <= 0:
        raise ValidationError(f"{field_name} must be greater than 0")
    return value

