# 🤖 LangChain MCP Agent

A modular AI agent system that connects a **LangChain-powered LLM** to an **MCP (Model Context Protocol) tool server** via streamable HTTP. The agent discovers available tools at runtime and uses them to respond to user prompts — no hardcoded tool logic in the client.

---

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
│       └─> model: ChatGroq (openai/gpt-oss-20b)             │
│       └─> tools: fetched dynamically from MCP server        │
│       └─> system_prompt: "ONLY USE AVAILABLE TOOLS..."      │
│                    │                                        │
│                    ▼                                        │
│   [MultiServerMCPClient]                                    │
│       └─> transport: streamable_http                        │
│       └─> url: http://127.0.0.1:8000/mcp                   │
└────────────────────┬────────────────────────────────────────┘
                     │  HTTP (Streamable MCP Protocol)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                        SERVER SIDE                          │
│                                                             │
│   [FastMCP Server]  ← mcp.run(transport="streamable-http") │
│       │                                                     │
│       ├─> add(a, b)          → returns int                  │
│       ├─> multiply(a, b)     → returns int                  │
│       ├─> list_files(dir)    → returns str                  │
│       ├─> read_files(path)   → returns str                  │
│       ├─> file_info(path)    → returns dict                 │
│       └─> search_files(dir, keyword) → returns dict         │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Full Execution Flow

```
[User Input]
  └─> user_prompt = input("User:\n")

             │
             ▼
[MultiServerMCPClient — Tool Discovery]
  └─> client = MultiServerMCPClient({
        "add":          { url, transport },
        "multiply":     { url, transport },
        "list_files":   { url, transport },
        "read_files":   { url, transport },
        "file_info":    { url, transport },
        "search_files": { url, transport },
      })
  └─> tools = await client.get_tools()
        - Tools are fetched live from the MCP server
        - Each tool includes name, description, and input schema

             │
             ▼
[Agent Construction]
  └─> model = ChatGroq(model="openai/gpt-oss-20b", api_key=API_KEY)
  └─> agent = create_agent(
        model,
        tools,
        system_prompt="ONLY USE AVAILABLE TOOLS AND REPLY NOTHING ELSE"
      )
        - Agent binds model + tools into a ReAct-style executor

             │
             ▼
[Agent Invocation]
  └─> response = await agent.ainvoke({
        "messages": [{"role": "user", "content": user_prompt}]
      })
        - LLM decides which tool to call based on the prompt
        - Tool arguments are inferred from context
        - MCP client routes the call to the server

             │
             ▼
[MCP Tool Execution — Server Side]
  └─> FastMCP receives the tool call over streamable HTTP
  └─> Executes the registered Python function
  └─> Returns result back to the agent

             │
             ▼
[Agent Response]
  └─> response["messages"][-1].content
        - The final message content from the agent
        - Contains the tool result or composed answer

             │
             ▼
[Display to User]
  └─> ic("Agent:", response["messages"][-1].content)
```

---

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

---

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

---

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install langchain-mcp-adapters langchain langchain-groq fastmcp icecream python-dotenv sympy
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
API_KEY=your_groq_api_key_here
```

---

## 🚀 Running the Project

### Step 1 — Start the MCP server

```bash
python server.py
```

The server starts at `http://127.0.0.1:8000/mcp` using the `streamable-http` transport.

```
[FastMCP] Server running on http://127.0.0.1:8000/mcp
```

### Step 2 — Start the agent client

In a separate terminal:

```bash
python client.py
```

You'll see tool discovery output, then an interactive prompt:

```
User:
```

### Step 3 — Chat with the agent

```
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

Type `exit` to quit.

---

## 💡 Example Prompts

| Prompt | Tool Used | Result |
|--------|-----------|--------|
| `add 5 and 3` | `add` | `8` |
| `multiply 6 by 7` | `multiply` | `42` |
| `list files in /home/user/docs` | `list_files` | List of filenames |
| `read the file /tmp/notes.txt` | `read_files` | File contents |
| `get info about /etc/hosts` | `file_info` | `{size_bytes, is_directory, last_modified}` |
| `search /home/user for the word "TODO"` | `search_files` | `{matches: ["todo.txt"]}` |

---

## 🔑 Key Design Decisions

```
[Why MultiServerMCPClient?]
  └─> Each tool key maps to the same server URL
  └─> Allows per-tool routing if servers ever split
  └─> Tools are discovered dynamically — no hardcoding

[Why streamable_http transport?]
  └─> Persistent-friendly, works over standard HTTP
  └─> Compatible with FastMCP's streamable-http mode
  └─> Easy to proxy or deploy behind a gateway

[Why system_prompt = "ONLY USE AVAILABLE TOOLS"?]
  └─> Prevents the LLM from hallucinating free-text answers
  └─> Forces structured, tool-grounded responses only
```

---

## 📦 Requirements

```
langchain
langchain-mcp-adapters
langchain-groq
fastmcp
icecream
python-dotenv
sympy
```

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.