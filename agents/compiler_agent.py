import logging
import sys
from crewai import Agent

# ── logging setup ───────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_agent():
    """Return the CompilerAgent instance."""
    return Agent(
        name="CompilerAgent",
        role="Tech Digest Writer",
        goal=(
            "Turn enriched stories into a structured list of dicts, each with "
            "headline, date, summary, podcast title, and supporting links."
        ),
        backstory=(
            "You distill complex technical developments into clear, engaging copy "
            "that busy audiences can grasp quickly."
        ),
        run=run,
    )

def run(stories: list[dict]):
    """
    :param stories: Enriched stories from ResearchAgent.
    :return: A list of dicts, one per story.
    :raises RuntimeError: if input is invalid or empty.
    """
    # 1️⃣  Validate input type & non-emptiness
    if not isinstance(stories, list):
        raise RuntimeError(f"CompilerAgent expected list[dict], got {type(stories)}")
    if not stories:
        raise RuntimeError("CompilerAgent received ZERO stories – aborting.")

    print(f"[DEBUG] CompilerAgent received {len(stories)} stories", file=sys.stderr)

    compiled: list[dict] = []
    for item in stories:
        # Extract fields from the enriched story
        title   = item.get("title", "Untitled")
        date    = item.get("date", "")
        summary = item.get("article_snippet", "")
        links   = item.get("links", [])

        # Create a concise podcast title
        podcast_title = f"{title} – Quick Tech Dive"

        compiled.append({
            "headline":      title,
            "date":          date,
            "summary":       summary,
            "podcast_title": podcast_title,
            "links":         links,
        })

    print(f"[DEBUG] CompilerAgent produced {len(compiled)} compiled items", file=sys.stderr)
    return compiled
