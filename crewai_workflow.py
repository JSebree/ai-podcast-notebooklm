import logging, sys
from agents.curator_agent     import get_agent as get_curator
from agents.researcher_agent  import get_agent as get_researcher
from agents.compiler_agent    import get_agent as get_compiler
from agents.doc_creator_agent import get_agent as get_doc_creator
from agents.notifier_agent    import get_agent as get_notifier

# Configure top-level logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def main():
    # 1️⃣ Curate
    curator = get_curator()
    stories = curator.run()
    logger.info("⓵ Curator fetched %d stories", len(stories))
    if not stories:
        sys.exit("No stories; aborting.")

    # 2️⃣ Research
    researcher = get_researcher()
    enriched = researcher.run(stories)
    logger.info("⓶ Researcher enriched %d stories", len(enriched))
    if not enriched:
        sys.exit("Enrichment failed; aborting.")

    # 3️⃣ Compile
    compiler = get_compiler()
    compiled = compiler.run(enriched)
    logger.info("⓷ Compiler produced %d items", len(compiled))
    if not compiled:
        sys.exit("Compilation failed; aborting.")

    # 4️⃣ Doc creation
    doc_creator = get_doc_creator()
    url = doc_creator.run(compiled)
    logger.info("⓸ Document created at %s", url)
    if not url:
        sys.exit("No doc URL; aborting.")

    # 5️⃣ Notify
    notifier = get_notifier()
    status = notifier.run(url)
    logger.info("⓹ Notifier status: %s", status)

if __name__ == "__main__":
    main()
