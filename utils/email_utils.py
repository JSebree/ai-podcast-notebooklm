import os, smtplib, ssl
from email.message import EmailMessage

USER = os.getenv("SMTP_USER")        # your Gmail address
PASS = os.getenv("SMTP_PASS")        # 16‑char Gmail App Password
HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
PORT = int(os.getenv("SMTP_PORT", "465"))   # SSL port 465
TO   = os.getenv("NOTIFY_EMAIL", USER)

ctx = ssl.create_default_context()

def send_email(link: str):
    msg = EmailMessage()
    msg["Subject"] = "Daily Tech Digest ready"
    msg["From"] = USER
    msg["To"] = TO
    msg.set_content(f"Your Digest is ready: {link}")
    with smtplib.SMTP_SSL(HOST, PORT, context=ctx) as server:
        server.login(USER, PASS)
        server.send_message(msg)
