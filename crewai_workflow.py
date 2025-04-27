import logging, sys
from agents.curator_agent    import get_agent as get_curator
from agents.researcher_agent import get_agent as get_researcher
from agents.compiler_agent   import get_agent as get_compiler
from agents.doc_creator_agent import get_agent as get_doc_creator
from agents.notifier_agent   import get_agent as get_notifier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Instantiate agents
curator   = get_curator()
research  = get_researcher()
compiler  = get_compiler()
doc_creator = get_doc_creator()
notifier  = get_notifier()

def debug(msg, *vals):
    print("[DEBUG]", msg, *vals, file=sys.stderr)

def main():
    debug("Starting manual workflow")

    # 1️⃣ Curate
    stories = curator.run()
    debug("CuratorAgent produced", len(stories), "stories")
    if not stories:
        raise RuntimeError("CuratorAgent returned ZERO stories – aborting.")

    # 2️⃣ Research
    enriched = research.run(stories)
    debug("ResearchAgent produced", len(enriched), "enriched stories")
    if not enriched:
        raise RuntimeError("ResearchAgent returned ZERO enriched stories – aborting.")

    # 3️⃣ Compile
    compiled = compiler.run(enriched)
    debug("CompilerAgent produced", len(compiled), "items")
    if not compiled:
        raise RuntimeError("CompilerAgent returned ZERO compiled items – aborting.")

    # 4️⃣ Create the Google Doc
    url = doc_creator.run(compiled)
    debug("DocCreatorAgent returned URL:", url)
    if not url or "docs.google.com/document" not in url:
        raise RuntimeError("DocCreatorAgent did not return a valid Doc URL.")

    # 5️⃣ Notify
    status = notifier.run(url)
    debug("NotifierAgent returned status:", status)

    logger.info("✅ WORKFLOW COMPLETE — Doc URL: %s", url)
    return url

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error("Workflow failed: %s", e)
        sys.exit(1)
