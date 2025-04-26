from crewai import Agent, Message
from utils.twilio_utils import send_sms
from utils.email_utils import send_email

def get_agent():
    return Agent(
        name="NotifierAgent",
        sys_prompt="Send SMS (and fallback email) with the Google Doc link provided.",
        fn=run
    )

def run(msg: Message):
    link = msg.content
    try:
        send_sms(link)
    except Exception as e:
        send_email(link)
    return Message(content="Notifications sent")
