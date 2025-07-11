#!/usr/bin/env node

// TypeScript MCP server implementation based on Python binance_mcp.py
import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import fs from "fs";
import path from "path";

// Import version from package.json
const { version } = require("../package.json");

// File paths
const BASE_FOLDER = path.dirname(__dirname);
const ACTIVITY_LOG_FILE = path.join(BASE_FOLDER, "activity.log");
const SYMBOL_MAP_FILE = path.join(BASE_FOLDER, "symbol_map.csv");

// Symbol cache for performance
let symbolCache: { [key: string]: string } | null = null;

// Symbol mappings initialization data
const SYMBOL_MAPPINGS = [
    ["btc", "BTCUSDT"],
    ["bitcoin", "BTCUSDT"],
    ["eth", "ETHUSDT"],
    ["ethereum", "ETHUSDT"],
    ["sol", "SOLUSDT"],
    ["solana", "SOLUSDT"],
    ["doge", "DOGEUSDT"],
    ["shiba", "SHIBUSDT"],
    ["xrp", "XRPUSDT"],
    ["ada", "ADAUSDT"],
    ["dot", "DOTUSDT"],
    ["link", "LINKUSDT"],
    ["ltc", "LTCUSDT"],
    ["xlm", "XLMUSDT"],
    ["eos", "EOSUSDT"],
    ["bnb", "BNBUSDT"],
    ["matic", "MATICUSDT"],
    ["avax", "AVAXUSDT"],
    ["algo", "ALGOUSDT"],
    ["ftt", "FTTUSDT"],
    ["mana", "MANAUSDT"],
    ["uni", "UNIUSDT"],
    ["xmr", "XMRUSDT"],
    ["xem", "XEMUSDT"],
];

// Initialize files
function initializeFiles(): void {
    // Create log file if it doesn't exist
    if (!fs.existsSync(ACTIVITY_LOG_FILE)) {
        fs.writeFileSync(ACTIVITY_LOG_FILE, "");
    }

    // Create symbol map file if it doesn't exist
    if (!fs.existsSync(SYMBOL_MAP_FILE)) {
        let csvContent = "crypto_name,symbol\n";
        for (const [cryptoName, symbol] of SYMBOL_MAPPINGS) {
            csvContent += `${cryptoName},${symbol}\n`;
        }
        fs.writeFileSync(SYMBOL_MAP_FILE, csvContent);
    }
}

// Load symbol mappings with caching
function loadSymbolMappings(): { [key: string]: string } {
    if (symbolCache !== null) {
        return symbolCache;
    }

    symbolCache = {};

    if (fs.existsSync(SYMBOL_MAP_FILE)) {
        try {
            const csvContent = fs.readFileSync(SYMBOL_MAP_FILE, "utf-8");
            const lines = csvContent.split("\n");
            
            // Skip header line
            for (let i = 1; i < lines.length; i++) {
                const line = lines[i].trim();
                if (line) {
                    const [cryptoName, symbol] = line.split(",");
                    if (cryptoName && symbol) {
                        symbolCache[cryptoName.toLowerCase()] = symbol;
                    }
                }
            }
        } catch (error) {
            const errorMessage = `${new Date().toISOString()}: Error reading symbol_map.csv: ${error}\n`;
            fs.appendFileSync(ACTIVITY_LOG_FILE, errorMessage);
        }
    }

    return symbolCache;
}

// Get symbol from input name
function getSymbolFromInput(name: string): string {
    const symbolMappings = loadSymbolMappings();
    
    if (name.toLowerCase() in symbolMappings) {
        return symbolMappings[name.toLowerCase()];
    } else {
        return name.toUpperCase();
    }
}

// Create MCP server instance
const server = new McpServer({
    name: "Binance MCP TypeScript",
    version
});

// Tool: get_price
server.tool(
    "get_price",
    { symbol: z.string() },
    async ({ symbol }) => {
        const resolvedSymbol = getSymbolFromInput(symbol);
        const url = `https://api.binance.us/api/v3/ticker/price?symbol=${resolvedSymbol}`;
        
        try {
            const response = await fetch(url);
            if (!response.ok) {
                const errorText = await response.text();
                const errorMessage = `${new Date().toISOString()}: Error getting price for ${resolvedSymbol}: ${response.status} ${errorText}\n`;
                fs.appendFileSync(ACTIVITY_LOG_FILE, errorMessage);
                throw new Error(`Error getting price for ${resolvedSymbol}: ${response.status} ${errorText}`);
            }

            const data = await response.json() as any;
            const price = data.price;
            
            const successMessage = `${new Date().toISOString()}: Successfully got the current price for ${resolvedSymbol}: ${price}\n`;
            fs.appendFileSync(ACTIVITY_LOG_FILE, successMessage);
            
            return {
                content: [{
                    type: "text",
                    text: `The current price of ${resolvedSymbol} is ${price}`
                }]
            };
        } catch (error) {
            const errorMessage = `${new Date().toISOString()}: Error in get_price for ${resolvedSymbol}: ${error}\n`;
            fs.appendFileSync(ACTIVITY_LOG_FILE, errorMessage);
            throw error;
        }
    }
);

// Tool: get_price_24hr_change
server.tool(
    "get_price_24hr_change",
    { symbol: z.string() },
    async ({ symbol }) => {
        const resolvedSymbol = getSymbolFromInput(symbol);
        const url = `https://api.binance.us/api/v3/ticker/24hr?symbol=${resolvedSymbol}`;
        
        try {
            const response = await fetch(url);
            if (!response.ok) {
                const errorText = await response.text();
                const errorMessage = `${new Date().toISOString()}: Error getting price change for ${resolvedSymbol}: ${response.status} ${errorText}\n`;
                fs.appendFileSync(ACTIVITY_LOG_FILE, errorMessage);
                throw new Error(`Error getting price change for ${resolvedSymbol}: ${response.status} ${errorText}`);
            }

            const data = await response.json() as any;
            const priceChange = data.priceChange;
            const priceChangePercent = data.priceChangePercent;
            
            const successMessage = `${new Date().toISOString()}: Successfully got the price change for ${resolvedSymbol}: ${priceChange} (${priceChangePercent}%)\n`;
            fs.appendFileSync(ACTIVITY_LOG_FILE, successMessage);
            
            return {
                content: [{
                    type: "text",
                    text: JSON.stringify(data)
                }]
            };
        } catch (error) {
            const errorMessage = `${new Date().toISOString()}: Error in get_price_24hr_change for ${resolvedSymbol}: ${error}\n`;
            fs.appendFileSync(ACTIVITY_LOG_FILE, errorMessage);
            throw error;
        }
    }
);

// Tool: get_rolling_windows_price
server.tool(
    "get_rolling_windows_price",
    { 
        symbol: z.string(),
        window: z.string().optional().default("1d")
    },
    async ({ symbol, window }) => {
        const resolvedSymbol = getSymbolFromInput(symbol);
        const url = `https://api.binance.us/api/v3/ticker?symbol=${resolvedSymbol}&windowSize=${window}`;
        
        try {
            const response = await fetch(url);
            if (!response.ok) {
                const errorText = await response.text();
                const errorMessage = `${new Date().toISOString()}: Error getting the price change for ${resolvedSymbol} in the window ${window}: ${response.status} ${errorText}\n`;
                fs.appendFileSync(ACTIVITY_LOG_FILE, errorMessage);
                throw new Error(`Error getting the price change for ${resolvedSymbol} in the window ${window}: ${response.status} ${errorText}`);
            }

            const data = await response.json() as any;
            const priceChange = data.priceChange;
            const priceChangePercent = data.priceChangePercent;
            
            const successMessage = `${new Date().toISOString()}: Successfully got the price change for ${resolvedSymbol} in the window ${window}: ${priceChange} (${priceChangePercent}%)\n`;
            fs.appendFileSync(ACTIVITY_LOG_FILE, successMessage);
            
            return {
                content: [{
                    type: "text",
                    text: JSON.stringify(data)
                }]
            };
        } catch (error) {
            const errorMessage = `${new Date().toISOString()}: Error in get_rolling_windows_price for ${resolvedSymbol}: ${error}\n`;
            fs.appendFileSync(ACTIVITY_LOG_FILE, errorMessage);
            throw error;
        }
    }
);

// Resource: file://symbol_map.csv
server.resource(
    "file://symbol_map.csv",
    new ResourceTemplate("file://symbol_map.csv", { list: undefined }),
    async () => {
        if (!fs.existsSync(SYMBOL_MAP_FILE)) {
            return { contents: [{ uri: "file://symbol_map.csv", text: "" }] };
        }
        const text = fs.readFileSync(SYMBOL_MAP_FILE, "utf-8");
        return { contents: [{ uri: "file://symbol_map.csv", text }] };
    }
);

// Resource: file://activity.log
server.resource(
    "file://activity.log",
    new ResourceTemplate("file://activity.log", { list: undefined }),
    async () => {
        if (!fs.existsSync(ACTIVITY_LOG_FILE)) {
            return { contents: [{ uri: "file://activity.log", text: "" }] };
        }
        const text = fs.readFileSync(ACTIVITY_LOG_FILE, "utf-8");
        return { contents: [{ uri: "file://activity.log", text }] };
    }
);

// Resource: resource://crypto_price/{symbol}
server.resource(
    "resource://crypto_price/{symbol}",
    new ResourceTemplate("resource://crypto_price/{symbol}", { list: undefined }),
    async (uri, variables) => {
        const symbol = variables.symbol as string;
        const resolvedSymbol = getSymbolFromInput(symbol);
        const url = `https://api.binance.us/api/v3/ticker/price?symbol=${resolvedSymbol}`;
        
        try {
            const response = await fetch(url);
            if (!response.ok) {
                return { contents: [{ uri: uri.href, text: `Error getting price for ${resolvedSymbol}` }] };
            }
            const data = await response.json() as any;
            return { contents: [{ uri: uri.href, text: `The current price of ${resolvedSymbol} is ${data.price}` }] };
        } catch (error) {
            return { contents: [{ uri: uri.href, text: `Error getting price for ${resolvedSymbol}: ${error}` }] };
        }
    }
);

// Prompt: executive_summary
server.prompt(
    "executive_summary",
    "Returns an executive summary of Bitcoin and Ethereum",
    {},
    async () => {
        return {
            messages: [{
                role: "user",
                content: {
                    type: "text",
                    text: `Get the prices of the following crypto asset: btc, eth
    
Provide me with an executive summary including the 
two-sentence summary of the crypto asset, the current price, 
the price change in the last 24 hours, and the percentage change
in the last 24 hours.

When using the get_price and get_price_24hr_change tools,
use the symbol as the argument.

Symbols: For bitcoin/btc, the symbol is "BTCUSDT".
Symbols: For ethereum/eth, the symbol is "ETHUSDT".`
                }
            }]
        };
    }
);

// Prompt: crypto_summary
server.prompt(
    "crypto_summary",
    "Return an executive summary of crypto assets (supports multiple assets separated by commas)",
    { cryptos: z.string() },
    async ({ cryptos }) => {
        return {
            messages: [{
                role: "user",
                content: {
                    type: "text",
                    text: `Get the current price of the following crypto assets:
${cryptos}

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

Format the output as a clean summary for each asset.`
                }
            }]
        };
    }
);

// Main server startup function
async function startServer(): Promise<void> {
    // Initialize files
    initializeFiles();
    
    // Create transport and connect
    const transport = new StdioServerTransport();
    await server.connect(transport);
    
    console.error(`Binance MCP TypeScript Server v${version} started`);
    console.error("Tools: get_price, get_price_24hr_change, get_rolling_windows_price");
    console.error("Resources: file://activity.log, file://symbol_map.csv, resource://crypto_price/{symbol}");
    console.error("Prompts: executive_summary, crypto_summary");
}

// Error handling and startup
startServer().catch(err => {
    console.error("Error starting server:", err);
    process.exit(1);
}); 