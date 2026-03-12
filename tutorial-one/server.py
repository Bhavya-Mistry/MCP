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


@mcp.tool()
def file_info(path: str) -> dict:
    """Returns metada about a file"""

    stat = os.stat(path)

    return {
        "size_bytes": stat.st_size,
        "is_directory": os.path.isdir(path),
        "last_modified": stat.st_mtime,
    }


@mcp.tool()
def search_files(directory: str, keyword: str) -> dict:
    """Search files in a directory for a keyword"""
    matches = []

    if not os.path.exists(directory):
        return {"error": "directory does not exist"}

    for file in os.listdir(directory):
        path = os.path.join(directory, file)
        if os.path.isfile(path):
            with open(path, "r", errors="ignore") as f:
                content = f.read()

                if keyword in content:
                    matches.append(file)

    return {"matches": matches}


if __name__ == "__main__":
    mcp.run()
