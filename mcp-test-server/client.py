import asyncio
from icecream import ic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():

    server = StdioServerParameters(command="python", args=["server.py"])

    # This block of code is using asynchronous context managers in Python to interact with a server
    # through standard input and output (stdio) communication.
    # Below line does two things: 1. Starts server.py    2. Opens pipes:
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:  # MCP connection established
            await session.initialize()  # Handshake between client and server.

            tools_result = await session.list_tools()

            print("-" * 50)
            ic(tools_result.tools)
            print("-" * 50)

            ic("Tools available are:")

            for tool in tools_result.tools:
                ic(tool.name)

            # add_result = await session.call_tool("add", {"a": 10, "b": 5})
            # multiply_result = await session.call_tool("multiply", {"a": 10, "b": 20})
            result = await session.call_tool("multiply", {"a": 10, "b": 20})

            ic("Add:", result.content[0].text)
            ic("Multiply:", result.content[0].text)
            print("-" * 50)
            ic("DEBUG:", result)
            print("-" * 50)
            ic("DEBUG:", result.content)
            print("-" * 50)


asyncio.run(main())
