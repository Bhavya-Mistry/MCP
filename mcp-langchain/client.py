from ast import arg
from langchain_core.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from icecream import ic

from dotenv import load_dotenv
from langsmith import expect

load_dotenv()

import asyncio


async def main():
    client = MultiServerMCPClient(
        {
            "math": {
                "command": "python",
                "args": ["mathserver.py"],
                "transport": "stdio",
            },
            "weather": {
                "url": "http://127.0.0.1:8000/mcp",
                "transport": "streamable_http",
            },
        }
    )

    import os

    api_key = os.getenv("API_KEY")

    tools = await client.get_tools()
    ic(tools)
    print("-" * 90)

    model = ChatGroq(
        model="openai/gpt-oss-20b",
        api_key=api_key,
    )
    ic(model)
    print("-" * 50)

    agent = create_agent(
        model,
        tools,
        system_prompt="ONLY USE AVAILABLE TOOLS AND REPLY NOTHING ELSE",
    )
    ic(agent)
    print("-" * 90)

    ic("Enter exit to quit")

    while True:
        user_prompt = input("User:\n")

        if user_prompt.lower() == "exit":
            break

        try:
            response = await agent.ainvoke(
                {"messages": [{"role": "user", "content": user_prompt}]}
            )

            ic("Agent:", response["messages"][-1].content)

        except Exception as e:
            ic(e)


asyncio.run(main())
