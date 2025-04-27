import os
import requests
import logging

logger = logging.getLogger(__name__)

TWITTER_SEARCH_URL = "https://api.twitter.com/2/tweets/search/recent"

def search_twitter(query: str, max_results: int = 1) -> list[dict]:
    """
    Search recent tweets for `query`. Returns list of {"url": tweet_url}.
    Silently skips if rate-limited (HTTP 429).
    """
    bearer = os.getenv("TWITTER_BEARER_TOKEN")
    if not bearer:
        raise RuntimeError("TWITTER_BEARER_TOKEN environment variable is not set.")

    headers = {"Authorization": f"Bearer {bearer}"}
    params = {
        "query": query,
        "max_results": max_results,
        "tweet.fields": "id"
    }

    try:
        resp = requests.get(TWITTER_SEARCH_URL, headers=headers, params=params, timeout=30)
        if resp.status_code == 429:
            logger.info("Twitter rate limit hit; skipping Twitter links")
            return []
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.warning("Twitter lookup failed: %s", e)
        return []

    data = resp.json().get("data", [])
    return [{"url": f"https://twitter.com/i/web/status/{t['id']}"} for t in data]


def search_linkedin(query: str, max_results: int = 1) -> list[dict]:
    """
    LinkedIn scraping not implemented—return empty silently.
    """
    return []
