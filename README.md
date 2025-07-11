# Binance MCP Server

A Model Context Protocol (MCP) server for cryptocurrency price data from Binance, built with FastMCP. This server provides real-time crypto price information and supports both STDIO and HTTP transports.

## Features

- 🔍 **Real-time crypto price lookup** - Get current prices for popular cryptocurrencies
- 📈 **24-hour price changes** - Track price movements with percentage changes  
- ⏱️ **Rolling window prices** - Get price data for custom time windows
- 🗂️ **Symbol mapping** - Support for common crypto names (btc, eth, etc.)
- 📊 **Activity logging** - In-memory logging for API calls and responses
- ☁️ **Cloud-ready** - Zero local file dependencies for containerized deployments

## Supported Cryptocurrencies

The server supports common cryptocurrency symbols including:
- Bitcoin (btc, bitcoin → BTCUSDT)
- Ethereum (eth, ethereum → ETHUSDT) 
- Solana (sol, solana → SOLUSDT)
- Dogecoin (doge → DOGEUSDT)
- And many more...

## Installation

1. **Install Python 3.11+** (recommended: use UV for version management)
2. **Install dependencies:**
   ```bash
   uv sync
   # or
   pip install -r requirements.txt
   ```

## Running the Server

### Option 1: Streamable HTTP (Recommended for Web/Cloud)

```bash
python binance_mcp/binance_mcp_sse.py
```

This starts the server at: `http://127.0.0.1:8897/mcp/`

**Features:**
- ✅ Perfect for cloud deployment
- ✅ Web-accessible via HTTP
- ✅ Supports real-time bidirectional streaming
- ✅ No local file dependencies

### Option 2: STDIO (For Local/Desktop Clients)

Modify the server file to use STDIO transport:

```python
if __name__ == "__main__":
    mcp.run(transport="stdio")
```

**Features:**
- ✅ Compatible with Claude Desktop
- ✅ Direct process communication
- ✅ Lower latency for local clients

### Option 3: SSE (Legacy Support)

For legacy SSE support, modify the server:

```python
if __name__ == "__main__":
    mcp.run(transport="sse", host="127.0.0.1", port=8897)
```

Access at: `http://127.0.0.1:8897/sse/`

## Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `get_price` | Get current price of a cryptocurrency | `symbol: str` |
| `get_price_24hr_change` | Get 24-hour price change data | `symbol: str` |
| `get_rolling_windows_price` | Get price data for custom time windows | `symbol: str, window: str` |
| `get_recent_logs` | Get recent API activity logs | `limit: int (1-100)` |

## Available Resources

| Resource | Description |
|----------|-------------|
| `memory://symbol_map` | CSV mapping of crypto names to symbols |
| `memory://activity_log` | Real-time activity logs from API calls |

## Inspecting the MCP Server

### Method 1: MCP Inspector (Node.js)

For **HTTP/SSE servers**:
```bash
npx @modelcontextprotocol/inspector
```
Then connect to: `http://127.0.0.1:8897/mcp/`

For **STDIO servers**:
```bash
npx @modelcontextprotocol/inspector python binance_mcp/binance_mcp_sse.py
```

### Method 2: FastMCP Dev Command

```bash
fastmcp dev binance_mcp/binance_mcp_sse.py
```

This launches the FastMCP development inspector with auto-reload.

### Method 3: MCP CLI (Legacy)

```bash
mcp dev binance_mcp/binance_mcp_sse.py
```

## Usage Examples

### With FastMCP Client (Python)

```python
import asyncio
from fastmcp import Client

async def get_crypto_prices():
    async with Client("http://127.0.0.1:8897/mcp/") as client:
        # Get Bitcoin price
        btc_price = await client.call_tool("get_price", {"symbol": "btc"})
        print(f"Bitcoin: {btc_price.content[0].text}")
        
        # Get 24hr change for Ethereum
        eth_change = await client.call_tool("get_price_24hr_change", {"symbol": "eth"})
        print(f"Ethereum 24h: {eth_change.content[0].text}")
        
        # Check recent activity
        logs = await client.call_tool("get_recent_logs", {"limit": 5})
        print(f"Recent activity:\n{logs.content[0].text}")

asyncio.run(get_crypto_prices())
```

### With Claude Desktop

Add to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "binance-crypto": {
      "command": "python",
      "args": ["path/to/binance_mcp/binance_mcp_sse.py"],
      "env": {}
    }
  }
}
```

### With HTTP Clients (cURL)

```bash
# Test server connectivity
curl -X POST http://127.0.0.1:8897/mcp/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "ping"}'
```

## Architecture

- **Transport Layer**: FastMCP with Streamable HTTP
- **Data Source**: Binance US API
- **Storage**: In-memory (no local files for cloud compatibility)
- **Logging**: Circular buffer with 1000-entry limit
- **Symbol Resolution**: Built-in mapping for common crypto names

## Development

### Getting Python Path

- **macOS/Linux**: `which python`
- **Windows**: `(Get-Command python).Path -replace '\\', '/'`

### Environment Setup

```bash
# Using UV (recommended)
uv python install 3.11.13
uv venv --python 3.11.13
uv sync

# Using pip
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## Deployment

The server is optimized for cloud deployment:

- ✅ **No local file dependencies**
- ✅ **Stateless operation** 
- ✅ **Container-ready**
- ✅ **Memory-efficient logging**
- ✅ **Environment variable support**

Deploy to any platform that supports Python web applications:
- Docker containers
- Cloud Run
- Heroku
- Railway
- Fly.io

## API Reference

### Window Formats for `get_rolling_windows_price`

- **Minutes**: `1m`, `2m`, ..., `59m`
- **Hours**: `1h`, `2h`, ..., `23h`  
- **Days**: `1d`, `2d`, ..., `7d`

### Symbol Resolution

The server automatically converts common names:
- `btc`, `bitcoin` → `BTCUSDT`
- `eth`, `ethereum` → `ETHUSDT`
- `sol`, `solana` → `SOLUSDT`
- Or pass exact Binance symbols directly

## Troubleshooting

### Server Won't Start
- Check Python version (3.11+ required)
- Verify all dependencies installed: `uv sync`
- Check port 8897 is available

### Connection Issues  
- Ensure server is running: `curl http://127.0.0.1:8897/mcp/`
- Check firewall settings
- Verify correct transport (HTTP vs STDIO)

### API Errors
- Check recent logs: Use `get_recent_logs` tool
- Verify Binance API is accessible
- Check symbol formatting (use `memory://symbol_map` resource)

## Links

- [FastMCP Documentation](https://gofastmcp.com)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [Binance US API Documentation](https://docs.binance.us)
- [Official Python MCP SDK](https://github.com/modelcontextprotocol/python-sdk)
