from crewai import Agent
from utils.web_search_utils import enrich_story

def get_agent():
    return Agent(
        name="ResearchAgent",
        role="Tech Research Analyst",
        goal=(
            "For each curated headline, gather 3–5 authoritative supporting "
            "resources: an official publication article, at least one YouTube "
            "video, and at least one Twitter or LinkedIn post from recognized "
            "industry figures."
        ),
        backstory=(
            "You are a meticulous researcher who cross-checks sources and "
            "surfaces the most credible commentary around emerging-tech news."
        ),
        run=run,
    )

def run(stories: list[dict]):
    """Return the enriched list of story dictionaries."""
    return [enrich_story(s) for s in stories]
