import logging, sys
from crewai import Agent
from utils.google_docs_utils import create_daily_doc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_agent():
    """Return the DocCreatorAgent instance."""
    return Agent(
        name="DocCreatorAgent",
        role="Google Docs Publisher",
        goal="Create the daily digest doc in Drive.",
        backstory="You automate Google Workspace formatting.",
        run=run,
    )


def run(compiled: list[dict]):
    """
    Create the Google Doc and return its link.
    Raises RuntimeError if no valid URL is produced.
    """
    if not isinstance(compiled, list) or not all(isinstance(c, dict) for c in compiled):
        raise RuntimeError("DocCreatorAgent received invalid 'compiled' input (must be list[dict]).")

    if not compiled:
        raise RuntimeError("DocCreatorAgent received EMPTY compiled list – aborting chain.")

    print("[DEBUG] DocCreatorAgent entered, len =", len(compiled), file=sys.stderr)

    try:
        url = create_daily_doc(compiled)
        print("[DEBUG] DocCreatorAgent got URL:", url, file=sys.stderr)
    except Exception as err:
        logger.error("Failed to create daily document: %s", err)
        print("[DEBUG] create_daily_doc error →", err, file=sys.stderr)
        raise  # propagate so GitHub step goes red

    if "docs.google.com/document" not in str(url):
        raise RuntimeError("DocCreatorAgent did NOT receive a Google-Docs URL!")

    return url
