import logging
from crewai import Agent
from utils.web_search_utils import enrich_story

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_agent():
    return Agent(
        name="ResearchAgent",
        role="Tech Research Analyst",
        # ▶ Require 3–5 links *only* on the same topic, from approved sources
        goal=(
            "For each headline, gather **3 to 5** distinct supporting links
            "that are directly about that exact AI, quantum computing, or
            "robotics topic. You must include at least:\n"
            "  • One article from a reputable publication,\n"
            "  • One YouTube video by an industry influencer,\n"
            "  • One Twitter or LinkedIn post by a recognized leader.\n"
            "Reject any link that is off-topic or from unknown sources."
        ),
        backstory=(
            "You’re a meticulous researcher who cross-checks and filters
            "out anything not strictly on AI, quantum computing, or
            "robotics from top publications, social, and video."
        ),
        run=run,
    )

def run(stories: list[dict]):
    enriched = []
    for s in stories:
        try:
            item = enrich_story(s)
            # enforce link-count
            links = item.get("links", [])
            if not (3 <= len(links) <= 5):
                logger.warning(
                    "Story '%s' yielded %d links—expecting 3–5", s["title"], len(links)
                )
            enriched.append(item)
        except Exception as e:
            logger.error("Failed to enrich '%s': %s", s.get("title"), e)
    return enriched
