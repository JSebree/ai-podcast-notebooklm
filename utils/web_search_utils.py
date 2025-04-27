import os, requests, time
from datetime import datetime
from bs4 import BeautifulSoup
import sys

API_KEY = os.getenv("NEWSDATA_API_KEY")
print("[DEBUG] NEWSDATA_API_KEY seen by Python:", repr(API_KEY)[:20], file=sys.stderr)

if not API_KEY:
    raise EnvironmentError("Environment variable 'NEWSDATA_API_KEY' is not set!")

BASE_URL   = "https://newsdata.io/api/1/news"
TECH_QUERY = "artificial intelligence OR quantum computing OR robotics"

# ──────────────────────────────────────────────────────────
# 1️⃣ Pull the 5 most recent tech headlines (past 24 h)
# ──────────────────────────────────────────────────────────
def fetch_top_news(max_items: int = 5):
    params = {
        "apikey": API_KEY,
        "language": "en",
        "category": "technology",
        "q": TECH_QUERY,
        "page": 0,
    }

    print("[DEBUG] fetch_top_news() calling Newsdata…", file=sys.stderr)
    try:
        resp = requests.get(BASE_URL, params=params, timeout=30)
        print("[DEBUG] Newsdata HTTP status:", resp.status_code, file=sys.stderr)
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.RequestException as err:
        print("[DEBUG] Newsdata request failed →", err, file=sys.stderr)
        return []

    results = data.get("results", [])[:max_items]
    print("[DEBUG] Newsdata returned", len(results), "articles", file=sys.stderr)

    stories = [
        {"rank": i + 1, "title": art.get("title", "Untitled"), "url": art.get("link", "#")}
        for i, art in enumerate(results)
    ]
    return stories


# ──────────────────────────────────────────────────────────
# 2️⃣ Enrich story with snippet + placeholder links
# ──────────────────────────────────────────────────────────
def enrich_story(story: dict):
    story["article_snippet"] = scrape_snippet(story["url"])
    story.setdefault("links", []).append(story["url"])
    return story


def scrape_snippet(url: str) -> str:
    try:
        html = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"}).text
        soup = BeautifulSoup(html, "html.parser")
        first_p = soup.find("p")
        return first_p.text.strip()[:1000] if first_p else "Snippet not found."
    except requests.exceptions.RequestException as e:
        print(f"[DEBUG] Error fetching URL {url}: {e}", file=sys.stderr)
    except Exception as e:
        print(f"[DEBUG] Unexpected error scraping {url}: {e}", file=sys.stderr)
    return ""


# ──────────────────────────────────────────────────────────
# Optional: retry helper with exponential back-off
#
