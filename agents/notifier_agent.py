from crewai import Agent
from utils.twilio_utils import send_sms
from utils.email_utils import send_email


def get_agent():
    return Agent(
        name="NotifierAgent",
        role="Notification Dispatcher",
        goal="Alert the user via SMS and fallback email with the digest link.",
        backstory="You ensure timely delivery of daily tech updates.",
        run=run,
    )


def run(link: str):
    """Send SMS, then fallback email if SMS fails."""
    try:
        send_sms(link)
    except Exception:
        send_email(link)
    return "Notifications dispatched"
