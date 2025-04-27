import os
import logging
import sys
from crewai import Agent
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load API key and validate
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise EnvironmentError("Environment variable 'OPENAI_API_KEY' is not set.")
client = OpenAI(api_key=api_key)

# Model configuration
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o")

PROMPT_TITLE = "Write a punchy podcast episode title (under 12 words) summarizing: "
PROMPT_SUMMARY = "Provide a 6-sentence journalistic summary of the following tech news:\n"

def get_agent():
    return Agent(
        name="CompilerAgent",
        role="Tech Digest Writer",
        goal=(
            "Turn enriched stories into a one-paragraph summary and a catchy "
            "podcast title for each item."
        ),
        backstory=(
            "You distill complex technical developments into clear, engaging "
            "copy that busy audiences can grasp quickly."
        ),
        run=run,
    )

def run(stories: list[dict]):
    print("[DEBUG] CompilerAgent received", len(stories), "stories", file=sys.stderr)
    if not stories:
        logger.warning("No stories provided to the `run` function.")
        return []

    compiled = []

    for story in stories:
        if not isinstance(story, dict):
            logger.error(f"Invalid story format: {story}")
            continue

        if "title" not in story or "links" not in story:
            logger.error(f"Missing required keys in story: {story}")
            continue

        try:
            # --- generate podcast title ---
            title_prompt = PROMPT_TITLE + story["title"]
            podcast_title = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": title_prompt}],
            ).choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating podcast title for story '{story['title']}': {e}")
            podcast_title = "Error generating title"

        try:
            # --- generate summary ---
            context = story.get("article_snippet") or story["title"]
            summary_prompt = PROMPT_SUMMARY + context
            summary = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": summary_prompt}],
            ).choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating summary for story '{story['title']}': {e}")
            summary = "Error generating summary"

        compiled.append(
            {
                "headline": story["title"],
                "podcast_title": podcast_title,
                "summary": summary,
                "links": story["links"],
            }
        )
        print("[DEBUG] CompilerAgent produced", len(compiled), "items", file=sys.stderr)

    return compiled
