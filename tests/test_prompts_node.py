import json
import pytest

import api.nodes.prompts_node as pn
from api.nodes.prompts_node import PromptsNode

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
    def fake_create(model, messages, temperature):
        return DummyResponse(content)
    monkeypatch.setattr(pn.openai.ChatCompletion, 'create', fake_create)
    result = PromptsNode("master", ["#FFF"])
    assert result == groups

def test_invalid_json(monkeypatch):
    def fake_create(model, messages, temperature):
        return DummyResponse("not a json")
    monkeypatch.setattr(pn.openai.ChatCompletion, 'create', fake_create)
    with pytest.raises(json.JSONDecodeError):
        PromptsNode("master", ["#FFF"])

def test_invalid_structure(monkeypatch):
    # JSON but not list of lists
    def fake_create(model, messages, temperature):
        return DummyResponse(json.dumps({"a": 1}))
    monkeypatch.setattr(pn.openai.ChatCompletion, 'create', fake_create)
    with pytest.raises(ValueError):
        PromptsNode("master", ["#FFF"])

def test_retry(monkeypatch):
    calls = {'n': 0}
    def fake_create(model, messages, temperature):
        calls['n'] += 1
        raise RuntimeError("api error")
    monkeypatch.setattr(pn.openai.ChatCompletion, 'create', fake_create)
    with pytest.raises(RuntimeError):
        PromptsNode("master", ["#FFF"])
    # should have retried 3 times
    assert calls['n'] == 3