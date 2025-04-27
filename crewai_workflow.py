import logging, sys
from crewai import Task, Crew
from agents.curator_agent import get_agent as curator
from agents.researcher_agent import get_agent as researcher
from agents.compiler_agent import get_agent as compiler
from agents.doc_creator_agent import get_agent as doc_creator
from agents.notifier_agent import get_agent as notifier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
print("[DEBUG] crewai_workflow starting", file=sys.stderr)

# Instantiate agents
curator_agent   = curator()
research_agent  = researcher()
compiler_agent  = compiler()
doc_agent       = doc_creator()
notifier_agent  = notifier()

def agent_name(agent):
    return getattr(getattr(agent, "profile", None), "name", repr(agent))

def define_tasks():
    curate_task = Task(agent=curator_agent, description="Pick top 5 stories", expected_output="list[dict]")
    research_task = Task(agent=research_agent, depends_on=curate_task, description="Enrich stories", expected_output="list[dict]")
    compile_task = Task(agent=compiler_agent, depends_on=research_task, description="Compile summaries", expected_output="list[dict]")
    doc_task = Task(agent=doc_agent, depends_on=compile_task, description="Create Google Doc", expected_output="str")
    notify_task = Task(agent=notifier_agent, depends_on=doc_task, description="Notify user", expected_output="str")

    all_tasks = [curate_task, research_task, compile_task, doc_task, notify_task]
    print("[DEBUG] Crew tasks scheduled →", [agent_name(t.agent) for t in all_tasks], file=sys.stderr)
    return all_tasks

if __name__ == "__main__":
    crew = Crew(tasks=define_tasks())
    print("[DEBUG] Running Crew…", file=sys.stderr)

    # Always use run(), fallback to execute()
    if hasattr(crew, "run"):
        result = crew.run()
    else:
        result = crew.execute()

    print("[DEBUG] Crew returned →", result, file=sys.stderr)

    # Fail if no Google Doc URL
    if not result or "docs.google.com/document" not in str(result):
        raise RuntimeError("❌ No Google Doc URL produced – aborting build.")

    logger.info("✅ Workflow complete, Doc URL: %s", result)
