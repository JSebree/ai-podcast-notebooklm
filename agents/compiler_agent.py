import logging, sys
from crewai import Agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_agent():
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
    """
    # 1️⃣  Validate input
    if not isinstance(stories, list):
        raise RuntimeError("CompilerAgent expected a list, got %r" % type(stories))
    if not stories:
        raise RuntimeError("CompilerAgent received ZERO stories – aborting.")

    print(f"[DEBUG] CompilerAgent received {len(stories)} stories", file=sys.stderr)

    compiled = []
    for item in stories:
        # you may need to adjust these keys to match your enrich_story output
        title   = item.get("title", "Untitled")
        date    = item.get("date", "")
        summary = item.get("article_snippet") or item.get("summary", "")
        links   = item.get("links", [])

        # generate a one-line podcast episode title
        podcast_title = f"{title} – Quick Tech Dive"

        compiled.append({
            "headline": title,
            "date":      date,
            "summary":   summary,
            "podcast_title": podcast_title,
            "links":     links,
        })

    print(f"[DEBUG] CompilerAgent produced {len(compiled)} compiled items", file=sys.stderr)
    return compiled
