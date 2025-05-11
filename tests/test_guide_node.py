import json
import pytest

import api.nodes.guide_node as gn
from api.nodes.guide_node import GuideNode
import types

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
    prompts = ["Prompt A", "Prompt B"]
    tips = ["Use A with low temperature.", "Use B for exploration."]
    resp_content = json.dumps(tips)
    class DummyClient:
        def __init__(self):
            self.chat = types.SimpleNamespace(
                completions=types.SimpleNamespace(
                    create=lambda model, messages, temperature: DummyResponse(resp_content)
                )
            )
    monkeypatch.setattr(gn.openai, 'OpenAI', lambda *args, **kwargs: DummyClient())
    result = GuideNode(prompts)
    assert result == tips

def test_invalid_json(monkeypatch):
    class DummyClient2:
        def __init__(self):
            self.chat = types.SimpleNamespace(
                completions=types.SimpleNamespace(
                    create=lambda model, messages, temperature: DummyResponse("not json")
                )
            )
    monkeypatch.setattr(gn.openai, 'OpenAI', lambda *args, **kwargs: DummyClient2())
    with pytest.raises(json.JSONDecodeError):
        GuideNode(["Prompt A"])

def test_invalid_length(monkeypatch):
    prompts = ["A", "B"]
    resp_content = json.dumps(["only one tip"])
    class DummyClient3:
        def __init__(self):
            self.chat = types.SimpleNamespace(
                completions=types.SimpleNamespace(
                    create=lambda model, messages, temperature: DummyResponse(resp_content)
                )
            )
    monkeypatch.setattr(gn.openai, 'OpenAI', lambda *args, **kwargs: DummyClient3())
    with pytest.raises(ValueError):
        GuideNode(prompts)

def test_empty_tip(monkeypatch):
    prompts = ["A"]
    resp_content = json.dumps([""])
    class DummyClient4:
        def __init__(self):
            self.chat = types.SimpleNamespace(
                completions=types.SimpleNamespace(
                    create=lambda model, messages, temperature: DummyResponse(resp_content)
                )
            )
    monkeypatch.setattr(gn.openai, 'OpenAI', lambda *args, **kwargs: DummyClient4())
    with pytest.raises(ValueError):
        GuideNode(prompts)

def test_retry(monkeypatch):
    calls = {'n': 0}
    class DummyClient5:
        def __init__(self):
            def create(model, messages, temperature):
                calls['n'] += 1
                raise RuntimeError("fail")
            self.chat = types.SimpleNamespace(
                completions=types.SimpleNamespace(
                    create=create
                )
            )
    monkeypatch.setattr(gn.openai, 'OpenAI', lambda *args, **kwargs: DummyClient5())
    with pytest.raises(RuntimeError):
        GuideNode(["A"])
    assert calls['n'] == 3