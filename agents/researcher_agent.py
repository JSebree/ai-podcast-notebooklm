import logging
from crewai import Agent
from utils.web_search_utils import enrich_story

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_agent():
    """Return a ResearchAgent configured to enrich stories."""
    return Agent(
        name="ResearchAgent",
        role="Tech Research Analyst",
        goal=(
            "For each curated headline, gather 3–5 authoritative supporting "
            "resources (official article, YouTube, Twitter/LinkedIn)."
        ),
        backstory=(
            "You verify sources and surface the most credible commentary on "
            "emerging-tech news."
        ),
        run=run,
    )

def run(stories: list[dict]):
    """Enrich each story and return the updated list."""
    if not isinstance(stories, list) or not all(isinstance(s, dict) for s in stories):
        logger.error("Invalid input: 'stories' must be a list of dicts.")
        return []

    if not stories:
        logger.warning("The 'stories' list is empty. No enrichment performed.")
        return []

    enriched = []
    for story in stories:
        try:
            enriched.append(enrich_story(story))
        except Exception as e:
            logger.error(
                "Failed to enrich story '%s' – %s",
                story.get("title", "<no-title>"),
                e,
            )
    return enriched
