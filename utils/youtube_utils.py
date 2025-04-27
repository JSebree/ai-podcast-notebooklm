import os
import requests
import logging

logger = logging.getLogger(__name__)
API_KEY = os.getenv("YOUTUBE_API_KEY")
BASE_URL = "https://www.googleapis.com/youtube/v3/search"

def search_videos(query: str, max_results: int = 1) -> list[dict]:
    """
    Query the YouTube Data API v3 for videos matching `query` plus context
    keywords (space-separated, no OR). Returns [{"url":..., "title":...}].
    """
    if not API_KEY:
        raise RuntimeError("YOUTUBE_API_KEY environment variable is not set.")

    # Append context keywords without boolean operators
    context = "artificial intelligence quantum computing robotics"
    full_query = f"{query} {context}"

    params = {
        "part":             "snippet",
        "q":                full_query,
        "type":             "video",
        "maxResults":       max_results,
        "relevanceLanguage":"en",
        "videoEmbeddable":  "true",
        "key":              API_KEY,
    }

    logger.debug("YouTube.search: %s", {k: params[k] for k in ("q","maxResults","relevanceLanguage")})

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
