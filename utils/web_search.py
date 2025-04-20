import os
import requests
from dotenv import load_dotenv

load_dotenv()

SERP_API_KEY = os.getenv("SERPAPI_API_KEY")

def simple_web_search(query: str, max_results: int = 3) -> str:
    """
    Uses SerpAPI to fetch web results. Requires SERPAPI_API_KEY in .env.
    """
    try:
        url = "https://serpapi.com/search"
        params = {
            "q": query,
            "api_key": SERP_API_KEY,
            "num": max_results,
            "engine": "google"
        }
        res = requests.get(url, params=params, timeout=8)
        res.raise_for_status()
        data = res.json()

        snippets = []
        for result in data.get("organic_results", []):
            snippet = result.get("snippet") or result.get("title")
            if snippet:
                snippets.append(snippet)

        return "\n".join(snippets[:max_results]) or "No relevant web results found."
    except Exception as e:
        return f"Web search error: {e}"
