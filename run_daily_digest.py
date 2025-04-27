import os, sys, logging
from datetime import datetime

# 1️⃣  Curator: fetch top headlines
from utils.web_search_utils import fetch_top_news
# 2️⃣  Research: enrich each story
from utils.web_search_utils import enrich_story
# 3️⃣  Compile: format into structured dicts
from agents.compiler_agent import run as compile_fn
# 4️⃣  Doc: create & move Google Doc
from utils.google_docs_utils import create_daily_doc
# 5️⃣  Notify: SMS & email
from utils.twilio_utils import send_sms
from utils.email_utils  import send_email

logging.basicConfig(level=logging.DEBUG, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def debug(msg, *args):
    print("[DEBUG]", msg, *args, file=sys.stderr)

def main():
    debug("1️⃣  CuratorAgent: fetching top stories…")
    stories = fetch_top_news(max_items=5)
    debug("CuratorAgent returned", len(stories), "stories")
    if not stories:
        logger.error("No stories fetched—aborting.")
        sys.exit(1)

    debug("2️⃣  ResearchAgent: enriching…")
    enriched = []
    for s in stories:
        try:
            enriched.append(enrich_story(s))
        except Exception as e:
            logger.error("Enrich failed for %r: %s", s.get("title"), e)
    debug("ResearchAgent returned", len(enriched), "enriched stories")
    if not enriched:
        logger.error("No enriched stories—aborting.")
        sys.exit(1)

    debug("3️⃣  CompilerAgent: compiling…")
    compiled = compile_fn(enriched)
    debug("CompilerAgent returned", len(compiled), "compiled items")
    if not isinstance(compiled, list) or not compiled:
        logger.error("Compilation failed or returned empty—aborting.")
        sys.exit(1)

    debug("4️⃣  DocCreatorAgent: creating Google Doc…")
    try:
        url = create_daily_doc(compiled)
    except Exception as e:
        logger.exception("Doc creation failed")
        sys.exit(1)
    debug("DocCreatorAgent returned URL:", url)
    logger.info("Google Doc created at: %s", url)

    debug("5️⃣  NotifierAgent: sending notifications…")
    try:
        send_sms(url)
    except Exception as sms_err:
        logger.warning("SMS failed: %s; falling back to email", sms_err)
        try:
            send_email(url)
        except Exception as email_err:
            logger.exception("Email also failed")
            sys.exit(1)

    logger.info("All done! Digest at %s", url)

if __name__ == "__main__":
    main()
