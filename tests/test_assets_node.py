import types
import io

import pytest

import httpx
from api.nodes.assets_node import AssetsNode

class DummyHTMLResponse:
    def __init__(self, text):
        self.text = text
        self.status_code = 200
        self.headers = {'Content-Type': 'text/html'}
    def raise_for_status(self):
        pass

class DummyImageResponse:
    def __init__(self, content, headers=None):
        self.content = content
        self.status_code = 200
        self.headers = headers or {'Content-Type': 'image/png'}
    def raise_for_status(self):
        pass

def test_no_asset(monkeypatch):
    html = "<html><head></head><body>No icons here</body></html>"
    monkeypatch.setattr(httpx, 'get', lambda url, timeout: DummyHTMLResponse(html))
    result = AssetsNode("http://example.com")
    assert result['logo_url'] is None
    assert result['palette'] == []

def test_og_image(monkeypatch):
    html = '<html><head><meta property="og:image" content="/logo.png"></head></html>'
    def mock_get(url, timeout):
        if url == "http://example.com":
            return DummyHTMLResponse(html)
        elif url == "http://example.com/logo.png":
            return DummyImageResponse(b'dummy_png', {'Content-Type': 'image/png'})
        raise RuntimeError("Unexpected URL: " + url)
    monkeypatch.setattr(httpx, 'get', mock_get)
    # Stub ColorThief to return a known palette
    class DummyCT:
        def __init__(self, file):
            pass
        def get_palette(self, color_count=5):
            return [(10, 20, 30), (40, 50, 60)]
    monkeypatch.setattr('api.nodes.assets_node.ColorThief', DummyCT)
    result = AssetsNode("http://example.com")
    assert result['logo_url'] == "http://example.com/logo.png"
    assert result['palette'] == ['#0A141E', '#28323C']

def test_svg_conversion(monkeypatch):
    html = '<html><head><link rel="icon" href="/icon.svg"></head></html>'
    def mock_get(url, timeout):
        if url == "http://example.com":
            return DummyHTMLResponse(html)
        elif url == "http://example.com/icon.svg":
            return DummyImageResponse(b'<svg></svg>', {'Content-Type': 'image/svg+xml'})
        raise RuntimeError("Unexpected URL: " + url)
    monkeypatch.setattr(httpx, 'get', mock_get)
    # Stub cairosvg.svg2png
    fake_cairo = types.SimpleNamespace(svg2png=lambda bytestring: b'converted_png')
    monkeypatch.setattr('api.nodes.assets_node.cairosvg', fake_cairo)
    # Stub ColorThief
    class DummyCT2:
        def __init__(self, file): pass
        def get_palette(self, color_count=5): return [(1, 2, 3)]
    monkeypatch.setattr('api.nodes.assets_node.ColorThief', DummyCT2)
    result = AssetsNode("http://example.com")
    assert result['logo_url'] == "http://example.com/icon.svg"
    assert result['palette'] == ['#010203']