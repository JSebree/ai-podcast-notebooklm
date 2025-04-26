from crewai import Agent, Task, Crew

# ——— import factory functions for each agent ———
from agents.curator_agent import get_agent as curator
from agents.researcher_agent import get_agent as researcher
from agents.compiler_agent import get_agent as compiler
from agents.doc_creator_agent import get_agent as doc_creator
from agents.notifier_agent import get_agent as notifier

# instantiate agents
curator_agent   = curator()
research_agent  = researcher()
compiler_agent  = compiler()
doc_agent       = doc_creator()
notifier_agent  = notifier()

# define tasks (data passed as plain Python objects between them)
curate_task   = Task(agent=curator_agent)                      # returns list[dict]
research_task = Task(agent=research_agent,  depends_on=curate_task)   # returns enriched list
compile_task  = Task(agent=compiler_agent,  depends_on=research_task)  # returns compiled list
create_doc    = Task(agent=doc_agent,       depends_on=compile_task)   # returns str (Doc URL)
notify_task   = Task(agent=notifier_agent,  depends_on=create_doc)     # final step

if __name__ == "__main__":
    Crew(tasks=[notify_task]).run()
