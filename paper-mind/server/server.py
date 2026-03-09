from mcp.server.fastmcp import FastMCP

mcp = FastMCP("PaperMind MCP Powered Research Assistant")

from tools import *

if __name__=="__main__":
    mcp.run()