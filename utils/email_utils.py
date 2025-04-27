import os
import smtplib
import ssl
import logging
from email.message import EmailMessage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
USER = os.getenv("SMTP_USER")        # Your email address
PASS = os.getenv("SMTP_PASS")        # 16-char Gmail App Password
HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")

try:
    PORT = int(os.getenv("SMTP_PORT", "465"))  # Default SSL port 465
except ValueError:
    logger.warning("Invalid SMTP_PORT value. Defaulting to 465.")
    PORT = 465

TO = os.getenv("NOTIFY_EMAIL", USER)
CTX = ssl.create_default_context()

# Validate required environment variables
if not USER or not PASS:
    raise EnvironmentError("SMTP_USER and SMTP_PASS environment variables must be set.")
if not TO:
    raise EnvironmentError("NOTIFY_EMAIL environment variable must be set.")

def send_email(link: str):
    """
    Send an email using SMTP.
    
    :param link: The link to include in the email content.
    """
    try:
        msg = EmailMessage()
        msg["Subject"] = "Daily Tech Digest ready"
        msg["From"] = USER
        msg["To"] = TO
        msg.set_content(f"Your Digest is ready: {link}")

        with smtplib.SMTP_SSL(HOST, PORT, context=CTX) as server:
            server.login(USER, PASS)
            server.send_message(msg)
        logger.info(f"Email sent successfully to {TO}")
    except smtplib.SMTPException as e:
        logger.error(f"Failed to send email: {e}")
        raise
