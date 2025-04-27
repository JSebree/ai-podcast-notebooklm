import logging
from crewai import Agent
from utils.google_docs_utils import create_daily_doc

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_agent():
    """
    Create and return an instance of the DocCreatorAgent.

    :return: An Agent instance configured for creating Google Docs.
    """
    return Agent(
        name="DocCreatorAgent",
        role="Google Docs Publisher",
        goal="Create the daily digest doc in Drive.",
        backstory="You automate Google Workspace formatting.",
        run=run,
    )

def run(compiled: list[dict]):
    """
    Generate a daily digest document in Google Drive.

    :param compiled: A list of dictionaries containing the content for the document.
    :return: The URL of the created document, or None if an error occurs.
    """
    if not isinstance(compiled, list) or not all(isinstance(item, dict) for item in compiled):
        logger.error("Invalid input: 'compiled' must be a list of dictionaries.")
        return None

    if not compiled:
        logger.warning("The 'compiled' list is empty. No document will be created.")
        return None

    try:
        logger.debug("DocCreatorAgent entered, len = %d", len(compiled))
        url = create_daily_doc(compiled)
        logger.debug("DocCreatorAgent returned URL: %s", url)
        return url
    except Exception as e:
        logger.error("Failed to create daily document: %s", e)
        return None
