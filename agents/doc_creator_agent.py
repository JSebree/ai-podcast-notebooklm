import logging
import sys
from crewai import Agent
from utils.google_docs_utils import create_daily_doc

# ── logging setup ───────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_agent():
    """
    Return the DocCreatorAgent. This agent expects a list[dict] from
    CompilerAgent and uses it to create/move/share a Google Doc, returning
    the final docs.google.com URL.
    """
    return Agent(
        name="DocCreatorAgent",
        role="Google Docs Publisher",
        goal="Create the daily digest doc in Drive and return its URL.",
        backstory="You automate Google Workspace formatting for daily tech digests.",
        run=run,
    )

def run(compiled: list[dict]) -> str:
    """
    Create the Google Doc and return its URL.
    :param compiled: A list of dicts (headline, date, summary, podcast_title, links)
    :return: The docs.google.com URL.
    :raises RuntimeError: if input is invalid or URL isn’t produced.
    """
    # 1️⃣  Validate input
    if not isinstance(compiled, list) or not all(isinstance(c, dict) for c in compiled):
        raise RuntimeError("DocCreatorAgent expected list[dict], got %r" % type(compiled))

    if not compiled:
        raise RuntimeError("DocCreatorAgent received ZERO compiled items – aborting.")

    print(f"[DEBUG] DocCreatorAgent received {len(compiled)} items", file=sys.stderr)

    # 2️⃣  Create the doc
    try:
        url = create_daily_doc(compiled)
        print("[DEBUG] DocCreatorAgent got URL:", url, file=sys.stderr)
    except Exception as err:
        logger.error("Failed to create/move/share document: %s", err)
        print("[DEBUG] create_daily_doc error →", err, file=sys.stderr)
        raise

    # 3️⃣  Validate the URL
    if not isinstance(url, str) or "docs.google.com/document" not in url:
        raise RuntimeError("DocCreatorAgent did not receive a valid Google Doc URL: %r" % url)

    return url
