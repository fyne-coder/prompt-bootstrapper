import json
import types
import pytest

import api.nodes.new_pipeline.explanation_node as exn
from api.nodes.new_pipeline.explanation_node import ExplanationNode

class DummyChoice:
    def __init__(self, content):
        class Msg:
            def __init__(self, txt):
                self.content = txt
        self.message = Msg(content)

class DummyResponse:
    def __init__(self, content):
        self.choices = [DummyChoice(content)]

def test_explanation_success(monkeypatch):
    prompts = ["Prompt A", "Prompt B"]
    tips = ["Use A when ...", "Use B for ..."]
    resp_content = json.dumps(tips)
    class DummyClient:
        def __init__(self):
            self.chat = types.SimpleNamespace(
                completions=types.SimpleNamespace(
                    create=lambda model, messages, temperature: DummyResponse(resp_content)
                )
            )
    import openai
    monkeypatch.setattr(openai, 'OpenAI', lambda *args, **kwargs: DummyClient())
    result = ExplanationNode(prompts)
    assert result == tips

def test_explanation_invalid_json(monkeypatch):
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
        ExplanationNode(["Prompt A"])

def test_explanation_invalid_length(monkeypatch):
    prompts = ["A", "B"]
    resp_content = json.dumps(["only one tip"])
    class DummyClient3:
        def __init__(self):
            self.chat = types.SimpleNamespace(
                completions=types.SimpleNamespace(
                    create=lambda *args, **kwargs: DummyResponse(resp_content)
                )
            )
    import openai
    monkeypatch.setattr(openai, 'OpenAI', lambda *args, **kwargs: DummyClient3())
    with pytest.raises(ValueError):
        ExplanationNode(prompts)

def test_explanation_empty_tip(monkeypatch):
    prompts = ["A"]
    resp_content = json.dumps([""])
    class DummyClient4:
        def __init__(self):
            self.chat = types.SimpleNamespace(
                completions=types.SimpleNamespace(
                    create=lambda *args, **kwargs: DummyResponse(resp_content)
                )
            )
    import openai
    monkeypatch.setattr(openai, 'OpenAI', lambda *args, **kwargs: DummyClient4())
    with pytest.raises(ValueError):
        ExplanationNode(prompts)