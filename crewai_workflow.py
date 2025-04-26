from crewai import Agent, Task, Crew

# --- import agent factories ---
from agents.curator_agent import get_agent as curator
from agents.researcher_agent import get_agent as researcher
from agents.compiler_agent import get_agent as compiler
from agents.doc_creator_agent import get_agent as doc_creator
from agents.notifier_agent import get_agent as notifier

# --- instantiate agents ---
curator_agent   = curator()
research_agent  = researcher()
compiler_agent  = compiler()
doc_agent       = doc_creator()
notifier_agent  = notifier()

# --- define tasks with required fields ---
curate_task = Task(
    agent=curator_agent,
    description="Select the top five breaking stories in AI, quantum computing, and robotics from the last 24 hours.",
    expected_output="A list of 5 dict objects, each with keys: rank, title, url.",
)

research_task = Task(
    agent=research_agent,
    depends_on=curate_task,
    description="Enrich each story with 3-5 supporting links (articles, YouTube, Twitter/LinkedIn) and a short snippet.",
    expected_output="The same list of 5 dicts, each now containing 'links' and 'article_snippet'.",
)

compile_task = Task(
    agent=compiler_agent,
    depends_on=research_task,
    description="Generate a one-paragraph summary and a podcast-ready title for each enriched story.",
    expected_output="A list of 5 dicts, each with keys: headline, podcast_title, summary, links.",
)

doc_task = Task(
    agent=doc_agent,
    depends_on=compile_task,
    description="Create a formatted Google Doc for today containing the compiled digest and return its URL.",
    expected_output="A string containing the public link to the new Google Doc.",
)

notify_task = Task(
    agent=notifier_agent,
    depends_on=doc_task,
    description="Send an SMS via Twilio and a fallback email with the Google Doc link.",
    expected_output="String confirmation that notifications were dispatched.",
)

# ── run the crew ────────────────────────────────────────────
if __name__ == "__main__":
    crew = Crew(tasks=[notify_task])

    # Try the modern method first; fall back if needed
    if hasattr(crew, "kickoff"):
        crew.kickoff()
    else:
        crew.execute()
