from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from icecream import ic

from dotenv import load_dotenv
import os
import asyncio

from sympy import true

load_dotenv()

API_KEY = os.getenv("API_KEY")


async def main():
    client = MultiServerMCPClient(
        {
            "add": {
                "url": "http://127.0.0.1:8000/mcp",
                "transport": "streamable_http",
            },
            "multiply": {
                "url": "http://127.0.0.1:8000/mcp",
                "transport": "streamable_http",
            },
            "list_files": {
                "url": "http://127.0.0.1:8000/mcp",
                "transport": "streamable_http",
            },
            "read_files": {
                "url": "http://127.0.0.1:8000/mcp",
                "transport": "streamable_http",
            },
            "file_info": {
                "url": "http://127.0.0.1:8000/mcp",
                "transport": "streamable_http",
            },
            "search_files": {
                "url": "http://127.0.0.1:8000/mcp",
                "transport": "streamable_http",
            },
        }
    )

    tools = await client.get_tools()
    ic(tools)
    print("_" * 80)

    model = ChatGroq(model="openai/gpt-oss-20b", api_key=API_KEY)
    ic(model)
    print("_" * 80)

    agent = create_agent(
        model, tools, system_prompt="ONLY USE AVAILABLE TOOLS AND REPLY NOTHING ELSE"
    )
    ic(agent)
    print("_" * 80)

    ic("Enter EXIT to quit")

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
