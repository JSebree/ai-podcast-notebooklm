from crewai import Agent
from utils.web_search_utils import fetch_top_news

def get_agent():
    return Agent(
        name="CuratorAgent",
        description="Selects top 5 breaking stories in AI, quantum, and robotics from the last 24 hours.",
        run=run
    )

def run(_: list | None = None):
    return fetch_top_news(max_items=5)   # -> list[dict]
