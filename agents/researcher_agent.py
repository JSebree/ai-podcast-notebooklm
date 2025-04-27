import logging
from crewai import Agent
from utils.web_search_utils import enrich_story

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_agent():
    """
    Create and return an instance of the ResearchAgent.

    :return: An Agent instance configured for researching and enriching stories.
    """
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
            "surfaces the most credible commentary on emerging-tech news."
        ),
        run=run,
    )

def run(stories: list[dict]):
    """
    Return the enriched list of story dictionaries.

    :param stories: A list of dictionaries, each representing a story to be enriched.
    :return: A list of enriched story dictionaries.
    """
    if not isinstance(stories, list) or not all(isinstance(s, dict) for s in stories):
        logger.error("Invalid input: 'stories' must be a list of dictionaries.")
        return []

    if not stories:
        logger.warning("The 'stories' list is empty. No enrichment will be performed.")
        return []

    enriched_stories = []
    for story in stories:
        try:
            enriched_story = enrich_story(story)
            enriched_stories.append(enriched_story)
        except Exception as e:
            logger.error(f"Failed to enrich story {story.get('title

