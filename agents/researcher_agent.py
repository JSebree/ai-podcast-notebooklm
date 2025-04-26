from crewai import Agent
from utils.web_search_utils import enrich_story

def get_agent():
    return Agent(
        name="ResearchAgent",
        description="For each story, find 3‑5 authoritative supporting links (official article, at least one YouTube video, and at least one Twitter or LinkedIn post).",
        run=run
    )

def run(stories: list[dict]):
    return [enrich_story(s) for s in stories]  # enriched list[dict]
