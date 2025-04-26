import os, requests
from datetime import datetime
from bs4 import BeautifulSoup

API_KEY = os.getenv("NEWSDATA_API_KEY")
BASE_URL = "https://newsdata.io/api/1/news"

TECH_QUERY = "artificial intelligence OR quantum computing OR robotics"

# 1️⃣  Pull the 5 most recent tech headlines (past 24 h)

def fetch_top_news(max_items: int = 5):
    params = {
        "apikey": API_KEY,
        "language": "en",
        "category": "technology",
        "q": TECH_QUERY,
        "page": 0
    }
    res = requests.get(BASE_URL, params=params, timeout=30).json()
    stories = []
    for i, art in enumerate(res.get("results", [])[:max_items]):
        stories.append({
            "rank": i + 1,
            "title": art.get("title", "Untitled"),
            "url": art.get("link", "#"),
        })
    return stories

# 2️⃣  Enrich each story with snippet + placeholder links (YouTube, social scraped elsewhere)

def enrich_story(story: dict):
    story["article_snippet"] = scrape_snippet(story["url"])
    story.setdefault("links", []).append(story["url"])
    return story


def scrape_snippet(url: str) -> str:
    try:
        html = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"}).text
        soup = BeautifulSoup(html, "html.parser")
        first_p = soup.find("p")
        return first_p.text.strip()[:1000]
    except Exception:
        return ""
