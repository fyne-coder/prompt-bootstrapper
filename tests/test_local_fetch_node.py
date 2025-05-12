import pytest

from api.nodes.new_pipeline.local_fetch_node import LocalFetchNode

class DummyResponse:
    def __init__(self, text, status=200):
        self.text = text
        self.status_code = status
        self.headers = {}
    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f'Status {self.status_code}')

def test_local_fetch_success(monkeypatch):
    # Stub httpx.get to return dummy HTML
    # Stub httpx.get globally to return dummy HTML
    dummy = DummyResponse('<html>ok</html>')
    import httpx
    monkeypatch.setattr(httpx, 'get', lambda url, timeout: dummy)
    result = LocalFetchNode('http://example.com')
    assert '<html>ok</html>' == result

def test_local_fetch_error(monkeypatch):
    # Stub httpx.get globally to return error status
    dummy = DummyResponse('error', status=500)
    import httpx
    monkeypatch.setattr(httpx, 'get', lambda url, timeout: dummy)
    with pytest.raises(Exception):
        LocalFetchNode('http://example.com')