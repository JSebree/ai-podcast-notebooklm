#!/usr/bin/env python3
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

def main():
    logger.info("🔍 1. Fetching top tech stories…")
    stories = fetch_top_news(max_items=5)
    if not stories:
        logger.error("No stories fetched—aborting.")
        sys.exit(1)

    logger.info("📝 2. Enriching stories…")
    enriched = []
    for s in stories:
        try:
            enriched.append(enrich_story(s))
        except Exception as e:
            logger.error("Enrich failed for %r: %s", s.get("title"), e)
    if not enriched:
        logger.error("No enriched stories—aborting.")
        sys.exit(1)

    logger.info("✍️  3. Compiling summaries…")
    compiled = compile_fn(enriched)
    if not isinstance(compiled, list) or not compiled:
        logger.error("Compilation failed or returned empty—aborting.")
        sys.exit(1)

    logger.info("📄 4. Creating Google Doc…")
    try:
        url = create_daily_doc(compiled)
    except Exception as e:
        logger.exception("Doc creation failed")
        sys.exit(1)

    logger.info("✅ Google Doc created at: %s", url)

    logger.info("📲 5. Sending SMS notification…")
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
