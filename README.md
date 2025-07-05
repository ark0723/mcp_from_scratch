## Implementing Your Own MCP Server
* [Official Python MCP Docs](https://github.com/modelcontextprotocol/python-sdk)

### Getting The Python Interpreter's path
* On a Max/Linux: `which python`
* On Window: `(Get-Command python).Path | -replace '\\', '/'`

### Launching the MCP inspector
```
npx @modelcontextprotocol/inspector <<PATH OF PYTHON>> <<PATH OF YOUR binance_mcp.py>>
```
or 
```
mcp dev <<PATH OF YOUR binance_mcp.py>>
```
