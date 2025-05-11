import functools
import io
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

# cairosvg import (convert SVG to PNG if available)
try:
    import cairosvg
except ImportError:
    cairosvg = None
# ColorThief import
try:
    from colorthief import ColorThief
except ImportError:
    ColorThief = None

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

@Node(retries=3)
def AssetsNode(page_url: str) -> dict:
    """
    Return a dict with keys 'logo_url' and 'palette' (list of HEX strings).
    """
    try:
        resp = httpx.get(page_url, timeout=10.0)
        resp.raise_for_status()
        html = resp.text
    except Exception:
        return {'logo_url': None, 'palette': []}
    soup = BeautifulSoup(html, 'html.parser')
    # Possible selectors in priority order
    selectors = [
        ('meta', {'property': 'og:image'}, 'content'),
        ('link', {'rel': 'icon'}, 'href'),
        ('link', {'rel': 'shortcut icon'}, 'href'),
        ('link', {'rel': 'apple-touch-icon'}, 'href'),
    ]
    logo = None
    for tag, attrs, attr in selectors:
        el = soup.find(tag, attrs=attrs)
        if el and el.get(attr):
            logo = urljoin(page_url, el.get(attr))
            break
    palette = []
    if logo and ColorThief:
        try:
            img_resp = httpx.get(logo, timeout=10.0)
            img_resp.raise_for_status()
            data = img_resp.content
            content_type = img_resp.headers.get('Content-Type', '')
            # Convert SVG to PNG if needed
            if cairosvg and ('svg' in content_type or logo.lower().endswith('.svg')):
                try:
                    data = cairosvg.svg2png(bytestring=data)
                except Exception:
                    pass
            # Extract palette
            buf = io.BytesIO(data)
            ct = ColorThief(buf)
            colors = ct.get_palette(color_count=5)
            # Convert to HEX and uppercase
            palette = [f"#{r:02X}{g:02X}{b:02X}" for r, g, b in colors]
        except Exception:
            palette = []
    return {'logo_url': logo, 'palette': palette}