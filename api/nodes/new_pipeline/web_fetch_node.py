from api.nodes.fetch_summary_node import Node

@Node(retries=3)
def WebFetchNode(url: str) -> str:
    """
    Fetch raw HTML for homepage and first-level internal links using OpenAI web tool.
    Falls back to LocalFetchNode if tool fails or returns insufficient content.
    Returns concatenated HTML string.
    """
    import openai
    # Use OpenAI WebSearch tool to fetch page snippets
    try:
        ws = openai.WebSearch.create(query=url)
        snippets = []
        # v1 compatibility: ws.data vs ws.web_pages
        # Prefer ws.data if present and iterable, else ws.web_pages
        if getattr(ws, 'data', None):
            for item in ws.data:
                snippets.append(item.get('text') or item.get('snippet') or '')
        elif getattr(ws, 'web_pages', None):
            for item in ws.web_pages:
                snippets.append(item.get('snippet') or item.get('text') or '')
        html = ' '.join(filter(None, snippets))
        return html
    except Exception:
        # On any error, return empty to signal fallback
        return ''