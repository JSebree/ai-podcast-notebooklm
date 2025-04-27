import logging
from crewai import Agent
from utils.twilio_utils import send_sms
from utils.email_utils import send_email

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_agent():
    """
    Create and return an instance of the NotifierAgent.

    :return: An Agent instance configured for dispatching notifications via SMS and email.
    """
    return Agent(
        name="NotifierAgent",
        role="Notification Dispatcher",
        goal="Alert the user via SMS and fallback email with the digest link.",
        backstory="You ensure timely delivery of daily tech updates.",
        run=run,
    )

def run(link: str):
    """
    Send SMS, then fallback to email if SMS fails.

    :param link: The digest link to be sent via notifications.
    :return: A status message indicating the result of the notifications.
    """
    if not link or not isinstance(link, str):
        logger.error("Invalid link provided for notifications.")
        return "Invalid link provided"

    try:
        send_sms(link)
        logger.info("SMS notification sent successfully.")
    except Exception as sms_error:
        logger.error(f"Failed to send SMS: {sms_error}")
        try:
            send_email(link)
            logger.info("Email notification sent

