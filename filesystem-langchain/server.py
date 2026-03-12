from mcp.server.fastmcp import FastMCP
import os

mcp = FastMCP("llm-server")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiple two numbers"""
    return a * b


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


@mcp.tool()
def file_info(path: str) -> dict:
    """Returns metadata/information about a file"""

    stat = os.stat(path)

    return {
        "size_bytes": stat.st_size,
        "is_directory": os.path.isdir(path),
        "last_modified": stat.st_mtime,
    }


@mcp.tool()
def search_files(directory: str, keyword: str) -> dict:
    """Search files in a directory and all subdirectories for a keyword"""
    matches = []

    if not os.path.exists(directory):
        return {"error": "directory does not exist"}

    for root, dirs, files in os.walk(directory):
        for file in files:
            path = os.path.join(root, file)

            try:
                with open(path, "r", errors="ignore") as f:
                    content = f.read()

                if keyword in content:
                    matches.append(path)  # returning full path is better
            except Exception:
                pass  # skip unreadable files

    return {"matches": matches}


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
    # mcp.run(transport="stdio")
