from crewai import Agent
from utils.web_search_utils import fetch_top_news


def get_agent():
    return Agent(
        name="CuratorAgent",
        role="News Curator",
        goal=(
            "Identify the five most important breaking stories in AI, "
            "quantum computing, and robotics every 24 hours."
        ),
        backstory=(
            "You are an experienced tech journalist with a keen eye for "
            "industry-moving announcements and scientific breakthroughs."
        ),
        run=run,
    )


def run(_=None):
    # Returns list[dict] with keys: title, url, rank
    return fetch_top_news(max_items=5)
