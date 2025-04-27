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

def agent_name(agent):
    return getattr(getattr(agent, "profile", None), "name", repr(agent))

# ── define tasks ───────────────────────────────────────────────
def define_tasks():
    curate = Task(agent=curator_agent, description="Pick top 5 stories", expected_output="list[dict]")
    research = Task(agent=research_agent, depends_on=curate, description="Enrich stories", expected_output="list[dict]")
    compile_ = Task(agent=compiler_agent, depends_on=research, description="Compile summaries", expected_output="list[dict]")
    doc = Task(agent=doc_agent, depends_on=compile_, description="Create Google Doc", expected_output="str")
    notify = Task(agent=notifier_agent, depends_on=doc, description="Notify user", expected_output="str")

    tasks = [curate, research, compile_, doc, notify]
    print("[DEBUG] Crew tasks scheduled →", [agent_name(t.agent) for t in tasks], file=sys.stderr)
    return tasks

# ── run the crew ───────────────────────────────────────────────
if __name__ == "__main__":
    crew = Crew(tasks=define_tasks())
    print("[DEBUG] Dispatching Crew with kickoff()", file=sys.stderr)

    # *** Use kickoff() directly ***
    result = crew.kickoff()

    print("[DEBUG] Crew returned →", result, file=sys.stderr)

    # Fail fast if no Docs URL
    if not result or "docs.google.com/document" not in str(result):
        raise RuntimeError("❌ No Google Doc URL produced – aborting build.")

    logger.info("✅ Workflow complete, Doc URL: %s", result)
