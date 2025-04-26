from crewai import Agent
from utils.google_docs_utils import create_daily_doc


def get_agent():
    return Agent(
        name="DocCreatorAgent",
        role="Google Docs Publisher",
        goal="Create or update a daily Google Doc with the compiled digest.",
        backstory=(
            "You are an automation specialist who formats information neatly "
            "inside Google Workspace documents."
        ),
        run=run,
    )


def run(compiled_stories: list[dict]):
    """Create the Google Doc and return its URL."""
    return create_daily_doc(compiled_stories)
