from duckduckgo_search import DDGS

def simple_web_search(query: str, max_results: int = 3) -> str:
    """
    Uses duckduckgo-search to perform live search without API keys.
    Returns top result snippets.
    """
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=max_results)
            snippets = [res["body"] for res in results if "body" in res]
            return "\n".join(snippets[:max_results]) if snippets else "No web results found."
    except Exception as e:
        return f"Web search error: {e}"
