from mcp.server.fastmcp import FastMCP
import tools

# Create the server instance
mcp = FastMCP("PaperMind Research Assistant")

# Register the tools from tools.py
tools.register_tools(mcp)

if __name__ == "__main__":
    mcp.run()