import pytest
try:
    from fastapi.testclient import TestClient
    from api.main import app
except ImportError:
    pytest.skip("fastapi or dependencies not installed; skipping API tests", allow_module_level=True)

client = TestClient(app)

def test_healthz():
    res = client.get("/healthz")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}

def test_generate_missing_url():
    res = client.post("/generate", json={})
    assert res.status_code == 400
    assert "Missing 'url'" in res.json().get('detail', '')

def test_generate_success(monkeypatch):
    # Stub nodes to return predictable results
    monkeypatch.setattr('api.main.FetchSummaryNode', lambda url: "dummy text")
    monkeypatch.setattr('api.main.SummariseNode', lambda text: "summary prompt")
    monkeypatch.setattr('api.main.AssetsNode', lambda url: {"logo_url": "http://logo", "palette": ["#AAA"]})
    res = client.post("/generate", json={"url": "http://example.com"})
    assert res.status_code == 200
    assert res.json() == {"master_prompt": "summary prompt", "logo_url": "http://logo", "palette": ["#AAA"]}

def test_generate_node_error(monkeypatch):
    monkeypatch.setattr('api.main.FetchSummaryNode', lambda url: (_ for _ in ()).throw(RuntimeError("fail")))
    res = client.post("/generate", json={"url": "http://example.com"})
    assert res.status_code == 500
    assert "fail" in res.json().get('detail', '')