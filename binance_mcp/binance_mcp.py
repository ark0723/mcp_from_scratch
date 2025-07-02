from mcp.server.fastmcp import FastMCP
import requests
from typing import Any

mcp = FastMCP("binance-mcp")


def get_symbol_from_input(name: str) -> str:
    if name.lower() in ["btc", "bitcoin"]:
        return "BTCUSDT"
    elif name.lower() in ["eth", "ethereum"]:
        return "ETHUSDT"
    elif name.lower() in ["sol", "solana"]:
        return "SOLUSDT"
    else:
        return name.upper()


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
    response.raise_for_status()
    return response.json()

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
    response.raise_for_status()
    return response.json()

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
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    print("Starting MCP server...")
    mcp.run(transport="stdio")