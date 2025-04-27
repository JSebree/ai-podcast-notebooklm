import os
import requests
import logging

logger = logging.getLogger(__name__)
API_KEY = os.getenv("YOUTUBE_API_KEY")
BASE_URL = "https://www.googleapis.com/youtube/v3/search"

def search_videos(query: str, max_results: int = 1) -> list[dict]:
    """
    Query the YouTube Data API v3 for videos matching `query`, plus
    context keywords to hone in on AI/quantum/robotics content.
    Returns a list of {"url": ..., "title": ...}.
    """
    if not API_KEY:
        raise RuntimeError("YOUTUBE_API_KEY environment variable is not set.")

    # 1) Append context keywords
    context = "artificial intelligence OR quantum computing OR robotics"
    full_query = f"{query} {context}"

    params = {
        "part":             "snippet",
        "q":                full_query,
        "type":             "video",
        "maxResults":       max_results,
        "relevanceLanguage":"en",        # favor English‐language results
        "videoEmbeddable":  "true",      # only embeddable videos
        "key":              API_KEY,
    }

    logger.debug("YouTube search params: %s", {k: params[k] for k in ("q","maxResults","relevanceLanguage")})

    resp = requests.get(BASE_URL, params=params, timeout=30)
    resp.raise_for_status()
    items = resp.json().get("items", [])

    results = []
    for item in items:
        vid   = item["id"]["videoId"]
        title = item["snippet"]["title"]
        results.append({
            "url":   f"https://www.youtube.com/watch?v={vid}",
            "title": title,
        })

    logger.debug("YouTube returned %d videos", len(results))
    return results
