import logging
import sys
from crewai import Agent
from utils.web_search_utils import fetch_top_news

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_agent():
    """Return the CuratorAgent instance."""
    return Agent(
        name="CuratorAgent",
        role="News Curator",
        goal=(
            "Identify the five most important breaking stories in AI, "
            "quantum computing, and robotics every from the past 36 hours."
            "**IMPORTANT! only gather stpries from the past 36 hours from this date."
            "Pull stories from reputale publications, Linkedin and Twitter posts "
            "from industry leaders and influencers, and YouTube influencer who specialize "
            "in AI, quantum computing, and robotics." 
        ),
        backstory=(
            "You are an experienced tech journalist with a keen eye for "
            "industry-moving announcements and scientific breakthroughs."
        ),
        run=run,
    )


def run(_=None, max_items: int = 5):
    """
    Fetch and validate the top news stories.

    :param _ : (ignored) dependency input from CrewAI chain.
    :param max_items: Number of stories to fetch.
    :return: List of story dicts.
    :raises RuntimeError: if zero stories are fetched.
    """
    stories = fetch_top_news(max_items=max_items)

    # ── validate structure ─────────────────────────────
    if not isinstance(stories, list):
        raise RuntimeError("fetch_top_news() returned non-list object")

    if not stories:
        raise RuntimeError("CuratorAgent fetched ZERO stories – aborting chain.")

    for item in stories:
        if not isinstance(item, dict) or not all(k in item for k in ("title", "url", "rank")):
            raise RuntimeError(f"Invalid news item format: {item}")

    print(f"[DEBUG] CuratorAgent fetched {len(stories)} stories", file=sys.stderr)
    return stories
