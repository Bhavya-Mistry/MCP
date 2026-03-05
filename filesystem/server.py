from mcp.server.fastmcp import FastMCP
import os

mcp = FastMCP("filesystem")


@mcp.tool()
def list_files(directory: str) -> str:
    """Lists files in the directory"""
    files = os.listdir(directory)
    return "\n".join(files)


@mcp.tool()
def read_files(path: str) -> str:
    """Read contents of a file"""
    with open(path, "r") as f:
        return f.read()


if __name__ == "__main__":
    mcp.run()
