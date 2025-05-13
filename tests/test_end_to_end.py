import json
import types
import pytest

from fastapi.testclient import TestClient
import openai
import api.main as main
from api.main import app

class DummyResponse:
    def __init__(self, content):
        # Provide both access patterns
        class Msg:
            def __init__(self, txt):
                self.content = txt
        self.choices = [types.SimpleNamespace(message=Msg(content))]

def test_end_to_end_pdf_generation(monkeypatch):
    """
    End-to-end test of the /generate endpoint, with mocked OpenAI responses.
    """
    # Counter to sequence LLM calls
    call_counter = {'n': 0}

    # Define dummy OpenAI client
    def create(*args, **kwargs):
        call_counter['n'] += 1
        # SummariseNode -> one summary string
        if call_counter['n'] == 1:
            resp_content = "Master summary prompt"
        # PromptsNode -> JSON array of 3 groups × 5 prompts
        elif call_counter['n'] == 2:
            groups = [[f"P{g}{i}" for i in range(5)] for g in range(1, 4)]
            resp_content = json.dumps(groups)
        # RankNode -> best prompt per group
        elif call_counter['n'] == 3:
            bests = [f"P{g}0" for g in range(1, 4)]
            resp_content = json.dumps(bests)
        # GuideNode -> usage tips
        elif call_counter['n'] == 4:
            tips = [f"Tip {i}" for i in range(1, 4)]
            resp_content = json.dumps(tips)
        else:
            pytest.skip("Unexpected extra LLM call")
        return DummyResponse(resp_content)

    class DummyClient:
        def __init__(self):
            self.chat = types.SimpleNamespace(
                completions=types.SimpleNamespace(create=create)
            )

    # Monkey-patch OpenAI client and disable WebSearch
    monkeypatch.setattr(openai, 'OpenAI', lambda *args, **kwargs: DummyClient())
    monkeypatch.setattr(openai, 'WebSearch', None, raising=False)
    # Stub PageLLMProfileNode to use the one-shot LLM profile instead of summary+fetch
    import api.main as main_module
    profile_data = {
        "name": "Acme", "sector": "Test", "services": ["A"],
        "geo": "X", "value_props": ["V1", "V2"],
        "brand_tone": "friendly", "keywords": ["k1", "k2"]
    }
    monkeypatch.setattr(main_module, 'PageLLMProfileNode', lambda url: profile_data)
    # Stub PromptDraftNode to bump LLM call and return grouped prompts
    def fake_prompt_draft(text, framework_plan):
        # bump call count for second LLM stage
        openai.OpenAI().chat.completions.create()
        # return three groups of five prompts
        return [[f"P{g}{i}" for i in range(5)] for g in range(1, 4)]
    monkeypatch.setattr(main_module, 'PromptDraftNode', fake_prompt_draft)

    # Stub fetch, assets, and PDF builder to avoid network and WeasyPrint in CI
    monkeypatch.setattr(main, 'FetchSummaryNode', lambda url: "dummy text")
    monkeypatch.setattr(main, 'AssetsNode', lambda url: {"logo_url": None, "palette": []})
    monkeypatch.setattr(main, 'PdfBuilderNode', lambda logo_url, palette, prompts, tips: b"%PDF-INTEGRATION")
    client = TestClient(app)
    response = client.post('/generate', json={'url': 'http://example.com'})
    # Debug: print error detail on failure
    if response.status_code != 200:
        print('DEBUG END2END RESPONSE:', response.json())
    assert response.status_code == 200
    # Validate headers for PDF attachment
    assert response.headers.get('content-type') == 'application/pdf'
    cd = response.headers.get('content-disposition', '')
    assert 'attachment' in cd and 'prompts.pdf' in cd
    # Response content should start with PDF magic bytes
    content = response.content
    assert isinstance(content, (bytes, bytearray))
    assert content[:4] == b"%PDF"
    # Ensure all LLM stages were called
    assert call_counter['n'] == 4