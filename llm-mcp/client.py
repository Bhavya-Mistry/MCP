import asyncio
import json
from groq import Groq
from icecream import ic

import os
from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


load_dotenv()
client = Groq(api_key=os.getenv("API_KEY"))


async def main():
    server = StdioServerParameters(command="python", args=["server.py"])

    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools_result = await session.list_tools()

            tools = []

            for tool in tools_result.tools:
                tools.append(
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "input_schema": tool.inputSchema,
                    }
                )
            ic("Available Tools:", [t["name"] for t in tools])

            while True:
                user_prompt = input("\nUser:")

                if user_prompt.lower() == "exit":
                    break

                tool_descriptions = json.dumps(tools, indent=2)

                system_prompt = f"""
                You are an AI agent that can use tools.
                If no suitable tool exists, do NOT call any tool.
                Respond with a message explaining the limitation.

                Available tools:
                {tool_descriptions}

                If a tool is needed, respond ONLY with JSON:

                {{
                  "tool": "tool_name",
                  "arguments": {{ }}
                }}

                Do not explain anything.
                """

                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0,
                )

                message = response.choices[0].message.content

                ic(message)

                tool_call = json.loads(message)

                tool_name = tool_call["tool"]
                arguments = tool_call["arguments"]

                result = await session.call_tool(tool_name, arguments)

                ic("\nTool Result:")
                ic(result.content[0].text)


asyncio.run(main())
