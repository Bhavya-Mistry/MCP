import os
import smtplib
from email.message import EmailMessage
from github import Github
import os

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
        print("Error: ", e)


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
        print("Error: ", e)


@mcp.tool()
def commit_file(branch: str, file_path: str, content: str, message: str) -> str:
    """Create or update a file in a branch"""

    try:
        contents = repo.get_contents(file_path, ref=branch)

        repo.update_file(
            path=file_path,
            message=message,
            content=content,
            sha=contents.sha,
            branch=branch,
        )

        return f"Updated {file_path} in {branch}"

    except Exception as e:
        print("Error: ", e)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
