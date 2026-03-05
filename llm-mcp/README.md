# AI Tool Executor Flow

This project demonstrates how a user prompt is processed by a language model (LLM), interpreted as a tool call, and executed asynchronously via a session.

---

## Full Execution Flow

```text
[User Input]
  └─> user_prompt = input("User: ")

             │
             ▼
[Prepare System Prompt]
  └─> system_prompt includes:
        - Instructions for AI
        - JSON-only tool response format
        - Available tools and schemas

             │
             ▼
[Call LLM API]
  └─> response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0
      )

             │
             ▼
[Extract Assistant Message]
  └─> message = response.choices[0].message.content
        - This is a string
        - Expected JSON if a tool is needed
        - Example:
          {
            "tool": "add",
            "arguments": {"a":5, "b":3}
          }

             │
             ▼
[Parse JSON to Dict]
  └─> tool_call = json.loads(message)
        - tool_call["tool"] → "add"
        - tool_call["arguments"] → {"a": 5, "b": 3}

             │
             ▼
[Extract Tool Info]
  └─> tool_name = tool_call["tool"]
  └─> arguments = tool_call["arguments"]

             │
             ▼
[Call Tool via Session]
  └─> result = await session.call_tool(tool_name, arguments)
        - session calls the registered tool
        - tool executes with given arguments
        - returns a response object:
          result.content[0].text → "8" (example)

             │
             ▼
[Display Tool Result]
  └─> ic("\nTool Result:")
  └─> ic(result.content[0].text)
        - Prints the result of the tool execution to console
```
