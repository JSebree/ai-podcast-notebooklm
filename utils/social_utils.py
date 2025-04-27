import os
import requests
import logging

logger = logging.getLogger(__name__)

# Twitter API v2 recent search
TWITTER_SEARCH_URL = "https://api.twitter.com/2/tweets/search/recent"

def search_twitter(query: str, max_results: int = 1) -> list[dict]:
    """
    Search recent tweets for `query`. Returns list of {"url": tweet_url}.
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
    resp = requests.get(TWITTER_SEARCH_URL, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json().get("data", [])
    results = []
    for tweet in data:
        tid = tweet["id"]
        results.append({"url": f"https://twitter.com/i/web/status/{tid}"})
    return results

def search_linkedin(query: str, max_results: int = 1) -> list[dict]:
    """
    Stub for LinkedIn posts. Currently not implemented.
    """
    logger.warning("LinkedIn search not implemented; returning empty list")
    return []
