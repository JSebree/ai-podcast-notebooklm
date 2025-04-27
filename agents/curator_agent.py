import logging
from crewai import Agent
from utils.web_search_utils import fetch_top_news

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_agent():
    return Agent(
        name="CuratorAgent",
        role="News Curator",
        model="gpt-4o",
        # ▶ Focus only on AI, quantum computing, or robotics stories
        goal=(
            "In the last 36 hours, find breaking news articles **strictly** "
            "about artificial intelligence, quantum computing, or robotics."
            "Use only reputable tech publications (e.g. MIT Technology Review, "
            "IEEE Spectrum, Wired, Science, Nature, etc.). Rank by search term "
            "relevance (AI, quantum, robotics) and novelty, and "
            "return ONLY the **top 5 AI, quantum, and robotics** stories."
        ),
        backstory=(
            "You are a veteran tech journalist who never strays outside the "
            "fields of AI, quantum computing, and robotics, and only trusts "
            "well–known outlets."
        ),
        run=run,
    )

def run(max_items=5):
    try:
        news = fetch_top_news(max_items=max_items)
        # Validate each headline contains one of the three topics
        valid = [n for n in news if any(
            kw in n["title"].lower()
            for kw in ["artificial intelligence","ai","quantum","robot","robotics"]
        )]
        if len(valid) < len(news):
            logger.warning("Filtered out %d off-topic stories", len(news)-len(valid))
        return valid[:max_items]
    except Exception as e:
        logger.error("CuratorAgent error: %s", e)
        return []
