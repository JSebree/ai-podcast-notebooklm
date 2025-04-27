import sys, logging
from utils.web_search_utils   import fetch_top_news, enrich_story
from agents.compiler_agent    import run as compiler_run
from utils.google_docs_utils  import create_daily_doc

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def main():
    # 1️⃣ Curate
    logger.info("🔍 Fetching top tech stories…")
    stories = fetch_top_news(max_items=5)
    if not stories:
        logger.error("No stories fetched; aborting.")
        sys.exit(1)

    # 2️⃣ Research
    logger.info("🔎 Enriching each story…")
    enriched = []
    for s in stories:
        try:
            enriched.append(enrich_story(s))
        except Exception as e:
            logger.error("Enrichment error on %r: %s", s.get("title"), e)
    if not enriched:
        logger.error("No enriched stories; aborting.")
        sys.exit(1)

    # 3️⃣ Compile
    logger.info("✍️ Compiling summaries…")
    compiled = compiler_run(enriched)
    if not isinstance(compiled, list) or not compiled:
        logger.error("Compilation failed or empty; aborting.")
        sys.exit(1)

    # 4️⃣ Create Google Doc
    logger.info("📄 Creating Google Doc…")
    try:
        url = create_daily_doc(compiled)
    except Exception:
        logger.exception("Doc creation failed")
        sys.exit(1)

    logger.info("✅ All done! Document is at: %s", url)
    # Print for GitHub logs
    print("\n🍍 Daily Digest URL:", url)

if __name__ == "__main__":
    main()
