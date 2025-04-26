from crewai import Agent
from utils.web_search_utils import fetch_top_news

def get_agent():
    return Agent(
        name='CuratorAgent',
        role='News Curator',
        goal='Identify the five most important breaking stories in AI, quantum computing, and robotics every 24 hours.',
        backstory='You are an experienced tech journalist with a keen eye for breakthroughs and industry‑moving announcements.',
        run=run,
    )

def run(_=None):
    return fetch_top_news(max_items=5)
```python
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
