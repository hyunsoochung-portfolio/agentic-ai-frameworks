import os
import re

from crewai.tools import tool
from firecrawl import FirecrawlApp, ScrapeOptions


@tool
def web_search_tool(query: str):
    """
    web search tool.
    args:
        query: str
            the query to search web for
        returns
            a list of search results with the website content in markdown format
    """
    app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
    response = app.search(
        query=query,
        limit=1,
        scrape_options=ScrapeOptions(
            formats=["markdown"]
        ),
    )
    if not response.success:
        return "ERROR using tool"

    cleaned_chunks = []
    for result in response.data:
        title = result["title"]
        url = result["url"]
        markdown = result["markdown"]
        cleaned = re.sub(r"\\+|\n+", "", markdown).strip()
        cleaned = re.sub(r"\[[^\]]+\]\([^\)]+\)|https?://[^\s]+", "", cleaned)
        cleaned_result = {
            "title": title,
            "url": url,
            "markdown": cleaned,
        }
        cleaned_chunks.append(cleaned_result)
    return cleaned_chunks
