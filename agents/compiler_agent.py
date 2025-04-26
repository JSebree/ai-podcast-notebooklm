import os
from crewai import Agent
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PROMPT_TITLE = (
    "Write a punchy podcast episode title (under 12 words) summarizing: "
)
PROMPT_SUMMARY = (
    "Provide a 6-sentence journalistic summary of the following tech news:\n"
)


def get_agent():
    return Agent(
        name="CompilerAgent",
        role="Tech Digest Writer",
        goal=(
            "Turn enriched stories into a one-paragraph summary and a catchy "
            "podcast title for each item."
        ),
        backstory=(
            "You distill complex technical developments into clear, engaging "
            "copy that busy audiences can grasp quickly."
        ),
        run=run,
    )


def run(stories: list[dict]):
    compiled = []

    for story in stories:
        # --- generate podcast title ---
        title_prompt = PROMPT_TITLE + story["title"]
        podcast_title = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": title_prompt}],
        ).choices[0].message.content.strip()

        # --- generate summary ---
        context = story.get("article_snippet") or story["title"]
        summary_prompt = PROMPT_SUMMARY + context
        summary = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": summary_prompt}],
        ).choices[0].message.content.strip()

        compiled.append(
            {
                "headline": story["title"],
                "podcast_title": podcast_title,
                "summary": summary,
                "links": story["links"],
            }
        )

    return compiled
