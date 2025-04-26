from crewai import Agent
from utils.google_docs_utils import create_daily_doc


def get_agent():
    return Agent(
        name="DocCreatorAgent",
        role="Google Docs Publisher",
        goal="Create or update a daily Google Doc with the compiled digest.",
        backstory="You handle document automation and formatting in Google Workspace.",
        run=run,
    )


def run(compiled: list[dict]):
    return create_daily_doc(compiled)  # -> str (doc URL)
