from crewai import Agent
from utils.google_docs_utils import create_daily_doc


def get_agent():
    return Agent(
        name="DocCreatorAgent",
        description="Create a formatted Google Doc for today with each story’s podcast title, summary, and links.",
        run=run
    )

def run(compiled: list[dict]):
    return create_daily_doc(compiled)  # -> str (doc URL)
