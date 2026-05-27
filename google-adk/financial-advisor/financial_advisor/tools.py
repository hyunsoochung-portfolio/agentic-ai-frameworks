"""Web search tool for the News Analyst sub-agent.

The blog posts describe the News Analyst using a Firecrawl-based web search
tool (firecrawl-py is listed in the project dependencies), but the exact
source of this helper was not published. This is a best-effort
reconstruction following Firecrawl's documented search API so the agent can
be wired up end to end. Set FIRECRAWL_API_KEY in your environment.
"""

import os

from firecrawl import FirecrawlApp


def web_search_tool(query: str) -> dict:
    """
    Searches the web for current news and information using Firecrawl.

    Args:
        query (str): Search query (e.g., "Apple AAPL latest earnings news").

    Returns:
        dict: A dictionary containing:
            - query (str): The input search query
            - success (bool): True if the search completed
            - results (list): List of search results with title, url, and snippet
    """
    app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
    response = app.search(query)

    results = []
    for item in getattr(response, "data", []) or []:
        results.append(
            {
                "title": item.get("title"),
                "url": item.get("url"),
                "snippet": item.get("description") or item.get("markdown", "")[:500],
            }
        )

    return {
        "query": query,
        "success": True,
        "results": results,
    }
