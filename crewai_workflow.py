import logging, sys
from crewai import Task, Crew
from agents.curator_agent import get_agent as curator
from agents.researcher_agent import get_agent as researcher
from agents.compiler_agent import get_agent as compiler
from agents.doc_creator_agent import get_agent as doc_creator
from agents.notifier_agent import get_agent as notifier

# ── logging setup ───────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
print("[DEBUG] crewai_workflow starting", file=sys.stderr)

# ── instantiate agents ─────────────────────────────────────────
curator_agent   = curator()
research_agent  = researcher()
compiler_agent  = compiler()
doc_agent       = doc_creator()
notifier_agent  = notifier()

# helper to get a readable agent name without crashing
def agent_name(agent):
    return getattr(getattr(agent, "profile", None), "name", repr(agent))

# ── define tasks ───────────────────────────────────────────────
def define_tasks():
    curate_task = Task(
        agent=curator_agent,
        description="Pick top 5 stories from last 24 h.",
        expected_output="list[dict]",
    )

    research_task = Task(
        agent=research_agent,
        depends_on=curate_task,
        description="Enrich each story with links + snippet.",
        expected_output="list[dict] enriched",
    )

    compile_task = Task(
        agent=compiler_agent,
        depends_on=research_task,
        description="Generate summary + podcast title.",
        expected_output="compiled list[dict]",
    )

    doc_task = Task(
        agent=doc_agent,
        depends_on=compile_task,
        description="Create Google Doc and return its URL.",
        expected_output="doc URL (str)",
    )

    notify_task = Task(
        agent=notifier_agent,
        depends_on=doc_task,
        description="Send SMS + email with the URL.",
        expected_output="confirmation str",
    )

    all_tasks = [curate_task, research_task, compile_task, doc_task, notify_task]
    print(
        "[DEBUG] Crew tasks scheduled:",
        [agent_name(t.agent) for t in all_tasks],
        file=sys.stderr
    )
    return all_tasks

# ── run the crew ───────────────────────────────────────────────
if __name__ == "__main__":
    crew = Crew(tasks=define_tasks())
    print("[DEBUG] Dispatching Crew…", file=sys.stderr)

    # ① Try kickoff() first (it exists on your version)
    if hasattr(crew, "kickoff"):
        result = crew.kickoff()
    # ② Then try run()
    elif hasattr(crew, "run"):
        result = crew.run()
    # ③ Finally try execute()
    elif hasattr(crew, "execute"):
        result = crew.execute()
    else:
        raise AttributeError("Crew object has no kickoff/run/execute method!")

    print("[DEBUG] Crew returned →", result, file=sys.stderr)

    # fail build if no Google-Docs URL produced
    if not result or "docs.google.com/document" not in str(result):
        raise RuntimeError("❌  No Google Doc URL produced – aborting build.")

    logger.info("✅  Workflow finished, Doc URL: %s", result)
