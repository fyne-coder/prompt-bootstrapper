from api.nodes.fetch_summary_node import Node

@Node(retries=3)
def LocalFetchNode(url: str) -> str:
    """
    Fetch raw HTML using requests + BeautifulSoup as fallback.
    Should trigger when WebFetchNode fails or returns <500 chars.
    Returns concatenated HTML string.
    """
    import httpx
    # Fallback fetch via HTTP and return raw HTML
    resp = httpx.get(url, timeout=10.0)
    resp.raise_for_status()
    return resp.text