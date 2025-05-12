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
    # Stub httpx.Client context to return dummy HTML via .get()
    dummy = DummyResponse('<html>ok</html>')
    import httpx
    class DummyClient:
        def __init__(self, **kwargs): pass
        def __enter__(self): return self
        def __exit__(self, exc_type, exc, tb): return False
        def get(self, url): return dummy
    monkeypatch.setattr(httpx, 'Client', lambda **kwargs: DummyClient())
    result = LocalFetchNode('http://example.com')
    assert '<html>ok</html>' == result

def test_local_fetch_error(monkeypatch):
    # Stub httpx.Client to return dummy with HTTP error
    dummy = DummyResponse('error', status=500)
    import httpx
    class DummyClientErr:
        def __init__(self, **kwargs): pass
        def __enter__(self): return self
        def __exit__(self, exc_type, exc, tb): return False
        def get(self, url): return dummy
    monkeypatch.setattr(httpx, 'Client', lambda **kwargs: DummyClientErr())
    with pytest.raises(Exception):
        LocalFetchNode('http://example.com')