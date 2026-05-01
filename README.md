# Simplified Trading Bot

Small Python CLI app for placing `MARKET` and `LIMIT` orders on Binance Futures Testnet (USDT-M).

## Project Structure

```text
trading_bot/
  bot/
    __init__.py
    client.py
    logging_config.py
    orders.py
    validators.py
  __init__.py
  cli.py
README.md
requirements.txt
```

## Features

- Supports `BUY` and `SELL`
- Supports `MARKET` and `LIMIT`
- Uses Binance Futures Testnet base URL: `https://testnet.binancefuture.com`
- Splits CLI logic from API client logic
- Logs API requests, responses, and errors to `logs/trading_bot.log`
- Handles invalid input, Binance API errors, and network failures

## Setup

1. Create and activate a Python 3 virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set your Binance Futures Testnet credentials:

```bash
set BINANCE_API_KEY=your_key_here
set BINANCE_API_SECRET=your_secret_here
```

Or create a local `.env` file in the project root:

```env
BINANCE_API_KEY=your_key_here
BINANCE_API_SECRET=your_secret_here
```

## Usage

Market order:

```bash
python -m trading_bot.cli --symbol BTCUSDT --side BUY --order-type MARKET --quantity 0.001
```

Limit order:

```bash
python -m trading_bot.cli --symbol BTCUSDT --side SELL --order-type LIMIT --quantity 0.001 --price 75000
```

## Output

The app prints:

- order request summary
- order response details including `orderId`, `status`, `executedQty`, and `avgPrice` when available
- a success or failure result message

## Notes

- This app sends requests only to Binance Futures Testnet.
- Binance enforces symbol filters such as step size and tick size. If an order is rejected, check the error message in the console or log file.
- Environment variables from `.env` are loaded automatically if the file exists.
