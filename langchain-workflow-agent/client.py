from langchain_groq import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from icecream import ic

from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

API_KEY = os.getenv("API_KEY")


async def main():
    client = MultiServerMCPClient(
        {
            "myServer": {
                "url": "http://127.0.0.1:8000/mcp",
                "transport": "streamable_http",
            }
        }
    )

    tools = await client.get_tools()

    model = ChatGroq(model="openai/gpt-oss-20b", api_key=API_KEY)

    agent = create_agent(model, tools, system_prompt="MAKE SURE TO USE AVAILABLE TOOLS")

    print("Type 'exit' to quit")

    while True:
        user_prompt = input("User: \n")
        print("\n")

        if user_prompt.lower() == "exit":
            break

        try:
            response = await agent.ainvoke(
                {
                    "messages": [
                        {
                            "role": "User",
                            "content": user_prompt,
                        }
                    ]
                }
            )

            print("Agent: \n", response["messages"][-1].content)

        except Exception as e:
            ic(e)


asyncio.run(main())
