from crewai import Agent
from utils.google_docs_utils import create_daily_doc

def get_agent():
    return Agent(
        name="DocCreatorAgent",
        role="Google Docs Publisher",
        goal="Create the daily digest doc in Drive.",
        backstory="You automate Google Workspace formatting.",
        run=run,
    )

def run(compiled: list[dict]):
    print("[DEBUG] DocCreatorAgent entered, len =", len(compiled))
    url = create_daily_doc(compiled)
    print("[DEBUG] DocCreatorAgent returned URL:", url)
    return url
