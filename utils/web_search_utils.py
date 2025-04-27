import os, requests, time, sys
from datetime import datetime
from bs4 import BeautifulSoup

API_KEY = os.getenv("NEWSDATA_API_KEY")
if not API_KEY:
    raise RuntimeError("NEWSDATA_API_KEY env var is missing!")

BASE_URL   = "https://newsdata.io/api/1/news"
TECH_QUERY = "artificial intelligence OR quantum computing OR robotics"

# ──────────────────────────────────────────────────────────────
def fetch_top_news(max_items: int = 5):
    params = {
        "apikey": API_KEY,
        "language": "en",            # keep if you only want English
        "q": TECH_QUERY,
    }

    print("[DEBUG] Requesting Newsdata (key prefix:", API_KEY[:6], ")", file=sys.stderr)
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

    return [
        {"rank": i + 1, "title": art.get("title", "Untitled"), "url": art.get("link", "#")}
        for i, art in enumerate(results)
    ]


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
    except Exception as e:
        print(f"[DEBUG] Scrape error for {url} → {e}", file=sys.stderr)
        return ""
