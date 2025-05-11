import json
import pytest

import api.nodes.prompts_node as pn
from api.nodes.prompts_node import PromptsNode
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
    # Create 3 groups of 5 prompts
    groups = [[f"p{i}{j}" for j in range(5)] for i in range(3)]
    content = json.dumps(groups)
    # stub OpenAI client
    class DummyClient:
        def __init__(self):
            self.chat = types.SimpleNamespace(
                completions=types.SimpleNamespace(
                    create=lambda model, messages, temperature: DummyResponse(content)
                )
            )
    monkeypatch.setattr(pn.openai, 'OpenAI', lambda *args, **kwargs: DummyClient())
    result = PromptsNode("master", ["#FFF"])
    assert result == groups

def test_invalid_json(monkeypatch):
    # stub client returning invalid JSON
    class DummyClient2:
        def __init__(self):
            self.chat = types.SimpleNamespace(
                completions=types.SimpleNamespace(
                    create=lambda model, messages, temperature: DummyResponse("not a json")
                )
            )
    monkeypatch.setattr(pn.openai, 'OpenAI', lambda *args, **kwargs: DummyClient2())
    with pytest.raises(json.JSONDecodeError):
        PromptsNode("master", ["#FFF"])

def test_invalid_structure(monkeypatch):
    # JSON but not list of lists
    # stub client returning wrong structure
    class DummyClient3:
        def __init__(self):
            self.chat = types.SimpleNamespace(
                completions=types.SimpleNamespace(
                    create=lambda model, messages, temperature: DummyResponse(json.dumps({"a": 1}))
                )
            )
    monkeypatch.setattr(pn.openai, 'OpenAI', lambda *args, **kwargs: DummyClient3())
    with pytest.raises(ValueError):
        PromptsNode("master", ["#FFF"])

def test_retry(monkeypatch):
    # stub client to always fail
    class DummyClient4:
        def __init__(self):
            self.chat = types.SimpleNamespace(
                completions=types.SimpleNamespace(
                    create=lambda model, messages, temperature: (_ for _ in ()).throw(RuntimeError("api error"))
                )
            )
    monkeypatch.setattr(pn.openai, 'OpenAI', lambda *args, **kwargs: DummyClient4())
    with pytest.raises(RuntimeError):
        PromptsNode("master", ["#FFF"])