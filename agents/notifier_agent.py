import logging
from crewai import Agent
from utils.twilio_utils import send_sms
from utils.email_utils import send_email

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_agent():
    """Return a NotifierAgent that delivers digest links to the user."""
    return Agent(
        name="NotifierAgent",
        role="Notification Dispatcher",
        goal="Alert the user via SMS and, if that fails, via email.",
        backstory=(
            "You ensure the daily tech digest reaches the user reliably, "
            "trying SMS first and falling back to email."
        ),
        run=run,
    )


def run(link: str):
    """Send SMS, with email fallback. Return a status string."""
    if not isinstance(link, str) or not link.strip():
        logger.error("Invalid link provided for notifications: %s", link)
        return "Invalid link"

    # ── Attempt SMS first ────────────────────────────
    try:
        send_sms(link)
        logger.info("SMS notification sent successfully.")
        return "SMS sent"
    except Exception as sms_error:
        logger.error("Failed to send SMS → %s", sms_error)

    # ── Fallback to email ────────────────────────────
    try:
        send_email(link)
        logger.info("Email notification sent successfully.")
        return "Email fallback sent"
    except Exception as email_error:
        logger.error("Failed to send fallback email → %s", email_error)
        return "Both SMS and email failed"
