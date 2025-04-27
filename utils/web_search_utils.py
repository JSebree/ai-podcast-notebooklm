import os
import requests
import logging
from datetime import datetime
from bs4 import BeautifulSoup
from utils.youtube_utils import search_videos
from utils.social_utils import search_twitter, search_linkedin

logger = logging.getLogger(__name__)
API_KEY = os.getenv("NEWSDATA_API_KEY")
BASE_URL = "https://newsdata.io/api/1/news"
TECH_QUERY = "artificial intelligence OR AI OR quantum computing OR robotics"

def fetch_top_news(max_items: int = 5) -> list[dict]:
    params = {
        "apikey": API_KEY,
        "language": "en",
        "q": TECH_QUERY,
    }
    try:
        resp = requests.get(BASE_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        logger.error("Newsdata fetch failed: %s", e)
        return []

    results = data.get("results", [])[:max_items]
    return [
        {"rank": i+1, "title": art.get("title", "Untitled"), "url": art.get("link", "#")}
        for i, art in enumerate(results)
    ]

def scrape_snippet(url: str) -> str:
    try:
        html = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=20).text
        soup = BeautifulSoup(html, "html.parser")
        p = soup.find("p")
        return p.text.strip()[:1000] if p else ""
    except Exception as e:
        logger.warning("Snippet scrape failed for %s: %s", url, e)
        return ""

def enrich_story(story: dict) -> dict:
    """
    Build story["links"] to include:
      1. original article URL
      2. related articles
      3. YouTube videos
      4. tweets/ X posts
      5. LinkedIn posts (stubbed)
    """
    links = [story["url"]]
    title = story.get("title", "")

    # 1) Related articles (up to 2)
    params = {"apikey": API_KEY, "language": "en", "q": title}
    try:
        resp = requests.get(BASE_URL, params=params, timeout=15)
        resp.raise_for_status()
        for art in resp.json().get("results", []):
            url = art.get("link")
            if url and url not in links:
                links.append(url)
            if len(links) >= 3:
                break
    except Exception as e:
        logger.warning("Related articles lookup failed: %s", e)

    # 2) YouTube
    try:
        vids = search_videos(title, max_results=1)
        for v in vids:
            if v["url"] not in links:
                links.append(v["url"])
    except Exception as e:
        logger.warning("YouTube lookup failed: %s", e)

    # 3) Twitter
    try:
        tweets = search_twitter(title, max_results=1)
        for t in tweets:
            if t["url"] not in links:
                links.append(t["url"])
    except Exception as e:
        logger.warning("Twitter lookup failed: %s", e)

    # 4) LinkedIn
    try:
        posts = search_linkedin(title, max_results=1)
        for p in posts:
            if p["url"] not in links:
                links.append(p["url"])
    except Exception as e:
        logger.warning("LinkedIn lookup failed: %s", e)

    # Dedupe and cap at 5
    seen = set()
    final = []
    for u in links:
        if u not in seen:
            final.append(u)
            seen.add(u)
        if len(final) == 5:
            break

    # snippet
    story["article_snippet"] = scrape_snippet(story["url"])
    story["links"] = final
    return story
