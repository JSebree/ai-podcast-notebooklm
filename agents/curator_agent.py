from crewai import Agent, Message
from utils.web_search_utils import fetch_top_news

def get_agent():
    return Agent(
        name="CuratorAgent",
        sys_prompt="""You select the 5 most significant breaking stories from the last 24 h in AI, quantum computing, and robotics.""",
        fn=run
    )

def run(_: Message):
    stories = fetch_top_news(max_items=5)
    return Message(content=stories)  # list of dicts {title,url}
