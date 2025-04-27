import logging, sys
from agents.curator_agent     import get_agent as get_curator
from agents.researcher_agent  import get_agent as get_researcher
from agents.compiler_agent    import get_agent as get_compiler
from agents.doc_creator_agent import get_agent as get_doc_creator
from agents.notifier_agent    import get_agent as get_notifier

# ── Logging ─────────────────────────────────────────────────────
logging.basicConfig(level=logging.DEBUG, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def debug(msg, *args):
    print("[DEBUG]", msg, *args, file=sys.stderr)

def main():
    debug("1️⃣  CuratorAgent: fetching top stories…")
    curator = get_curator()
    stories = curator.run()  
    debug("CuratorAgent returned", len(stories), "stories")
    if not stories:
        raise RuntimeError("CuratorAgent returned zero stories")

    debug("2️⃣  ResearchAgent: enriching…")
    researcher = get_researcher()
    enriched = researcher.run(stories)
    debug("ResearchAgent returned", len(enriched), "enriched stories")
    if not enriched:
        raise RuntimeError("ResearchAgent returned zero enriched stories")

    debug("3️⃣  CompilerAgent: compiling…")
    compiler = get_compiler()
    compiled = compiler.run(enriched)
    debug("CompilerAgent returned", len(compiled), "compiled items")
    if not compiled:
        raise RuntimeError("CompilerAgent returned zero compiled items")

    debug("4️⃣  DocCreatorAgent: creating Google Doc…")
    doc_creator = get_doc_creator()
    url = doc_creator.run(compiled)
    debug("DocCreatorAgent returned URL:", url)
    if not url or "docs.google.com/document" not in url:
        raise RuntimeError("Invalid Doc URL from DocCreatorAgent")

    debug("5️⃣  NotifierAgent: sending notifications…")
    notifier = get_notifier()
    status = notifier.run(url)
    debug("NotifierAgent returned status:", status)

    logger.info("✅ Workflow complete—Doc URL: %s", url)
    # also print the URL so GH Actions picks it up in logs
    print("\n📄 Daily Digest is here:", url)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error("Workflow failed: %s", e)
        sys.exit(1)
