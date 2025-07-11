import datetime
from pathlib import Path
from fastmcp import FastMCP
import requests
from typing import Any
import csv
from collections import deque
import logging

# In-memory logging for cloud deployment
_activity_logs = deque(maxlen=1000)  # Keep last 1000 log entries
_symbol_cache = None

# Initialize symbol mappings in memory (no local files needed)
SYMBOL_MAPPINGS = {
    "btc": "BTCUSDT",
    "bitcoin": "BTCUSDT",
    "eth": "ETHUSDT",
    "ethereum": "ETHUSDT",
    "sol": "SOLUSDT",
    "solana": "SOLUSDT",
    "doge": "DOGEUSDT",
    "shiba": "SHIBUSDT",
    "xrp": "XRPUSDT",
    "ada": "ADAUSDT",
    "dot": "DOTUSDT",
    "link": "LINKUSDT",
    "ltc": "LTCUSDT",
    "xlm": "XLMUSDT",
    "eos": "EOSUSDT",
    "bnb": "BNBUSDT",
    "matic": "MATICUSDT",
    "avax": "AVAXUSDT",
    "algo": "ALGOUSDT",
    "ftt": "FTTUSDT",
    "mana": "MANAUSDT",
    "uni": "UNIUSDT",
    "xmr": "XMRUSDT",
    "xem": "XEMUSDT",
}

mcp = FastMCP("binance-mcp")


def log_activity(message: str):
    """Log activity to in-memory deque instead of file"""
    timestamp = datetime.datetime.now().isoformat()
    log_entry = f"{timestamp}: {message}"
    _activity_logs.append(log_entry)
    # Also log to console for debugging
    logging.info(log_entry)


def get_symbol_from_input(name: str) -> str:
    """Get symbol from input name using in-memory mappings"""
    return SYMBOL_MAPPINGS.get(name.lower(), name.upper())


@mcp.resource("memory://symbol_map")
def get_symbol_map() -> str:
    """Get symbol mappings as CSV format from memory"""
    csv_content = "crypto_name,symbol\n"
    for crypto_name, symbol in SYMBOL_MAPPINGS.items():
        csv_content += f"{crypto_name},{symbol}\n"
    return csv_content


@mcp.resource("memory://activity_log")
def read_log() -> str:
    """Get recent activity logs from memory"""
    return "\n".join(_activity_logs)


@mcp.tool()
def get_recent_logs(limit: int = 50) -> str:
    """Get recent activity logs (limit: 1-100)"""
    limit = max(1, min(limit, 100))  # Clamp between 1-100
    recent_logs = list(_activity_logs)[-limit:]
    return "\n".join(recent_logs)


@mcp.prompt()
def executive_summary() -> str:
    """Returns an executive summary of Bitcoin and Ethereum"""
    return """
    Get the prices of the following crypto asset: btc, eth

    Provide me with an executive summary including the
    two-sentence summary of the crypto asset, the current price,
    the price change in the last 24 hours, and the percentage change
    in the last 24 hours.

    When using the get_price and get_price_price_change tools,
    use the symbol as the argument.

    Symbols: For bitcoin/btc, the symbol is "BTCUSDT".
    Symbols: For ethereum/eth, the symbol is "ETHUSDT".
    """


@mcp.prompt()
def crypto_summary(cryptos: str) -> str:
    """Return an executive summary of crypto assets (supports multiple assets separated by commas)"""
    return f"""
            Get the current price of the following crypto assets:
            {cryptos}

            If multiple assets are provided (separated by commas), get data for each one.
            Provide a summary including the current price and price change in the last 24 hours for each asset.

            When using the get_price and get_price_24hr_change tools, use the symbol as the argument.

            Symbol mappings:
            For bitcoin/btc, the symbol is BTCUSDT.
            For ethereum/eth, the symbol is ETHUSDT.
            For solana/sol, the symbol is SOLUSDT.
            For doge, the symbol is DOGEUSDT.
            For shiba, the symbol is SHIBUSDT.
            For xrp, the symbol is XRPUSDT.
            For ada, the symbol is ADAUSDT.
            For dot, the symbol is DOTUSDT.
            For link, the symbol is LINKUSDT.
            For ltc, the symbol is LTCUSDT.
            For xlm, the symbol is XLMUSDT.
            For eos, the symbol is EOSUSDT.
            For bnb, the symbol is BNBUSDT.
            For matic, the symbol is MATICUSDT.
            For avax, the symbol is AVAXUSDT.
            For algo, the symbol is ALGOUSDT.
            For ftt, the symbol is FTTUSDT.
            For mana, the symbol is MANAUSDT.
            For uni, the symbol is UNIUSDT.
            For xmr, the symbol is XMRUSDT.
            For xem, the symbol is XEMUSDT.

            Format the output as a clean summary for each asset.
            """


# https://github.com/modelcontextprotocol/python-sdk?tab=readme-ov-file#resources
# example: resource://crypto_price/BTCUSDT
@mcp.resource("resource://crypto_price/{symbol}")
def get_crypto_price(symbol: str) -> str:
    """
    Get the current price of a crypto asset from Binance
    """
    return get_price(symbol)


@mcp.tool()
def get_price(symbol: str) -> Any:
    """
    Get the current price of a crypto asset from Binance

    Args:
        symbol(str): The symbol of the crypto asset to get the price of

    Returns:
        The current price of the crypto asset
    """
    symbol = get_symbol_from_input(symbol)
    url = f"https://api.binance.us/api/v3/ticker/price?symbol={symbol}"
    response = requests.get(url)
    if response.status_code != 200:
        log_activity(
            f"Error getting price for {symbol}: {response.status_code} {response.text}"
        )
        raise Exception(
            f"Error getting price for {symbol}: {response.status_code} {response.text}"
        )
    else:
        price = response.json()["price"]
        log_activity(f"Successfully got the current price for {symbol}: {price}")
    return f"The current price of {symbol} is {price}"


@mcp.tool()
def get_price_24hr_change(symbol: str) -> Any:
    """
    Get the price change of a crypto asset from Binance

    Args:
        symbol(str): The symbol of the crypto asset to get the price change of
    """
    symbol = get_symbol_from_input(symbol)
    url = f"https://api.binance.us/api/v3/ticker/24hr?symbol={symbol}"
    response = requests.get(url)
    if response.status_code != 200:
        log_activity(
            f"Error getting price change for {symbol}: {response.status_code} {response.text}"
        )
        raise Exception(
            f"Error getting price change for {symbol}: {response.status_code} {response.text}"
        )
    else:
        data = response.json()
        price_change = data["priceChange"]
        price_change_percent = data["priceChangePercent"]

        log_activity(
            f"Successfully got the price change for {symbol}: {price_change} ({price_change_percent}%)"
        )
    return data


@mcp.tool()
def get_rolling_windows_price(symbol: str, window: str = "1d") -> Any:
    """
    Get the rolling windows price of a crypto asset from Binance

    Args:
        symbol(str): The symbol of the crypto asset to get the rolling windows price of
        window(str): The window size of the rolling windows price
            - Minutes: 1m, 2m, ..., 59m
            - Hours: 1h, 2h, ..., 23h
            - Days: 1d, 2d, ..., 7d
    """
    symbol = get_symbol_from_input(symbol)
    url = f"https://api.binance.us/api/v3/ticker?symbol={symbol}&windowSize={window}"
    response = requests.get(url)
    if response.status_code != 200:
        log_activity(
            f"Error getting the price change for {symbol} in the window {window}: {response.status_code} {response.text}"
        )
        raise Exception(
            f"Error getting the price change for {symbol} in the window {window}: {response.status_code} {response.text}"
        )
    else:
        data = response.json()
        price_change = data["priceChange"]
        price_change_percent = data["priceChangePercent"]
        log_activity(
            f"Successfully got the price change for {symbol} in the window {window}: {price_change} ({price_change_percent}%)"
        )
    return data


if __name__ == "__main__":
    # Streamable HTTP protocol - optimized for cloud deployment
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8897,
        log_level="info",  # Changed from debug to reduce noise
    )
