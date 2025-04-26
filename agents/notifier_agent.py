from crewai import Agent
from utils.twilio_utils import send_sms
from utils.email_utils import send_email


def get_agent():
    return Agent(
        name="NotifierAgent",
        description="Send SMS (and fallback email) with the Google Doc link provided.",
        run=run
    )

def run(link: str):
    try:
        send_sms(link)
    except Exception:
        send_email(link)
    return "Notifications dispatched"
