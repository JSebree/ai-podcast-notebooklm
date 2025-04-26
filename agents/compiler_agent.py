from crewai import Agent
import os
from openai import OpenAI

# Initialize OpenAI client with secret key from env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PROMPT_TITLE = "Write a punchy podcast episode title (under 12 words) summarizing: "
PROMPT_SUMMARY = "Provide a 6-sentence journalistic summary of the following tech news: "

def get_agent():
    return Agent(
        name="CompilerAgent",
        description="Create a full‑paragraph summary and a 1‑line podcast title for each story.",
        run=run
    )

def run(stories: list[dict]):
    compiled = []
    for story in stories:
        title_prompt   = PROMPT_TITLE + story["title"]
        summary_prompt = PROMPT_SUMMARY + (story.get("article_snippet") or story["title"])

        podcast_title = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": title_prompt}]
        ).choices[0].message.content.strip()

        summary = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": summary_prompt}]
        ).choices[0].message.content.strip()

        compiled.append({
            "headline": story["title"],
            "podcast_title": podcast_title,
            "summary": summary,
            "links": story["links"],
        })
    return compiled  # list[dict]
