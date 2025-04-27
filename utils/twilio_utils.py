import os
import re
import logging
from twilio.rest import Client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
FROM = os.getenv("TWILIO_FROM_NUMBER")
TO = os.getenv("NOTIFY_PHONE")

# Validate environment variables
if not sid or not auth_token:
    raise EnvironmentError("Twilio credentials (TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN) are not set.")
if not FROM:
    raise EnvironmentError("Twilio 'FROM' phone number (TWILIO_FROM_NUMBER) is not set.")
if not TO:
    raise EnvironmentError("Notification 'TO' phone number (NOTIFY_PHONE) is not set.")

# Validate phone numbers (E.164 format)
def validate_phone_number(phone_number):
    pattern = r"^\+?[1-9]\d{1,14}$"  # E.164 format
    if not re.match(pattern, phone_number):
        raise ValueError(f"Invalid phone number format: {phone_number}")

validate_phone_number(FROM)
validate_phone_number(TO)

# Initialize Twilio client
client = Client(sid, auth_token)

def send_sms(link, body=None):
    """
    Send an SMS using Twilio's API.
    
    :param link: The link to include in the message body.
    :param body: Optional custom message body. Defaults to a standard message format.
    """
    if body is None:
        body = f"Today's Tech Digest is ready: {link}"
    
    try:
        client.messages.create(
            body=body,
            from_=FROM,
            to=TO
        )
        logger.info(f"SMS sent successfully to {TO}")
    except Exception as e:
        logger.error(f"Failed to send SMS: {e}")
        raise
