import asyncio
from icecream import ic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():

    server = StdioServerParameters(command="python", args=["server.py"])

    # This block of code is using asynchronous context managers in Python to interact with a server
    # through standard input and output (stdio) communication.
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools_result = await session.list_tools()

            ic("Tools available:")

            for tool in tools_result.tools:
                ic(tool.name)

            result = await session.call_tool("add", {"a": 10, "b": 5})

            ic(result.content[0].text)


asyncio.run(main())
