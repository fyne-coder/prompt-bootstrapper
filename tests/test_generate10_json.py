import json
import types

import pytest
from fastapi.testclient import TestClient

import api.main as main
from api.main import app

client = TestClient(app)

class DummyClientNode:
    def __init__(self, return_value):
        self.return_value = return_value
    def __call__(self, *args, **kwargs):
        return self.return_value

@pytest.fixture(autouse=True)
def stub_pipeline(monkeypatch):
    # Stub all pipeline nodes; ensure fetched HTML meets length requirement (>500 chars)
    long_html = 'x' * 600
    monkeypatch.setattr(main, 'WebFetchNode', lambda url: long_html)
    monkeypatch.setattr(main, 'LocalFetchNode', lambda url: long_html)
    monkeypatch.setattr(main, 'CleanNode', lambda html: 'clean text')
    monkeypatch.setattr(main, 'KeyphraseNode', lambda text: ['kp1', 'kp2'])
    monkeypatch.setattr(main, 'FrameworkSelectNode', lambda kps: {'Marketing':3,'Sales':2,'Success':2,'Product':2,'Ops':1})
    dummy_prompts = [f'P{i}' for i in range(10)]
    # Return grouped dict from PromptDraftNode
    monkeypatch.setattr(main, 'PromptDraftNode', lambda text, plan: {'Test': dummy_prompts})
    # Pass through grouped dict
    monkeypatch.setattr(main, 'DeduplicateNode', lambda d: d)
    monkeypatch.setattr(main, 'BusinessAnchorGuard', lambda d, kps: d)
    monkeypatch.setattr(main, 'QuotaEnforceNode', lambda d, plan: d)
    # ExplanationNode is no longer used; no tips to stub
    monkeypatch.setattr(main, 'AssetsNode', lambda url: {'logo_url':'http://logo','palette':['#AAA']})

def test_generate10_json_success():
    res = client.post('/generate10/json', json={'url':'http://example.com'})
    assert res.status_code == 200
    data = res.json()
    assert 'prompts' in data and isinstance(data['prompts'], dict)
    # ensure total prompts count is 10 across all categories
    total = sum(len(v) for v in data['prompts'].values())
    assert total == 10
    assert data['logo_url'] == 'http://logo'
    assert data['palette'] == ['#AAA']

def test_generate10_json_missing_url():
    res = client.post('/generate10/json', json={})
    assert res.status_code == 400

def test_generate10_json_insufficient_prompts(monkeypatch):
    # PromptDraftNode returns fewer than 10; use real QuotaEnforceNode to trigger ValueError
    # PromptDraftNode returns only one under 'Test' category
    monkeypatch.setattr(main, 'PromptDraftNode', lambda text, plan: {'Test': ['only one']})
    # All pipeline steps pass through, but total <10; should still succeed
    res = client.post('/generate10/json', json={'url':'http://example.com'})
    assert res.status_code == 200
    data = res.json()
    total = sum(len(v) for v in data['prompts'].values())
    assert total == 1

def test_generate10_json_server_error(monkeypatch):
    # CleanNode raises unexpected error
    monkeypatch.setattr(main, 'CleanNode', lambda html: (_ for _ in ()).throw(RuntimeError('oops')))
    res = client.post('/generate10/json', json={'url':'http://example.com'})
    assert res.status_code == 500
    assert 'oops' in res.json().get('detail', '')
    
def test_generate10_json_with_text_fallback():
    # Test supplying raw text instead of URL
    response = client.post('/generate10/json', json={'text':'Fallback content'})
    assert response.status_code == 200
    data = response.json()
    # Total prompts across all categories should be 10
    total = sum(len(v) for v in data['prompts'].values())
    assert total == 10
    
def test_generate10_json_html_too_short(monkeypatch):
    # Simulate both WebFetch and LocalFetch returning too-short HTML
    monkeypatch.setattr(main, 'WebFetchNode', lambda url: '')
    monkeypatch.setattr(main, 'LocalFetchNode', lambda url: '<p>tiny</p>')
    res = client.post('/generate10/json', json={'url':'http://example.com'})
    assert res.status_code == 422
    assert 'Fetched content too short' in res.json().get('detail', '')