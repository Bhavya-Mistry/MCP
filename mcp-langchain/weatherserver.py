from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather")


@mcp.tool()
def get_weather(location: str) -> str:
    """Get the weather location"""
    return "It's always raining in california"


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
