import logging
from crewai import Agent
from utils.web_search_utils import enrich_story

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_agent():
    return Agent(
        name="ResearchAgent",
        role="Tech Research Analyst",
        goal=(
            "For each headline, gather **3 to 5** distinct supporting links "
            "that are directly about that exact AI, quantum computing, or "
            "robotics topic. You must include at least 3 of the following:\n"
            "  • article(s) from reputable publications,\n"
            "  • YouTube video(s) by industry influencers,\n"
            "  • Twitter or LinkedIn post(s) by a recognized industry leaders.\n"
            "**Reject any link that is off-topic or from unknown sources."
        ),
        backstory=(
            "You’re a meticulous researcher who cross-checks and filters "
            "out anything not strictly on AI, quantum computing, or "
            "robotics from top publications, social, and video."
        ),
        run=run,
    )


def run(stories: list[dict]) -> list[dict]:
    enriched = []
    for s in stories:
        try:
            item = enrich_story(s)
            links = item.get("links", [])
            # warn only if fewer than 3 links
            if len(links) < 3:
                logger.warning(
                    "Story '%s' yielded only %d links; expected at least 3.",
                    s.get("title", "<no-title>"),
                    len(links),
                )
            enriched.append(item)
        except Exception as e:
            logger.error("Failed to enrich '%s': %s", s.get("title", "<no-title>"), e)
    return enriched
