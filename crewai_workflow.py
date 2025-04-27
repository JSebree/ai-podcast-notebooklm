import logging, sys
from crewai import Agent, Task, Crew
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

    # ▶ return **all** tasks so CrewAI executes the full chain
    all_tasks = [curate_task, research_task, compile_task, doc_task, notify_task]
    print("[DEBUG] Crew tasks scheduled:", [t.agent.name for t in all_tasks], file=sys.stderr)
    return all_tasks

# ── run the crew ───────────────────────────────────────────────
if __name__ == "__main__":
    crew = Crew(tasks=define_tasks())

    # kickoff() for latest CrewAI, fallback to execute()
    run_fn = crew.kickoff if hasattr(crew, "kickoff") else crew.execute
    result = run_fn()

    # 🔴 fail build if no Google-Docs URL produced
    if not result or "docs.google.com/document" not in str(result):
        raise RuntimeError("❌  No Google Doc URL produced – aborting build.")

    logger.info("✅  Workflow finished, Doc URL: %s", result)
