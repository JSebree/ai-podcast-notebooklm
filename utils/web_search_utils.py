import os, requests, datetime, json
from bs4 import BeautifulSoup

SERP_API = os.getenv("SERPAPI_KEY")

# --- Step 1: fetch headlines ---

def fetch_top_news(max_items=5):
    today = datetime.datetime.utcnow()
    params = {
        "engine": "google_news",
        "q": "(artificial intelligence OR quantum computing OR robotics)",
        "sort_by": "date",
        "num": max_items,
        "api_key": SERP_API
    }
    res = requests.get("https://serpapi.com/search.json", params=params, timeout=30).json()
    stories = []
    for i,news in enumerate(res.get("news_results", [])[:max_items]):
        stories.append({"rank": i+1, "title": news["title"], "url": news["link"]})
    return stories

# --- Step 2: enrich with supporting links ---

def enrich_story(story):
    # Placeholder: add real scraping/APIs for YouTube, Twitter, LinkedIn
    links = [story["url"]]
    # TODO: call YouTube & social APIs here, append
    story["links"] = links
    story["article_snippet"] = scrape_snippet(story["url"])
    return story


def scrape_snippet(url):
    try:
        html = requests.get(url, timeout=20, headers={"User-Agent":"Mozilla/5.0"}).text
        soup = BeautifulSoup(html, "html.parser")
        p = soup.find("p")
        return p.text.strip()[:1000]
    except Exception:
        return ""
