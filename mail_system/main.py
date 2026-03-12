import os
import smtplib
from email.message import EmailMessage
from github import Github, GithubException

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

mcp = FastMCP("Mail Server")

MAIL_ACCOUNT = os.getenv("MAIL_ACCOUNT")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))


@mcp.tool()
def send_mail(to: str, subject: str, body: str) -> str:
    """Send and email"""
    try:
        msg = EmailMessage()
        msg["FROM"] = MAIL_ACCOUNT
        msg["TO"] = to
        msg["SUBJECT"] = subject
        msg.set_content(body)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(MAIL_ACCOUNT, MAIL_PASSWORD)
            server.send_message(msg)

        return "SUCCESS"

    except Exception as e:
        return f"Failed due to {e}"


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
g = Github(GITHUB_TOKEN)
repo_name = "Bhavya-Mistry/MCP"
repo = g.get_repo(repo_name)


@mcp.tool()
def create_branch(base_branch: str, new_branch: str) -> str:
    """
    Create a new Branch in a Github repository
    """
    try:
        base_repo = repo.get_branch(base_branch)
        sha = base_repo.commit.sha

        repo.create_git_ref(ref=f"refs/heads/{new_branch}", sha=sha)

        return f"SUCCESS, Branch '{new_branch}' created from '{base_branch}' in {repo_name}"

    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def create_pull_request(
    base_branch: str, head_branch: str, title: str, body: str
) -> str:
    """Create a pull request that merges head_branch into base_branch"""

    try:
        pr = repo.create_pull(
            base=base_branch, head=head_branch, title=title, body=body
        )

        return f"SUCCESS, PR #{pr.number} created from {head_branch} to {base_branch}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def commit_file(branch: str, file_path: str, content: str, message: str) -> str:
    """Create or update a file in a branch"""

    try:
        try:
            contents = repo.get_contents(file_path, ref=branch)
            # File exists — update it
            repo.update_file(
                path=file_path,
                message=message,
                content=content,
                sha=contents.sha,
                branch=branch,
            )
            return f"Updated {file_path} in {branch}"
        except GithubException as e:
            if e.status == 404:
                # File does not exist — create it
                repo.create_file(
                    path=file_path,
                    message=message,
                    content=content,
                    branch=branch,
                )
                return f"Created {file_path} in {branch}"
            raise

    except Exception as e:
        return f"Error: {e}"


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
