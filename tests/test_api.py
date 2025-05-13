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
    # Stub legacy nodes (not used after profile-based rewrite)
    monkeypatch.setattr('api.main.FetchSummaryNode', lambda url: "dummy text")
    monkeypatch.setattr('api.main.SummariseNode', lambda text: "summary prompt")
    # Stub the new one-shot profile node and prompt drafting
    profile_stub = {
        "name": "Test", "sector": "S", "services": ["A"],
        "geo": "G", "value_props": ["V1", "V2"],
        "brand_tone": "friendly", "keywords": ["k1", "k2"]
    }
    monkeypatch.setattr('api.main.PageLLMProfileNode', lambda url: profile_stub)
    monkeypatch.setattr('api.main.PromptDraftNode', lambda text, framework_plan: [['P1', 'P2']])
    monkeypatch.setattr('api.main.AssetsNode', lambda url: {"logo_url": "http://logo", "palette": ["#AAA"]})
    # Stub downstream nodes for full pipeline including PDF builder
    # (PromptsNode is no longer used by /generate)
    monkeypatch.setattr('api.main.RankNode', lambda groups: ['P1'])
    monkeypatch.setattr('api.main.GuideNode', lambda bests: ['Tip1'])
    monkeypatch.setattr('api.main.PdfBuilderNode', lambda logo_url, palette, prompts, tips: b"%PDF-1.4fakepdf")
    res = client.post("/generate", json={"url": "http://example.com"})
    assert res.status_code == 200
    # Expect PDF stream
    assert res.headers.get('content-type') == 'application/pdf'
    assert 'attachment' in res.headers.get('content-disposition', '')
    assert res.content.startswith(b"%PDF-1.4fakepdf")

def test_generate_node_error(monkeypatch):
    # Simulate error in profile generation
    monkeypatch.setattr('api.main.PageLLMProfileNode', lambda url: (_ for _ in ()).throw(RuntimeError("fail")))
    res = client.post("/generate", json={"url": "http://example.com"})
    assert res.status_code == 500
    assert "fail" in res.json().get('detail', '')