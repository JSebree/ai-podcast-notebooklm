import os
import smtplib
import ssl
from email.message import EmailMessage

USER = os.getenv("SMTP_USER")        # your Gmail address
PASS = os.getenv("SMTP_PASS")        # 16‑char Gmail App Password
HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")

# Gracefully handle non‑numeric or unset port env
try:
    PORT = int(os.getenv("SMTP_PORT", "465"))  # default SSL port 465
except ValueError:
    PORT = 465

TO  = os.getenv("NOTIFY_EMAIL", USER)
CTX = ssl.create_default_context()

def send_email(link: str):
    msg = EmailMessage()
    msg["Subject"] = "Daily Tech Digest ready"
    msg["From"] = USER
    msg["To"] = TO
    msg.set_content(f"Your Digest is ready: {link}")
    with smtplib.SMTP_SSL(HOST, PORT, context=CTX) as server:
        server.login(USER, PASS)
        server.send_message(msg)
