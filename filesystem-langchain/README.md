# 🤖 LangChain MCP Agent

A modular AI agent system that connects a **LangChain-powered LLM** to an **MCP (Model Context Protocol) tool server** via streamable HTTP. The agent discovers available tools at runtime and uses them to respond to user prompts; no hardcoded tool logic in the client.



## 📐 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT SIDE                          │
│                                                             │
│   [User Input]                                              │
│       └─> agent.ainvoke({"messages": [...]})                │
│                    │                                        │
│                    ▼                                        │
│   [LangChain Agent]                                         │
│       └─> model: ChatGroq (openai/gpt-oss-20b)              │
│       └─> tools: fetched dynamically from MCP server        │
│       └─> system_prompt                                     │
│                    │                                        │
│                    ▼                                        │
│   [MultiServerMCPClient]                                    │
│       └─> transport: streamable_http                        │
│       └─> url: http://127.0.0.1:8000/mcp                    │
└────────────────────┬────────────────────────────────────────┘
                     │  HTTP (Streamable MCP Protocol)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                        SERVER SIDE                          │
│                                                             │
│   [FastMCP Server]  ← mcp.run(transport="streamable-http")  │
│       │                                                     │
│       ├─> add(a, b)                   → returns int         │
│       ├─> multiply(a, b)              → returns int         │
│       ├─> list_files(dir)             → returns str         │
│       ├─> read_files(path)            → returns str         │
│       ├─> file_info(path)             → returns dict        │
│       └─> search_files(dir, keyword)  → returns dict        │
└─────────────────────────────────────────────────────────────┘
```



## 🔄 Full Execution Flow

```
[User Input]
  └─> Prompt is read from the terminal

             │
             ▼
[Tool Discovery]
  └─> Client connects to the MCP server over streamable HTTP
  └─> All tools are fetched dynamically with their schemas
  └─> No tools are hardcoded on the client side

             │
             ▼
[Agent Construction]
  └─> A ChatGroq model is loaded with the API key
  └─> The agent is assembled with the model, discovered tools, and a system prompt
  └─> System prompt restricts the agent to tool-only responses

             │
             ▼
[Agent Invocation]
  └─> The user prompt is passed to the agent as a message
  └─> The LLM selects the appropriate tool based on intent
  └─> Tool arguments are inferred automatically from the prompt

             │
             ▼
[MCP Tool Execution — Server Side]
  └─> FastMCP receives the tool name and arguments over HTTP
  └─> The matching Python function is executed
  └─> The result is streamed back to the agent

             │
             ▼
[Display to User]
  └─> The final message from the agent is printed to the terminal
```

## 🛠️ Available Tools

All tools are registered on the **FastMCP server** and exposed over `streamable-http`:

| Tool | Signature | Description |
|------|-----------|-------------|
| `add` | `add(a: int, b: int) -> int` | Add two integers |
| `multiply` | `multiply(a: int, b: int) -> int` | Multiply two integers |
| `list_files` | `list_files(directory: str) -> str` | List all files in a directory |
| `read_files` | `read_files(path: str) -> str` | Read the full contents of a file |
| `file_info` | `file_info(path: str) -> dict` | Get metadata: size, type, last modified |
| `search_files` | `search_files(directory: str, keyword: str) -> dict` | Search files for a keyword match |



## 📁 Project Structure

```
project/
│
├── client.py          # LangChain agent + MCP client
├── server.py          # FastMCP tool server
├── .env               # API keys (not committed)
├── requirements.txt   # Dependencies
└── README.md
```

> You can skip this setup phase if you have **Claude Desktop** installed in your system

## ⚙️ Setup

### 1. Install dependencies

```bash
uv add -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file in the project root:

```env
API_KEY=your_groq_api_key_here
```

## 🚀 Running the Project

### Step 1 — Start the MCP server

```bash
uv run server.py
```

The server starts at `http://127.0.0.1:8000/mcp` using the `streamable-http` transport.

```
[FastMCP] Server running on http://127.0.0.1:8000/mcp
```

### Step 2 — Start the agent client

In a separate terminal:

```bash
uv run client.py
```

You'll see tool discovery output, then an interactive prompt:

```
User:
```

### Step 3 — Chat with the agent

```
Type `exit` to quit.
User:
add 17 and 25

Agent: 42

User:
list the files in /tmp

Agent: file1.txt
       notes.md
       script.py

User:
exit
```

## 🖥️ Alternative Way — Use with Claude Desktop

You can skip the client entirely and connect the MCP server directly to **Claude Desktop**.

From the project root, run:

```bash
uv run mcp install server.py
```

```
[Install Command]
  └─> Registers server.py as an MCP server in Claude's config file
  └─> All tools are made available to Claude Desktop automatically

             │
             ▼
[Restart Claude Desktop]
  └─> Claude reads the updated config on launch
  └─> Tools from server.py are discovered and loaded

             │
             ▼
[Chat with Claude]
  └─> Claude uses the tools natively — no terminal or client.py needed
  └─> Same tools, same results
```

> This is the quickest way to use the server if you already have Claude Desktop installed.

