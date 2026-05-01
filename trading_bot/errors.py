"""Custom exceptions used by the trading bot."""


class TradingBotError(Exception):
    """Base application error."""


class ValidationError(TradingBotError):
    """Raised when CLI input is invalid."""


class BinanceAPIError(TradingBotError):
    """Raised when the Binance API returns an error response."""

    def __init__(self, message: str, status_code: int | None = None, payload: object | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


class NetworkError(TradingBotError):
    """Raised when the Binance API cannot be reached."""

