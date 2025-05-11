import pytest
import httpx

from api.nodes.fetch_summary_node import FetchSummaryNode

def test_success(monkeypatch):
    html = "<html><body><p>Hello</p> <p>World</p></body></html>"
    class DummyResponse:
        def __init__(self, text, status_code=200):
            self.text = text
            self.status_code = status_code
        def raise_for_status(self):
            if not (200 <= self.status_code < 300):
                raise httpx.HTTPStatusError("HTTP error", request=None, response=self)
    def mock_get(url, timeout):
        return DummyResponse(html)
    monkeypatch.setattr(httpx, "get", mock_get)
    result = FetchSummaryNode("http://example.com")
    assert result == "Hello World"

def test_truncate(monkeypatch):
    long_text = "a" * 4100
    html = f"<html><body><p>{long_text}</p></body></html>"
    class DummyResponse:
        def __init__(self, text):
            self.text = text
            self.status_code = 200
        def raise_for_status(self):
            return None
    monkeypatch.setattr(httpx, "get", lambda url, timeout: DummyResponse(html))
    result = FetchSummaryNode("http://example.com")
    assert len(result) == 4000
    assert result == long_text[:4000]

def test_retry(monkeypatch):
    calls = {"count": 0}
    def mock_get(url, timeout):
        calls["count"] += 1
        raise httpx.ConnectError("Network failure")
    monkeypatch.setattr(httpx, "get", mock_get)
    with pytest.raises(httpx.ConnectError):
        FetchSummaryNode("http://example.com")
    assert calls["count"] == 3