"""
LocalFetchNode
---------------
Fetch HTML with realistic browser headers. Falls back gracefully if http2
support (h2 package) is not installed.
"""
from api.nodes.fetch_summary_node import Node

@Node(retries=1)
def LocalFetchNode(url: str) -> str:
    import httpx, random, importlib

    _UAS = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) "
        "Gecko/20100101 Firefox/125.0",
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    ]

    headers = {
        "User-Agent": random.choice(_UAS),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    # Enable HTTP/2 only if the optional h2 library is present
    http2_supported = importlib.util.find_spec("h2") is not None

    with httpx.Client(
        headers=headers,
        follow_redirects=True,
        timeout=15.0,
        http2=http2_supported,
    ) as client:
        resp = client.get(url)
        resp.raise_for_status()      # bubble up 4xx/5xx to PocketFlow
        return resp.text
