import sys, logging
from utils.web_search_utils   import fetch_top_news, enrich_story
from agents.compiler_agent    import run as compiler_run
from utils.google_docs_utils  import create_daily_doc
from utils.twilio_utils       import send_sms
from utils.email_utils        import send_email

logging.basicConfig(level=logging.DEBUG, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def main():
    # 1) Curate
    logger.info("🔍 Fetching top tech stories…")
    stories = fetch_top_news(max_items=5)
    logger.debug("♦ Curator fetched %d stories", len(stories))
    if not stories:
        logger.error("No stories fetched; aborting.")
        sys.exit(1)

    # 2) Research
    logger.info("🔎 Enriching each story…")
    enriched = []
    for s in stories:
        try:
            enriched.append(enrich_story(s))
        except Exception as e:
            logger.error("Enrichment error on %r: %s", s.get("title"), e)
    logger.debug("♦ Researcher enriched %d stories", len(enriched))
    if not enriched:
        logger.error("No enriched stories; aborting.")
        sys.exit(1)

    # 3) Compile
    logger.info("✍️ Compiling summaries…")
    compiled = compiler_run(enriched)
    logger.debug("♦ Compiler produced %d items", len(compiled))
    if not isinstance(compiled, list) or not compiled:
        logger.error("Compilation failed or empty; aborting.")
        sys.exit(1)

    # 4) Create + move Google Doc
    logger.info("📄 Creating Google Doc…")
    try:
        url = create_daily_doc(compiled)
    except Exception as e:
        logger.exception("Doc creation failed")
        sys.exit(1)
    logger.debug("♦ DocCreator returned URL: %s", url)

    # 5) Notify via SMS, fallback to email
    logger.info("📲 Sending SMS notification…")
    try:
        sms = send_sms(url)
        logger.debug("♦ SMS sent: SID=%s status=%s", sms.sid, sms.status)
    except Exception as sms_err:
        logger.error("SMS failed: %s – falling back to email", sms_err)
        try:
            send_email(url)
            logger.debug("♦ Email fallback sent")
        except Exception as email_err:
            logger.exception("Email fallback also failed")
            sys.exit(1)

    logger.info("✅ All done! Digest is at: %s", url)
    # Print the URL so GH Actions UI surfaces it
    print("\n🍍 Daily Digest:", url)

if __name__ == "__main__":
    main()
