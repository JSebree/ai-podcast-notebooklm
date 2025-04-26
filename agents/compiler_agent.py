from crewai import Agent, Message

def get_agent():
    return Agent(
        name="CompilerAgent",
        sys_prompt="""Create a full‑paragraph summary (≈6 sentences) for each story, plus a 1‑line catchy podcast episode title.""",
        fn=run
    )

def run(msg: Message):
    compiled = []
    for story in msg.content:
        compiled.append({
            "headline": story["title"],
            "podcast_title": generate_podcast_title(story["title"]),
            "summary": summarize(story),
            "links": story["links"]
        })
    return Message(content=compiled)

# -- helper stubs (use your LLM or simple heuristic) --
from openai import OpenAI
client = OpenAI()

def generate_podcast_title(title):
    prompt = f"Write a punchy podcast episode title (under 12 words) summarizing: {title}"
    return client.chat.completions.create(model="gpt-4o", messages=[{"role":"user","content":prompt}]).choices[0].message.content.strip()

def summarize(story):
    context = story.get("article_snippet","")
    prompt = f"Provide a 6‑sentence journalistic summary of the following tech news:\n{context}"
    return client.chat.completions.create(model="gpt-4o", messages=[{"role":"user","content":prompt}]).choices[0].message.content.strip()
