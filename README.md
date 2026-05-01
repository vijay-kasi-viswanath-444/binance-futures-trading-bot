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
cli.py
main.py
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
python cli.py --symbol BTCUSDT --side BUY --order-type MARKET --quantity 0.001
```

Limit order:

```bash
python cli.py --symbol BTCUSDT --side SELL --order-type LIMIT --quantity 0.001 --price 70000
```

## Output

The app prints:

- order request summary
- order response details including `orderId`, `status`, `executedQty`, and `avgPrice` when available
- a success or failure result message

`main.py` is also available as a convenience entrypoint and calls the same CLI logic.

## Notes

- This app sends requests only to Binance Futures Testnet.
- Binance enforces symbol filters such as step size and tick size. If an order is rejected, check the error message in the console or log file.
- Environment variables from `.env` are loaded automatically if the file exists.

## Suggested Submission Checklist

- Confirm `python main.py --symbol BTCUSDT --side BUY --order-type MARKET --quantity 0.001` runs with your testnet credentials
- Confirm `python cli.py --symbol BTCUSDT --side BUY --order-type MARKET --quantity 0.001` runs with your testnet credentials
- Confirm `python cli.py --symbol BTCUSDT --side SELL --order-type LIMIT --quantity 0.001 --price 70000` runs
- Open `logs/trading_bot.log` and verify requests, responses, and errors are recorded
- Be ready to explain the structure:
  - `trading_bot/bot/client.py` handles Binance REST calls
  - `trading_bot/bot/validators.py` handles input validation
  - `trading_bot/bot/orders.py` handles order submission and output formatting
  - `trading_bot/bot/logging_config.py` handles logging and credentials
  - `trading_bot/cli.py` is the application CLI layer
- Keep your real API keys out of screenshots or shared files
