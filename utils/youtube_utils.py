import os
import requests
import logging

logger = logging.getLogger(__name__)
API_KEY = os.getenv("YOUTUBE_API_KEY")
BASE_URL = "https://www.googleapis.com/youtube/v3/search"

def search_videos(query: str, max_results: int = 1) -> list[dict]:
    """
    Query the YouTube Data API v3 for videos matching `query`.
    Returns a list of {"url": ..., "title": ...}.
    """
    if not API_KEY:
        raise RuntimeError("YOUTUBE_API_KEY environment variable is not set.")
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "key": API_KEY,
    }
    resp = requests.get(BASE_URL, params=params, timeout=30)
    resp.raise_for_status()
    items = resp.json().get("items", [])
    results = []
    for item in items:
        vid = item["id"]["videoId"]
        title = item["snippet"]["title"]
        results.append({
            "url": f"https://www.youtube.com/watch?v={vid}",
            "title": title
        })
    return results
