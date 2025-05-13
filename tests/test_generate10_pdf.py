import io
import types
import pytest

from fastapi.testclient import TestClient
import api.main as main
from api.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def stub_pdf_builder(monkeypatch):
    # Stub PdfBuilderNode (signature: logo_url, palette, prompts_by_cat)
    monkeypatch.setattr(main, 'PdfBuilderNode', lambda logo, palette, prompts: b"%PDF-FOO")

def test_generate10_pdf_success():
    # Use a simple dict with one category for testing
    payload = {
        'prompts': {'Test': [f'P{i}' for i in range(3)]},
        'logo_url': None,
        'palette': []
    }
    response = client.post('/generate10/pdf', json=payload)
    assert response.status_code == 200
    assert response.content.startswith(b"%PDF-FOO")

def test_generate10_pdf_invalid_payload():
    # tips length mismatch
    # prompts must be a dict, not a list
    payload = {
        'prompts': ['P0', 'P1'],
    }
    response = client.post('/generate10/pdf', json=payload)
    assert response.status_code == 400

def test_generate10_pdf_builder_error(monkeypatch):
    # Stub PdfBuilderNode to throw
    def bad_builder(logo, palette, prompts):
        raise RuntimeError('pdf fail')
    monkeypatch.setattr(main, 'PdfBuilderNode', bad_builder)
    payload = {
        'prompts': {'Test': ['P0']},
    }
    response = client.post('/generate10/pdf', json=payload)
    assert response.status_code == 500
    assert 'pdf fail' in response.json().get('detail', '')