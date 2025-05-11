import json
import pytest

import api.nodes.rank_node as rn
from api.nodes.rank_node import RankNode
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
    groups = [["a1","a2"], ["b1","b2"]]
    # prepare a JSON array of bests
    bests = ["a2","b1"]
    resp_content = json.dumps(bests)
    class DummyClient:
        def __init__(self):
            self.chat = types.SimpleNamespace(
                completions=types.SimpleNamespace(
                    create=lambda model, messages, temperature: DummyResponse(resp_content)
                )
            )
    monkeypatch.setattr(rn.openai, 'OpenAI', lambda *args, **kwargs: DummyClient())
    result = RankNode(groups)
    assert result == bests

def test_invalid_json(monkeypatch):
    class DummyClient2:
        def __init__(self):
            self.chat = types.SimpleNamespace(
                completions=types.SimpleNamespace(
                    create=lambda model, messages, temperature: DummyResponse("invalid json")
                )
            )
    monkeypatch.setattr(rn.openai, 'OpenAI', lambda *args, **kwargs: DummyClient2())
    with pytest.raises(json.JSONDecodeError):
        RankNode([["x"]])

def test_invalid_length(monkeypatch):
    groups = [["x"],["y"]]
    # return wrong length array
    resp_content = json.dumps(["onlyone"])
    class DummyClient3:
        def __init__(self):
            self.chat = types.SimpleNamespace(
                completions=types.SimpleNamespace(
                    create=lambda model, messages, temperature: DummyResponse(resp_content)
                )
            )
    monkeypatch.setattr(rn.openai, 'OpenAI', lambda *args, **kwargs: DummyClient3())
    with pytest.raises(ValueError):
        RankNode(groups)

def test_invalid_item(monkeypatch):
    groups = [["x"]]
    # return correct length but non-string
    resp_content = json.dumps([1])
    class DummyClient4:
        def __init__(self):
            self.chat = types.SimpleNamespace(
                completions=types.SimpleNamespace(
                    create=lambda model, messages, temperature: DummyResponse(resp_content)
                )
            )
    monkeypatch.setattr(rn.openai, 'OpenAI', lambda *args, **kwargs: DummyClient4())
    with pytest.raises(ValueError):
        RankNode(groups)

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
    monkeypatch.setattr(rn.openai, 'OpenAI', lambda *args, **kwargs: DummyClient5())
    with pytest.raises(RuntimeError):
        RankNode([["x"]])
    assert calls['n'] == 3