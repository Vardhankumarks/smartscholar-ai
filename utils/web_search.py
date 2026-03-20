from ddgs import DDGS

from config.config import MAX_SEARCH_RESULTS


def web_search(query, max_results=MAX_SEARCH_RESULTS):
    """Perform a live web search using DuckDuckGo and return formatted results."""
    try:
        ddgs = DDGS()
        results = list(ddgs.text(query, max_results=max_results))

        formatted = []
        for r in results:
            formatted.append({
                "title": r.get("title", ""),
                "body": r.get("body", ""),
                "url": r.get("href", ""),
            })
        return formatted
    except Exception as e:
        raise RuntimeError(f"Web search failed: {e}")


def format_search_results(results):
    """Convert search results into a readable context string for the LLM."""
    if not results:
        return ""

    lines = ["Web Search Results:\n"]
    for i, r in enumerate(results, 1):
        lines.append(f"{i}. {r['title']}")
        lines.append(f"   {r['body']}")
        lines.append(f"   Source: {r['url']}\n")

    return "\n".join(lines)
