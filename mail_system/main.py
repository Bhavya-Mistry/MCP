import os
import smtplib
from email.message import EmailMessage

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


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
