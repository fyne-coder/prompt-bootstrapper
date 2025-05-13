import io
import types
import pytest

from fastapi.testclient import TestClient
import api.main as main
from api.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def stub_pdf_builder(monkeypatch):
    # Stub PdfBuilderNode
    monkeypatch.setattr(main, 'PdfBuilderNode', lambda logo, palette, prompts, tips: b"%PDF-FOO")

def test_generate10_pdf_success():
    payload = {
        'prompts': [f'P{i}' for i in range(3)],
        'tips': ['T0', 'T1', 'T2'],
        'logo_url': None,
        'palette': []
    }
    # length mismatch we purposely test 3=3 is fine
    response = client.post('/generate10/pdf', json=payload)
    assert response.status_code == 200
    assert response.content.startswith(b"%PDF-FOO")

def test_generate10_pdf_invalid_payload():
    # tips length mismatch
    payload = {
        'prompts': ['P0', 'P1'],
        'tips': ['T0'],
    }
    response = client.post('/generate10/pdf', json=payload)
    assert response.status_code == 400

def test_generate10_pdf_builder_error(monkeypatch):
    def bad_builder(logo, palette, prompts, tips):
        raise RuntimeError('pdf fail')
    monkeypatch.setattr(main, 'PdfBuilderNode', bad_builder)
    payload = {
        'prompts': ['P0'],
        'tips': ['T0'],
    }
    response = client.post('/generate10/pdf', json=payload)
    assert response.status_code == 500
    assert 'pdf fail' in response.json().get('detail', '')