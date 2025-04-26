from crewai import Agent, Message
from utils.web_search_utils import enrich_story

def get_agent():
    return Agent(
        name="ResearchAgent",
        sys_prompt="""For each story provided, find 3‑5 authoritative supporting links: (1) official publication article, (2) at least one YouTube video, (3) at least one post from Twitter or LinkedIn by an industry leader.""",
        fn=run
    )

def run(msg: Message):
    enriched = [enrich_story(s) for s in msg.content]  # adds 'summary' & 'links'
    return Message(content=enriched)
