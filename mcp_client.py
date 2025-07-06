from pathlib import Path
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

ROOT_FOLDER = Path(__file__).parent.absolute()
MCP_FOLDER = ROOT_FOLDER / "binance_mcp"

server_parameters = StdioServerParameters(
    command="python",
    args=[str(MCP_FOLDER / "binance_mcp.py")],
    env=None,
)


# create a client session
# 비동기: 기다리는 동안 다른 일 하기
# await: 이 작업이 끝날 때까지 기다려, 그 동안 다른 일 해도 돼.
# async: 이 함수는 기다리는 시간이 있어서 다른 일과 동시에 할 수 있어.
async def run():
    async with stdio_client(server_parameters) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # tools = await session.list_tools()
            # print(tools)
            result = await session.call_tool(
                name="get_price",
                arguments={"symbol": "BTCUSDT"},
            )
            # print(result)
            print(result.content[0].text)


if __name__ == "__main__":
    import asyncio

    asyncio.run(run())
