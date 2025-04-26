from crewai import Agent, Message
from utils.google_docs_utils import create_daily_doc

def get_agent():
    return Agent(
        name="DocCreatorAgent",
        sys_prompt="Create a formatted Google Doc for today with each story’s podcast title, summary, and supporting links.",
        fn=run
    )

def run(msg: Message):
    url = create_daily_doc(msg.content)
    return Message(content=url)
