import asyncio
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

import os
from pydantic import SecretStr

# load .env file
load_dotenv(verbose=True)

# Get API key and validate it exists
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

# temperature: 0.0 ~ 1.0
model = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.0,
    api_key=SecretStr(api_key),
)


ROOT_FOLDER = Path(__file__).parent.parent.absolute()
MCP_PATH = str(ROOT_FOLDER / "binance_mcp" / "binance_mcp.py")

mcp_config = {
    "binance": {
        "command": "python",
        "args": [MCP_PATH],
        "transport": "stdio",
    }
}


async def get_crypto_price():
    async with MultiServerMCPClient(mcp_config) as client:
        tools = client.get_tools()
        agent = create_react_agent(model=model, tools=tools)
        # create a message
        question = f"What are the current price of Bitcoin and Ethereum?"
        messages = HumanMessage(content=question)
        # send the message to the model and get the response
        response = await agent.ainvoke({"messages": [messages]})
        answer = response["messages"][-1].content
        return answer


if __name__ == "__main__":
    response = asyncio.run(get_crypto_price())
    print(response)
