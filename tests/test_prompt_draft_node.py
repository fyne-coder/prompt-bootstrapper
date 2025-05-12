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
    # Prepare 16 prompts
    prompts = [f"Do action {i}" for i in range(16)]
    content = json.dumps(prompts)
    class DummyClient:
        def __init__(self):
            self.chat = types.SimpleNamespace(
                completions=types.SimpleNamespace(
                    create=lambda *args, **kwargs: DummyResponse(content)
                )
            )
    import openai
    monkeypatch.setattr(openai, 'OpenAI', lambda *args, **kwargs: DummyClient())
    result = PromptDraftNode("text", {'Marketing':3})
    assert result == prompts

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
    # Too few prompts (fewer than 10)
    content = json.dumps(["One prompt"] * 9)
    class DummyClient3:
        def __init__(self):
            self.chat = types.SimpleNamespace(
                completions=types.SimpleNamespace(create=lambda *args, **kwargs: DummyResponse(content))
            )
    import openai
    monkeypatch.setattr(openai, 'OpenAI', lambda *args, **kwargs: DummyClient3())
    with pytest.raises(ValueError):
        PromptDraftNode("text", {})

def test_invalid_length_long(monkeypatch):
    # Too many prompts
    content = json.dumps([f"P{i}" for i in range(30)])
    class DummyClient4:
        def __init__(self):
            self.chat = types.SimpleNamespace(
                completions=types.SimpleNamespace(create=lambda *args, **kwargs: DummyResponse(content))
            )
    import openai
    monkeypatch.setattr(openai, 'OpenAI', lambda *args, **kwargs: DummyClient4())
    with pytest.raises(ValueError):
        PromptDraftNode("text", {})

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