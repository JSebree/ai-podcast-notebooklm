import os, requests
from datetime import datetime
from bs4 import BeautifulSoup

API_KEY = os.getenv("NEWSDATA_API_KEY")
if not API_KEY:
    raise EnvironmentError("Environment variable 'NEWSDATA_API_KEY' is not set.")

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
    try:
        response = requests.get(BASE_URL, params=params, timeout=30)
        response.raise_for_status()  # Ensure there are no HTTP errors
        res = response.json()  # Parse response only if status is OK
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
        return []  # Return an empty list on failure
    except ValueError:
        print("Error parsing JSON response")
        return []

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
        return first_p.text.strip()[:1000] if first_p else "Snippet not found."
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
    except Exception as e:
        print(f"Unexpected error while scraping {url}: {e}")
    return ""

# Optional: Retry mechanism with exponential backoff
import time

def fetch_with_retries(url, params, retries=3, backoff_factor=1):
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:  # Retry if attempts are left
                wait_time = backoff_factor * (2 ** attempt)
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"Failed after {retries} attempts: {e}")
                return None
