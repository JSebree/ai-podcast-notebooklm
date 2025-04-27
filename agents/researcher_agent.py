import logging
import sys
from crewai import Agent
from utils.web_search_utils import enrich_story

# ── logging setup ────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_agent():
    """Return the ResearchAgent instance."""
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
    """
    Enrich each story and return the updated list.
    Raises RuntimeError if the result list is empty (to abort the chain).
    """
    if not isinstance(stories, list) or not all(isinstance(s, dict) for s in stories):
        raise RuntimeError("ResearchAgent received invalid input (must be list[dict]).")

    if not stories:
        raise RuntimeError("ResearchAgent received ZERO stories – aborting chain.")

    print(f"[DEBUG] ResearchAgent received {len(stories)} stories", file=sys.stderr)

    enriched: list[dict] = []
    for story in stories:
        try:
            enriched.append(enrich_story(story))
        except Exception as err:
            logger.error(
                "Failed to enrich story '%s' – %s",
                story.get("title", "<no-title>"),
                err,
            )
            print("[DEBUG] enrich_story error →", err, file=sys.stderr)

    print(f"[DEBUG] ResearchAgent produced {len(enriched)} enriched stories", file=sys.stderr)

    if not enriched:
        raise RuntimeError("ResearchAgent produced ZERO enriched stories – aborting chain.")

    return enriched
