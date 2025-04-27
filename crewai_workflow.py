import logging, sys
from crewai import Task, Crew
from agents.curator_agent    import get_agent as curator
from agents.researcher_agent import get_agent as researcher
from agents.compiler_agent   import get_agent as compiler
from agents.doc_creator_agent import get_agent as doc_creator
from agents.notifier_agent   import get_agent as notifier

# ── Logging setup ───────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
print("[DEBUG] crewai_workflow starting", file=sys.stderr)

# ── Instantiate agents ─────────────────────────────────────────
curator_agent   = curator()
research_agent  = researcher()
compiler_agent  = compiler()
doc_agent       = doc_creator()
notifier_agent  = notifier()

def agent_name(agent):
    """Safely extract an Agent’s name for debug output."""
    return getattr(getattr(agent, "profile", None), "name", repr(agent))

# ── Define the full chain of tasks ──────────────────────────────
def define_tasks():
    curate = Task(
        agent=curator_agent,
        description="Pick top 5 stories from last 24 h.",
        expected_output="list[dict]",
    )
    research = Task(
        agent=research_agent,
        depends_on=curate,
        description="Enrich each story with links + snippet.",
        expected_output="list[dict] enriched",
    )
    compile_ = Task(
        agent=compiler_agent,
        depends_on=research,
        description="Generate summary + podcast title.",
        expected_output="compiled list[dict]",
    )
    create_doc = Task(
        agent=doc_agent,
        depends_on=compile_,
        description="Create Google Doc and return its URL.",
        expected_output="doc URL (str)",
    )
    notify = Task(
        agent=notifier_agent,
        depends_on=create_doc,
        description="Send SMS + email with the URL.",
        expected_output="confirmation str",
    )

    tasks = [curate, research, compile_, create_doc, notify]
    print(
        "[DEBUG] Crew tasks scheduled →",
        [agent_name(t.agent) for t in tasks],
        file=sys.stderr
    )
    return tasks

# ── Run the CrewAI pipeline ──────────────────────────────────────
if __name__ == "__main__":
    crew = Crew(tasks=define_tasks())
    print("[DEBUG] Dispatching Crew via kickoff()", file=sys.stderr)

    # kickoff() is the only method available on your Crew
    result = crew.kickoff()

    print("[DEBUG] Crew returned →", result, file=sys.stderr)

    # Fail fast if no valid Google Docs link
    if not result or "docs.google.com/document" not in str(result):
        raise RuntimeError("❌ No Google Doc URL produced – aborting build.")

    logger.info("✅ Workflow finished successfully. Doc URL: %s", result)
