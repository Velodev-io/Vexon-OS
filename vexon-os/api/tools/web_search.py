import os
from .registry import register_tool
try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None

@register_tool(
    name="web_search",
    description="Search the web for real-time information using DuckDuckGo. Returns a summary and source URLs.",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The search query"}
        },
        "required": ["query"]
    }
)
def web_search(query: str):
    if not DDGS:
        return {"content": "Error: duckduckgo-search package not installed.", "sources": []}
    
    try:
        # Use the latest DDGS text search with a broad region
        with DDGS() as ddgs:
            # We use 'wt-wt' for worldwide results to ensure maximum coverage
            ddgs_gen = ddgs.text(query, region='wt-wt', safesearch='off', timelimit='y')
            results = []
            for r in ddgs_gen:
                results.append(r)
                if len(results) >= 5:
                    break
                    
            if not results:
                # Fallback: try without recency filter if 'y' (year) returned nothing
                ddgs_gen = ddgs.text(query, region='wt-wt', safesearch='off')
                for r in ddgs_gen:
                    results.append(r)
                    if len(results) >= 5:
                        break

            if not results:
                return {"content": "No results found for the query.", "sources": []}
            
            # Filter out known spam/shopping domains to keep research high-quality
            ignored_domains = ["batterygod.com", "amazon.", "ebay.", "flipkart.", "indiamart."]
            filtered_results = [r for r in results if not any(domain in r.get('href', '').lower() for domain in ignored_domains)]
            
            # If everything was filtered, keep at least the top one, otherwise use filtered list
            final_results = filtered_results if filtered_results else results[:1]
            
            content = "\n\n".join([f"Source: {r['title']}\nContent: {r['body']}" for r in final_results])
            sources = [r['href'] for r in final_results]
            
            return {"content": content, "sources": sources}
    except Exception as e:
        return {"content": f"Error performing web search: {str(e)}", "sources": []}
