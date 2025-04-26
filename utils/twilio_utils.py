import os
from twilio.rest import Client

sid = os.getenv("TWILIO_ACCOUNT_SID")
client = Client(sid, os.getenv("TWILIO_AUTH_TOKEN"))

FROM = os.getenv("TWILIO_FROM_NUMBER")
TO   = os.getenv("NOTIFY_PHONE")

def send_sms(link):
    client.messages.create(body=f"Today's Tech Digest is ready: {link}", from_=FROM, to=TO)
