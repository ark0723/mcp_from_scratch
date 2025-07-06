import datetime
from pathlib import Path
from mcp.server.fastmcp import FastMCP
import requests
from typing import Any
import csv

# set a folder to record the log
BASE_FOLDER = Path(__file__).parent.absolute()
LOG_FILE = BASE_FOLDER / "activity.log"
SYMBOL_MAP_FILE = BASE_FOLDER / "symbol_map.csv"


mcp = FastMCP("binance-mcp")

# Cache for symbol mappings to avoid reading CSV repeatedly
_symbol_cache = None


# Initialize files at module load time
def _initialize_files():
    """Initialize required files (log and symbol map) if they don't exist"""
    # Create log file if it doesn't exist
    if not Path(LOG_FILE).exists():
        Path(LOG_FILE).touch()

    # Create symbol map file if it doesn't exist
    if not Path(SYMBOL_MAP_FILE).exists():
        symbol_mappings = [
            ("btc", "BTCUSDT"),
            ("bitcoin", "BTCUSDT"),
            ("eth", "ETHUSDT"),
            ("ethereum", "ETHUSDT"),
            ("sol", "SOLUSDT"),
            ("solana", "SOLUSDT"),
            ("doge", "DOGEUSDT"),
            ("shiba", "SHIBUSDT"),
            ("xrp", "XRPUSDT"),
            ("ada", "ADAUSDT"),
            ("dot", "DOTUSDT"),
            ("link", "LINKUSDT"),
            ("ltc", "LTCUSDT"),
            ("xlm", "XLMUSDT"),
            ("eos", "EOSUSDT"),
            ("bnb", "BNBUSDT"),
            ("matic", "MATICUSDT"),
            ("avax", "AVAXUSDT"),
            ("algo", "ALGOUSDT"),
            ("ftt", "FTTUSDT"),
            ("mana", "MANAUSDT"),
            ("uni", "UNIUSDT"),
            ("xmr", "XMRUSDT"),
            ("xem", "XEMUSDT"),
        ]

        with open(SYMBOL_MAP_FILE, "w") as f:
            f.write("crypto_name,symbol\n")
            for crypto_name, symbol in symbol_mappings:
                f.write(f"{crypto_name},{symbol}\n")


# Initialize files when module is loaded
_initialize_files()


def load_symbol_mappings():
    """Load symbol mappings from CSV file with caching"""
    global _symbol_cache

    if _symbol_cache is not None:
        return _symbol_cache

    _symbol_cache = {}

    if Path(SYMBOL_MAP_FILE).exists():
        try:
            with open(SYMBOL_MAP_FILE, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    _symbol_cache[row["crypto_name"].lower()] = row["symbol"]
        except Exception as e:
            with open(LOG_FILE, "a") as log_f:
                log_f.write(
                    f"{datetime.datetime.now()}: Error reading symbol_map.csv: {e}\n"
                )

    return _symbol_cache


def get_symbol_from_input(name: str) -> str:
    """Get symbol from input name, first checking CSV mappings, then fallback logic"""
    # Load mappings from CSV
    symbol_mappings = load_symbol_mappings()

    # Check CSV mappings first
    if name.lower() in symbol_mappings:
        return symbol_mappings[name.lower()]
    else:
        return name.upper()


@mcp.resource("file://symbol_map.csv")
def get_symbol_map() -> str:
    with open(SYMBOL_MAP_FILE, "r") as f:
        return f.read()


@mcp.resource("file://activity.log")
def read_log() -> str:
    with open(LOG_FILE, "r") as f:
        return f.read()


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
        with open(LOG_FILE, "a") as f:
            f.write(
                f"{datetime.datetime.now()}: Error getting price for {symbol}: {response.status_code} {response.text}\n"
            )
        raise Exception(
            f"Error getting price for {symbol}: {response.status_code} {response.text}"
        )
    else:
        price = response.json()["price"]
        with open(LOG_FILE, "a") as f:
            f.write(
                f"{datetime.datetime.now()}: Successfully got the current price for {symbol}: {price}\n"
            )
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
        with open(LOG_FILE, "a") as f:
            f.write(
                f"{datetime.datetime.now()}: Error getting price change for {symbol}: {response.status_code} {response.text}\n"
            )
        raise Exception(
            f"Error getting price change for {symbol}: {response.status_code} {response.text}"
        )
    else:
        data = response.json()
        price_change = data["priceChange"]
        price_change_percent = data["priceChangePercent"]

        with open(LOG_FILE, "a") as f:
            f.write(
                f"{datetime.datetime.now()}: Successfully got the price change for {symbol}: {price_change} ({price_change_percent}%)\n"
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
        with open(LOG_FILE, "a") as f:
            f.write(
                f"{datetime.datetime.now()}: Error getting the price change for {symbol} in the window {window}: {response.status_code} {response.text}\n"
            )
        raise Exception(
            f"Error getting the price change for {symbol} in the window {window}: {response.status_code} {response.text}"
        )
    else:
        data = response.json()
        price_change = data["priceChange"]
        price_change_percent = data["priceChangePercent"]
        with open(LOG_FILE, "a") as f:
            f.write(
                f"{datetime.datetime.now()}: Successfully got the price change for {symbol} in the window {window}: {price_change} ({price_change_percent}%)\n"
            )
    return data


if __name__ == "__main__":
    print("Starting Binance MCP server...")
    mcp.run(transport="stdio")
