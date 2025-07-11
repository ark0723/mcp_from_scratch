# TypeScript MCP Binance Server

This project implements a Model Context Protocol (MCP) server in TypeScript that provides Binance cryptocurrency price data. It's a TypeScript port of the Python `binance_mcp.py` implementation.

## Features

### Tools
- `get_price` - Get current price of a cryptocurrency
- `get_price_24hr_change` - Get 24-hour price change data
- `get_rolling_windows_price` - Get rolling window price data (1m-59m, 1h-23h, 1d-7d)

### Resources
- `file://activity.log` - Server activity log
- `file://symbol_map.csv` - Cryptocurrency symbol mappings
- `resource://crypto_price/{symbol}` - Dynamic price resource

### Prompts
- `executive_summary` - Get executive summary for Bitcoin and Ethereum
- `crypto_summary` - Get summary for multiple cryptocurrencies

## Project Structure

```
typescript_mcp/
├── src/
│   ├── binance_mcp.ts      # Main MCP server implementation
│   └── price_graph.ts      # LangGraph integration (simplified)
├── dist/                   # Compiled JavaScript output
├── package.json           # Node.js dependencies and scripts
├── tsconfig.json          # TypeScript configuration
├── activity.log           # Server activity log (created at runtime)
├── symbol_map.csv         # Cryptocurrency mappings (created at runtime)
└── README.md              # This file
```

## Installation

1. Install Node.js (version 16 or higher)
2. Install dependencies:
   ```bash
   npm install
   ```

## Building

Compile TypeScript to JavaScript:
```bash
npm run build
```

## Usage

### Running the MCP Server

```bash
# Build and start the server
npm run dev

# Or run the compiled version directly
npm start
```

### Running the Price Graph Client

```bash
npm run price-graph
```

## Cryptocurrency Symbol Mappings

The server automatically creates a `symbol_map.csv` file with mappings for common cryptocurrencies:

- `btc`, `bitcoin` → `BTCUSDT`
- `eth`, `ethereum` → `ETHUSDT`
- `sol`, `solana` → `SOLUSDT`
- `doge` → `DOGEUSDT`
- And many more...

## API Endpoints

The server uses Binance US API endpoints:
- Price: `https://api.binance.us/api/v3/ticker/price`
- 24hr Change: `https://api.binance.us/api/v3/ticker/24hr`
- Rolling Windows: `https://api.binance.us/api/v3/ticker`

## Configuration

### TypeScript Configuration

The project uses modern TypeScript configuration:
- **Target**: ES2022 (modern JavaScript features)
- **Module**: Node16 (Node.js module system)
- **Strict**: Enabled (strong type checking)
- **Output**: `dist/` directory

### Package Configuration

- **Main Entry**: `dist/binance_mcp.js`
- **Executable**: Can be run as a command-line tool
- **Dependencies**: MCP SDK, Zod for validation

## Comparison with Python Implementation

This TypeScript implementation provides equivalent functionality to the Python version:

| Feature | Python | TypeScript |
|---------|--------|------------|
| MCP Server | ✅ FastMCP | ✅ MCP SDK |
| Tools | ✅ 3 tools | ✅ 3 tools |
| Resources | ✅ 3 resources | ✅ 3 resources |
| Prompts | ✅ 2 prompts | ✅ 2 prompts |
| Symbol Mapping | ✅ CSV-based | ✅ CSV-based |
| Logging | ✅ File-based | ✅ File-based |
| Error Handling | ✅ Comprehensive | ✅ Comprehensive |

## Development Notes

### Type Safety
- Uses Zod for runtime type validation
- Strict TypeScript configuration
- Proper error handling with typed exceptions

### Module System
- ES Modules with Node.js compatibility
- Proper import/export patterns
- JSON module support for package.json

### File Operations
- Cross-platform path handling
- Synchronous file operations for simplicity
- Automatic file creation (logs, symbol map)

## Dependencies

### Runtime Dependencies
- `@modelcontextprotocol/sdk` - MCP server functionality
- `zod` - Runtime type validation

### Development Dependencies
- `typescript` - TypeScript compiler
- `@types/node` - Node.js type definitions

## LangGraph Integration

The `price_graph.ts` file provides a simplified structure for LangGraph integration. For full functionality, you would need to add:

```bash
# Additional dependencies for full LangGraph support
npm install @langchain/core @langchain/community
```

## Error Handling

The server includes comprehensive error handling:
- API request failures are logged and re-thrown
- File operation errors are caught and logged
- Server startup errors exit gracefully

## Logging

All server activities are logged to `activity.log`:
- Successful price retrievals
- API errors
- Symbol mapping errors
- Timestamps for all activities

## License

MIT License - feel free to use and modify as needed.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run `npm run build` to ensure compilation
5. Submit a pull request

## Troubleshooting

### Common Issues

1. **Module not found errors**: Run `npm install` to install dependencies
2. **Compilation errors**: Check TypeScript configuration in `tsconfig.json`
3. **API errors**: Verify internet connection and Binance API availability
4. **File permission errors**: Ensure write permissions for log and CSV files

### Debug Mode

To see detailed server logs, the server outputs debug information to stderr:
```bash
npm run dev 2> debug.log
``` 