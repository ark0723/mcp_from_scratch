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


if __name__ == "__main__":
    print("Starting MCP server...")
    mcp.run(transport="stdio")