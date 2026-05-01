"""CLI entrypoint for placing Binance Futures Testnet orders."""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

from trading_bot.bot.client import BinanceFuturesTestnetClient
from trading_bot.bot.logging_config import BASE_URL, get_api_credentials, setup_logging
from trading_bot.bot.orders import print_request_summary, print_response_summary, submit_order
from trading_bot.bot.validators import validate_order_input
from trading_bot.errors import BinanceAPIError, NetworkError, TradingBotError, ValidationError


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


def parse_order(args: Sequence[str]):
    parser = build_parser()
    namespace = parser.parse_args(args)
    return validate_order_input(
        symbol=namespace.symbol,
        side=namespace.side,
        order_type=namespace.order_type,
        quantity=namespace.quantity,
        price=namespace.price,
    )


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
        response = submit_order(client, order)
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

