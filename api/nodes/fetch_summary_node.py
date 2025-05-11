import functools
import httpx
from html.parser import HTMLParser

# Node decorator with retry logic
class Node:
    def __init__(self, retries=0):
        self.retries = retries

    def __call__(self, fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            last_exc = None
            for _ in range(self.retries):
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    last_exc = e
            if last_exc is not None:
                raise last_exc
            return fn(*args, **kwargs)

        wrapper.__wrapped__ = fn
        return wrapper

# HTML text extraction (use BeautifulSoup if available, else fallback)
class _HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self._parts = []

    def handle_data(self, data):
        self._parts.append(data)

    def get_text(self):
        return ''.join(self._parts)

try:
    from bs4 import BeautifulSoup  # type: ignore

    def _extract_text(html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        return " ".join(soup.stripped_strings)
except ImportError:
    def _extract_text(html: str) -> str:
        parser = _HTMLTextExtractor()
        parser.feed(html)
        text = parser.get_text()
        # collapse whitespace
        return " ".join(text.split())

@Node(retries=3)
def FetchSummaryNode(url: str) -> str:
    """
    Fetch HTML content from the given URL, extract plain text,
    truncate to 4000 characters, and return.
    Retries up to `retries` times on network or HTTP errors.
    """
    # First, attempt to fetch via OpenAI WebSearch tool if available
    try:
        import openai
        # Use OpenAI WebSearch API to get page snippets
        ws = openai.WebSearch.create(query=url)
        snippets = []
        # Try common attributes for results
        if hasattr(ws, 'data'):
            for item in ws.data:
                snippets.append(item.get('text') or item.get('snippet') or '')
        elif hasattr(ws, 'web_pages'):
            for item in ws.web_pages:
                snippets.append(item.get('snippet') or item.get('text') or '')
        oa_text = ' '.join(filter(None, snippets))
        if oa_text:
            return oa_text[:4000]
    except Exception:
        # Fallback to direct HTTP fetch if OpenAI tool unavailable or fails
        pass
    # Fallback: fetch HTML, parse and truncate
    response = httpx.get(url, timeout=10.0)
    response.raise_for_status()
    text = _extract_text(response.text)
    return text[:4000]