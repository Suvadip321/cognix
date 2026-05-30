"""Search service for finding relevant sources on the web."""

import asyncio
from tavily import AsyncTavilyClient
from backend.app.core.config import settings


async def search_web(questions: list[str]) -> list[dict]:
    """
    Search the web for a list of research questions.

    Args:
        questions: A list of research questions.

    Returns:
        A list of search results, each containing title, url, snippet, and score.
    """
    client = AsyncTavilyClient(api_key=settings.tavily_api_key)
    
    async def _search_single_query(query: str):
        try:
            response = await client.search(query=query, search_depth="basic", max_results=3)
            return response.get("results", [])
        except Exception as e:
            print(f"Search failed for query '{query}': {e}")
            return []

    tasks = [_search_single_query(q) for q in questions]
    all_results = await asyncio.gather(*tasks)
    
    final_results = []
    seen_urls = set()
    
    for results_group in all_results:
        for r in results_group:
            url = r.get("url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                final_results.append({
                    "title": r.get("title", ""),
                    "url": url,
                    "snippet": r.get("content", ""),
                    "score": r.get("score", 0.0)
                })
                
    return final_results
