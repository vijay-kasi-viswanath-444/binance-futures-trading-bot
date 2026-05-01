"""Logging and environment configuration helpers."""

from __future__ import annotations

import logging
import os
from pathlib import Path


BASE_URL = "https://testnet.binancefuture.com"
LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "trading_bot.log"
ENV_FILE = Path(".env")


def load_dotenv() -> None:
    """Load simple KEY=VALUE pairs from a local .env file if present."""
    if not ENV_FILE.exists():
        return

    for raw_line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def get_api_credentials() -> tuple[str, str]:
    """Load API credentials from environment variables."""
    load_dotenv()
    api_key = os.getenv("BINANCE_API_KEY", "").strip()
    api_secret = os.getenv("BINANCE_API_SECRET", "").strip()
    return api_key, api_secret


def setup_logging() -> Path:
    """Configure file and console logging once for the app."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger()
    if logger.handlers:
        return LOG_FILE

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return LOG_FILE

