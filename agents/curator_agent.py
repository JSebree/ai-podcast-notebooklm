import logging
from crewai import Agent
from utils.web_search_utils import fetch_top_news

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

def run(max_items=5):
    """
    Fetch the top news stories.

    :param max_items: The maximum number of news items to fetch (default: 5).
    :return: A list of dictionaries with keys: 'title', 'url', 'rank'.
    """
    try:
        news = fetch_top_news(max_items=max_items)
        if not isinstance(news, list):
            raise ValueError("Unexpected response from fetch_top_news: Expected a list.")

        for item in news:
            if not isinstance(item, dict) or not all(key in item for key in ("title", "url", "rank")):
                raise ValueError(f"Invalid news item format: {item}")

        return news
    except Exception as e:
        logger.error(f"Error fetching or validating news: {e}")
        return []
