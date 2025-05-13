import json
import types
import pytest

import api.nodes.new_pipeline.prompt_draft_node as pdn
from api.nodes.new_pipeline.prompt_draft_node import PromptDraftNode

class DummyChoice:
    def __init__(self, content):
        class Msg:
            def __init__(self, txt):
                self.content = txt
        self.message = Msg(content)

class DummyResponse:
    def __init__(self, content):
        self.choices = [DummyChoice(content)]

def test_success(monkeypatch):
    # Prepare 16 prompts under 'Marketing' category
    prompts = [f"Do action {i}" for i in range(16)]
    content = json.dumps({"Marketing": prompts})
    class DummyClient:
        def __init__(self):
            self.chat = types.SimpleNamespace(
                completions=types.SimpleNamespace(
                    create=lambda *args, **kwargs: DummyResponse(content)
                )
            )
    import openai
    monkeypatch.setattr(openai, 'OpenAI', lambda *args, **kwargs: DummyClient())
    # Stub returns grouped JSON with 'Marketing' category
    # Monkey plan only needs Marketing quota
    result = PromptDraftNode("text", {'Marketing':3})
    assert isinstance(result, dict)
    # Ensure the 'Marketing' category has our 16 prompts
    assert result == {"Marketing": prompts}

def test_invalid_json(monkeypatch):
    class DummyClient2:
        def __init__(self):
            self.chat = types.SimpleNamespace(
                completions=types.SimpleNamespace(
                    create=lambda *args, **kwargs: DummyResponse("not json")
                )
            )
    import openai
    monkeypatch.setattr(openai, 'OpenAI', lambda *args, **kwargs: DummyClient2())
    with pytest.raises(json.JSONDecodeError):
        PromptDraftNode("text", {})

def test_invalid_length_short(monkeypatch):
    # Too few prompts (fewer than 10), now allow fewer
    content = json.dumps({"Marketing": ["One prompt"] * 9})
    class DummyClient3:
        def __init__(self):
            self.chat = types.SimpleNamespace(
                completions=types.SimpleNamespace(create=lambda *args, **kwargs: DummyResponse(content))
            )
    import openai
    monkeypatch.setattr(openai, 'OpenAI', lambda *args, **kwargs: DummyClient3())
    # Now allows fewer prompts; returns dict with one category empty
    result = PromptDraftNode("text", {'Marketing':3})
    assert isinstance(result, dict)
    # Marketing has 9 prompts
    assert result.get('Marketing') == ["One prompt"] * 9

def test_invalid_length_long(monkeypatch):
    # Too many prompts (more than 25), now allow many
    content = json.dumps({"Marketing": [f"P{i}" for i in range(30)]})
    class DummyClient4:
        def __init__(self):
            self.chat = types.SimpleNamespace(
                completions=types.SimpleNamespace(create=lambda *args, **kwargs: DummyResponse(content))
            )
    import openai
    monkeypatch.setattr(openai, 'OpenAI', lambda *args, **kwargs: DummyClient4())
    # Now allows many prompts; returns dict with 'Marketing' key
    result = PromptDraftNode("text", {'Marketing':3})
    assert isinstance(result, dict)
    # Marketing has 30 prompts, excess will be handled later
    assert result.get('Marketing') == [f"P{i}" for i in range(30)]

def test_invalid_item(monkeypatch):
    # Non-string entry
    content = json.dumps(["Valid prompt"] * 15 + [123])
    class DummyClient5:
        def __init__(self):
            self.chat = types.SimpleNamespace(
                completions=types.SimpleNamespace(create=lambda *args, **kwargs: DummyResponse(content))
            )
    import openai
    monkeypatch.setattr(openai, 'OpenAI', lambda *args, **kwargs: DummyClient5())
    with pytest.raises(ValueError):
        PromptDraftNode("text", {})