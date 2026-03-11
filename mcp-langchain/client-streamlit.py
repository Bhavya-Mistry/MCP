import streamlit as st
import asyncio
import os

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_groq import ChatGroq

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

st.title("MCP Agent Chat")

# -------------------------------------------
#   Session State initialization
# -------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent" not in st.session_state:
    st.session_state.agent = None


# -------------------------------------------
#   Async setup
# -------------------------------------------
async def setup_agent():
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

    tools = await client.get_tools()

    model = ChatGroq(model="openai/gpt-oss-20b", api_key=API_KEY)

    agent = create_agent(
        model,
        tools,
        system_prompt="ONLY USE AVAILABLE TOOLS AND REPLY NOTHING ELSE",
    )

    return agent


# -------------------------------------------
#   Load Agent Once
# -------------------------------------------
if st.session_state.agent is None:
    with st.spinner("Initializing Agent"):
        st.session_state.agent = asyncio.run(setup_agent())


# -------------------------------------------
#   Dispaly Chat History
# -------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# -------------------------------------------
#   User Input
# -------------------------------------------
prompt = st.chat_input("Ask Something")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    async def run_agent():
        response = await st.session_state.agent.ainvoke(
            {"messages": [{"role": "user", "content": prompt}]}
        )
        return response["messages"][-1].content

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = asyncio.run(run_agent())
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
