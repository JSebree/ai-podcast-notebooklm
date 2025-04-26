from crewai import Agent, Task, Crew, Message
import agents.curator_agent as curator
import agents.researcher_agent as researcher
import agents.compiler_agent as compiler
import agents.doc_creator_agent as doc_creator
import agents.notifier_agent as notifier

# 1️⃣ Define agents
curator_agent   = curator.get_agent()
research_agent  = researcher.get_agent()
compiler_agent  = compiler.get_agent()
doc_agent       = doc_creator.get_agent()
notifier_agent  = notifier.get_agent()

# 2️⃣ Define tasks (each returns a Message)
curate_task   = Task(agent=curator_agent,   name="curate")
research_task = Task(agent=research_agent,  name="research",   depends_on=curate_task)
compile_task  = Task(agent=compiler_agent,  name="compile",    depends_on=research_task)
doc_task      = Task(agent=doc_agent,       name="gdoc",       depends_on=compile_task)
notify_task   = Task(agent=notifier_agent,  name="notify",     depends_on=doc_task)

# 3️⃣ Run crew
if __name__ == "__main__":
    crew = Crew(tasks=[notify_task])
    crew.run()
